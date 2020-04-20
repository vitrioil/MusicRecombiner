import tempfile

import numpy as np
from pydub import AudioSegment

from werkzeug.utils import secure_filename

def save_audio(file_storage):
    with tempfile.NamedTemporaryFile() as f:
        file_storage.save(f.name)
        audio_array = AudioSegment.from_mp3(f.name)

    sample_rate = audio_array.frame_rate
    duration = audio_array.duration_seconds
    channels = audio_array.channels

    audio = np.array(audio_array.get_array_of_samples()).reshape(-1, channels)
    print("Save audio", audio.shape)
    return audio
