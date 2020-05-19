import uuid
import subprocess
from pathlib import Path

import librosa
import numpy as np
from pydub import AudioSegment

from werkzeug.utils import secure_filename

#package import
from separator import db
from separator.main import Signal
from separator.main.separate import SpleeterSeparator
from separator.models import (Session, Storage, Music, Command,
                              Volume, Copy, Undo)


class AudioMeta:

    def __init__(self, sample_rate, duration, channels,
                 sample_width, ext):
        self.sample_rate = sample_rate
        self.duration = duration
        self.channels = channels
        self.sample_width = sample_width
        self.ext = ext

def save_audio_from_storage(file_storage, dir_name):
    file_name = secure_filename(file_storage.filename)
    dir_name.mkdir(exist_ok=True)
    file_stem = Path(file_name).stem
    (dir_name / file_stem / "augmented").mkdir(parents=True)
    (dir_name / file_stem / "original").mkdir(parents=True)

    name = dir_name / file_name
    with open(name, 'w+b') as f:
        file_storage.save(f)

    # TODO: multiple extensions
    audio_array = AudioSegment.from_mp3(name)

    sample_rate = audio_array.frame_rate
    duration = audio_array.duration_seconds
    channels = audio_array.channels
    sample_width = audio_array.sample_width

    audio_meta = AudioMeta(sample_rate, duration,
                           channels, sample_width, ".mp3")

    return name, audio_meta

def save_audio(audio, path, audio_meta):
    #audio_segment = AudioSegment(audio.tobytes(), frame_rate=audio_meta.sample_rate,
    #                             sample_width=audio_meta.sample_width,
    #                             channels=audio_meta.channels)
    #audio_segment.export(path.as_posix() + audio_meta.ext, format=audio_meta.ext[1:])
    file_path = path.as_posix()
    librosa.output.write_wav(file_path+".wav", np.asfortranarray(audio), sr=audio_meta.sample_rate)
    #stupid method to convert wav array into mp3
    subprocess.Popen(f"ffmpeg -i {file_path}.wav {file_path}.mp3 -y", shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE).communicate()



def store_combined_signal(signal, session_path, audio_meta):
    signals = []
    for _, s in signal.get_items():
        signals.append(s)
    combined = np.mean(signals, axis=0)
    librosa.output.write_wav(session_path / "combined.wav", np.asfortranarray(combined),
                             sr=audio_meta.sample_rate)

def gen_session(session, parent_dir):
    parent_dir.mkdir(exist_ok=True)

    session_id = uuid.uuid4()
    session["session_id"] = session_id
    session["dir"] = parent_dir / str(session_id)

    session = Session(session_id=session_id)
    db.session.add(session)
    db.session.commit()

def gen_music(session, audio_file, stem):
    music_id = uuid.uuid4()
    audio_path, audio_meta = save_audio_from_storage(audio_file, session["dir"])

    session["audio_path"] = audio_path
    session["audio_meta"] = audio_meta

    music = Music(music_id=music_id, file_path=audio_path.as_posix(),
                  sample_rate=audio_meta.sample_rate, duration=audio_meta.duration,
                  channels=audio_meta.channels, sample_width=audio_meta.sample_width,
                  stem=stem)

    db.session.add(music)
    db.session.commit()

    if session.get("music_id") is None:
        session["music_id"] = []
    session.get("music_id").append(music_id)

def gen_storage(session, session_id, music_id, data, augment, signal):
    storage_id = uuid.uuid4()
    session["storage_id"] = storage_id

    storage = Storage(storage_id=storage_id, session_id=session_id,
                      music_id=music_id)
    db.session.add(storage)

    signal = gen_command(session, data, storage_id, augment, signal)
    db.session.commit()

    file_stem = Path(Music.query.get(music_id).file_path).stem
    _save_all(signal, session, file_stem, augmented=True)
    return signal

def gen_command(session, data, storage_id, augment, signal):
    storage = Storage.query.get(storage_id)
    music_id = storage.music_id

    music = Music.query.get(music_id)

    undo = Undo.query.filter_by(music_id=music_id).all()

    cmd_id = uuid.uuid4()
    command = Command(cmd_id=cmd_id, storage_id=storage_id)
    db.session.add(command)

    signal = store_cmd_attr(data, music, cmd_id, signal, augment, undo)
    return signal

def store_cmd_attr(json, music, cmd_id, signal, augment, undo):
    sample_rate = music.sample_rate
    duration = music.duration
    stem_names = list(json.keys())

    for s in stem_names:
        undo_stem = list(filter(lambda x: x.stem_name==s, undo))
        if len(undo_stem) == 0:
            u = Undo(music_id=music.music_id, total_augmentations=1,
                     current_augmentations=1, stem_name=s)
            db.session.add(u)
            continue
        u = undo_stem[0]
        u.increment_augmentations()

    print(json)
    for audio_name in stem_names:

        commands = json.get(audio_name)
        for command_name, command_params in commands.items():
            if command_name == "Volume":
                augment = store_volume_attr(True, sample_rate, augment,
                                            command_params, cmd_id, audio_name)
            elif command_name == "Copy":
                augment = store_copy_attr(True, sample_rate, augment,
                                          command_params, cmd_id, audio_name)
        augment.augment(signal, audio_name)
    return signal

