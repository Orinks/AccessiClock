import pytest


def _validate_wav_header(path):
    with open(path, "rb") as handle:
        header = handle.read(12)
    if len(header) < 12 or header[0:4] != b"RIFF" or header[8:12] != b"WAVE":
        raise ValueError("Invalid WAV header")


class FakeFileStream:
    def __init__(self, file):
        _validate_wav_header(file)
        self.file = file
        self.volume = 1.0
        self._playing = False

    def play(self):
        self._playing = True

    def stop(self):
        self._playing = False

    def free(self):
        return None

    @property
    def is_playing(self):
        return self._playing


class FakeOutput:
    def __init__(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def _mock_sound_lib(monkeypatch):
    from accessibletalkingclock.audio import player as player_module
    import sound_lib

    monkeypatch.setattr(player_module, "_bass_initialized", False)

    try:
        import sound_lib.output
        monkeypatch.setattr(sound_lib.output, "Output", FakeOutput)
    except Exception:
        pass

    monkeypatch.setattr(sound_lib.stream, "FileStream", FakeFileStream)
    monkeypatch.setattr(player_module.stream, "FileStream", FakeFileStream)


@pytest.fixture
def test_sound_path(tmp_path):
    wav_path = tmp_path / "test_sound.wav"
    num_channels = 1
    sample_rate = 8000
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    subchunk2_size = 0
    chunk_size = 36 + subchunk2_size

    header = b"".join(
        [
            b"RIFF",
            chunk_size.to_bytes(4, "little"),
            b"WAVE",
            b"fmt ",
            (16).to_bytes(4, "little"),
            (1).to_bytes(2, "little"),
            num_channels.to_bytes(2, "little"),
            sample_rate.to_bytes(4, "little"),
            byte_rate.to_bytes(4, "little"),
            block_align.to_bytes(2, "little"),
            bits_per_sample.to_bytes(2, "little"),
            b"data",
            subchunk2_size.to_bytes(4, "little"),
        ]
    )
    wav_path.write_bytes(header)
    return wav_path
