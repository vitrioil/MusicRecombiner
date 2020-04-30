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
    librosa.output.write_wav(path.as_posix()+".wav", np.asfortranarray(audio), sr=audio_meta.sample_rate)

def augment_data(augment, signal, json, audio_metadata):
    sample_rate = audio_metadata.sample_rate
    duration = audio_metadata.duration
    stem_names = list(json.keys())

    print(json)
    for name in stem_names:
        augment.clear()
        signal_base_name = name.replace("_augmented", '')

        commands = json.get(name)
        print(name, commands)
        for command in commands:
            if "Volume" in command.keys():
                param = command.get("Volume", {})
                start = float(param.get("start"))
                end = float(param.get("end"))
                volume = int(param.get("volume", 100)) / 100
                if volume == 1:
                    continue
                augment = augment.amplitude(interval=(start, end),
                                            gain=volume, sample_rate=sample_rate)

            elif "Copy" in command.keys():
                param = command.get("Copy")
                start = float(param.get("start"))
                end = float(param.get("end"))
                copy_start = float(param.get("copyStart"))
                augment = augment.copy(interval=(start, end), copy_start=copy_start,
                                       sample_rate=sample_rate)

        augment.augment(signal, signal_base_name)
    return signal
