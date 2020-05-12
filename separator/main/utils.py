import subprocess
from pathlib import Path

import librosa
import numpy as np
from pydub import AudioSegment

from werkzeug.utils import secure_filename


class AudioMeta:

    def __init__(self, sample_rate, duration, channels,
                 sample_width, ext):
        self.sample_rate = sample_rate
        self.duration = duration
        self.channels = channels
        self.sample_width = sample_width
        self.ext = ext

def save_audio_from_storage(file_storage, dir_name):
    dir_name.mkdir()
    (dir_name / "augmented").mkdir()

    name = dir_name / secure_filename(file_storage.filename)
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
    subprocess.Popen(f"ffmpeg -i {file_path}.wav {file_path}.mp3", shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE).communicate()

def augment_data(augment, signal, json, audio_metadata):
    sample_rate = audio_metadata.sample_rate
    duration = audio_metadata.duration
    stem_names = list(json.keys())

    print(json)
    for audio_name in stem_names:
        augment.clear()
        signal_base_name = audio_name.replace("_augmented", '')

        commands = json.get(audio_name)
        for command_name, command_params in commands.items():
            if command_name == "Volume":
                augment = augment_volume(augment, command_params, sample_rate)
            elif command_name == "Copy":
                augment = augment_copy(augment, command_params, sample_rate)
        augment.augment(signal, signal_base_name)
    return signal

def augment_volume(augment, params, sample_rate):
    for param in params:
        start = float(param.get("start"))
        end = float(param.get("end"))
        volume = int(param.get("volume", 100)) / 100
        if volume == 1:
            continue

        augment = augment.amplitude(interval=(start, end),
                                    gain=volume, sample_rate=sample_rate)
    return augment

def augment_copy(augment, params, sample_rate):
    for param in params:
        start = float(param.get("start"))
        end = float(param.get("end"))
        copy_start = float(param.get("copyStart"))
        augment = augment.copy(interval=(start, end), copy_start=copy_start,
                               sample_rate=sample_rate)
    return augment

def store_combined_signal(signal, session_path, audio_meta):
    signals = []
    for _, s in signal.get_items():
        signals.append(s)
    combined = np.mean(signals, axis=0)
    librosa.output.write_wav(session_path / "combined.wav", np.asfortranarray(combined),
                             sr=audio_meta.sample_rate)

