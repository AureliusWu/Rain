"""Decode complete WAV/OGG files and measure signals, without a TTS runtime."""
import math
import numpy as np
import soundfile as sf


def audio_metadata(path):
    with sf.SoundFile(path) as audio:
        samples = audio.read(dtype='float64', always_2d=True)
        if not len(samples) or len(samples) != audio.frames:
            raise ValueError('Empty or incomplete audio stream')
        if not np.isfinite(samples).all():
            raise ValueError('Non-finite audio samples')
        peak = float(np.max(np.abs(samples)))
        rms = float(np.sqrt(np.mean(samples * samples)))
        if rms < 1e-7:
            raise ValueError('Silent audio stream')
        return {
            'format': audio.format, 'subtype': audio.subtype,
            'sample_rate': audio.samplerate, 'channels': audio.channels,
            'frames': len(samples),
            'duration_seconds': round(len(samples) / audio.samplerate, 6),
            'peak': round(peak, 6), 'rms_dbfs': round(20 * math.log10(rms), 3),
        }


def metadata_matches(actual, recorded):
    if not isinstance(recorded, dict) or set(actual) != set(recorded):
        return False
    for key, value in actual.items():
        if key in {'peak', 'rms_dbfs'}:
            if type(recorded[key]) not in (int, float) or not math.isfinite(recorded[key]) or abs(value - recorded[key]) > .002:
                return False
        elif value != recorded[key]:
            return False
    return True