def store_volume_attr(from_json, sample_rate, augment, *args, **kwargs):
    def _retrieve_from_json(params, cmd_id, audio_name):
        for param in params:
            start = float(param.get("start"))
            end = float(param.get("end"))
            vol = int(param.get("volume", 100)) / 100
            if vol == 1:
                continue
            volume = Volume(vol_id=uuid.uuid4(), cmd_id=cmd_id,
                            start=start, end=end, volume=vol,
                            stem_name=audio_name)
            db.session.add(volume)
            yield start, end, vol

    def _retrieve_from_db(volume_list):
        for volume in volume_list:
            start = volume.start
            end = volume.end
            vol = volume.volume

            yield start, end, vol

    _retrieve = _retrieve_from_json if from_json else _retrieve_from_db
    for start, end, vol in _retrieve(*args, **kwargs):
        augment = augment.amplitude(interval=(start, end), gain=vol,
                                    sample_rate=sample_rate)
    return augment

def store_copy_attr(from_json, sample_rate, augment, *args, **kwargs):
    def _retrieve_from_json(params, cmd_id, audio_name):
        for param in params:
            start = float(param.get("start"))
            end = float(param.get("end"))
            copy_start = float(param.get("copyStart"))

            copy = Copy(copy_id=uuid.uuid4(), cmd_id=cmd_id,
                        start=start, end=end, copy_start=copy_start,
                        stem_name=audio_name)
            db.session.add(copy)
            yield start, end, copy_start

    def _retrieve_from_db(copy_list):
        for copy in copy_list:
            start = copy.start
            end = copy.end
            copy_start = copy.copy_start
            yield start, end, copy_start

    _retrieve = _retrieve_from_json if from_json else _retrieve_from_db
    for start, end, copy_start in _retrieve(*args, **kwargs):
        augment = augment.copy(interval=(start, end), copy_start=copy_start,
                               sample_rate=sample_rate)
    return augment

def _save_all(signal, session, file_stem, augmented=False):
    augment_str = "augmented" if augmented else 'original'
    for name, sig in signal.get_items():
        signal_path = session["dir"] / file_stem / augment_str / name
        save_audio(sig, signal_path, session["audio_meta"])

def load_separator(separator_name: str, *args, **kwargs):

    if separator_name.lower() == "spleeter":
        separator = SpleeterSeparator(*args, **kwargs)

    return separator

def split_or_load_signal(file_path, stem, session_id, session):
    file_path = Path(file_path)
    base_dir = file_path.parent
    file_stem = file_path.stem
    split_files = list((base_dir / file_stem / "original").rglob("*mp3"))
    audio_dir = f"/main/data/{session_id}"
    new_split = True

    print(file_path, file_stem)
    if len(split_files) == stem:
        print("CACHING SPLIT")
        new_split = False
        # no need to split
        return [s.stem for s in split_files], audio_dir, new_split

    #else split and save
    separator = load_separator("spleeter", stem)
    signal = separator.separate(file_path.as_posix())
    _save_all(signal, session, file_stem)
    print("Saved augmentations")
    return signal.get_names(), audio_dir, new_split

def undo_music(music_id, stem_name, session, augment):
    undo = Undo.query.filter_by(music_id=music_id,
                                 stem_name=stem_name).all()
    assert len(undo) == 1, undo
    undo = undo[0]
    undo.undo_augmentation()

    current_augmentations = undo.current_augmentations

    storages = Storage.query.filter_by(music_id=music_id).all()
    commands = [s.command for s in storages]

    #apply command only upto first `current_augmentations`
    #to the original signal, which acts as undo
    commands = commands[:current_augmentations]

    #get original signal
    music = Music.query.get(music_id)
    sr = music.sample_rate
    file_path = Path(music.file_path)
    file_stem = file_path.stem
    signal = Signal.load_from_path(file_path.parent / file_stem / "original",
                                   alt_path=None, sr=sr)

    for current_command in commands:
        print(current_command.all_commands)
        for command_name, command in current_command.all_commands.items():
            print(command_name, str(command))
            if command_name == "Volume":
                augment = store_volume_attr(False, sr, augment,
                                            command)
            elif command_name == "Copy":
                augment = store_copy_attr(False, sr, augment,
                                          command)
    augment.augment(signal, stem_name)
    _save_all(signal, session, file_stem, augmented=True)

    db.session.commit()
