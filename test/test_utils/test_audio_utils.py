"""
@mojuste
Created: 18-08-2016

Test the audio utilities module
"""
import pytest
from rennet.utils import audio_utils as au
from numpy.testing import assert_almost_equal

# pylint: disable=redefined-outer-name
ValidAudioFile = au.AudioMetadata

test_1_wav = ValidAudioFile(
    "./data/test/test1.wav",  # NOTE: Running from the project root
    'wav',
    32000,
    2,
    10.00946875,
    320303)

test_1_96k_wav = ValidAudioFile(
    "./data/test/test1_96k.wav",  # NOTE: Running from the project root
    'wav',
    96000,
    2,
    10.00946875,
    960909)

test_1_mp3 = ValidAudioFile(
    "./data/test/test1.mp3",  # NOTE: Running from the project root
    'mp3',
    32000,
    2,
    10.00946875,
    320303)

test_1_mp4 = ValidAudioFile(
    "./data/test/creative_common.mp4",  # NOTE: Running from the project root
    'mp4',
    48000,
    2,
    2.2613333333333334,
    108544)


@pytest.fixture(scope="module",
                params=[test_1_wav, test_1_mp3, test_1_96k_wav])
def valid_audio_files(request):
    """ A valid wav file for testing

    The test1.wav is assumed to exist
    """
    return request.param


@pytest.fixture(scope="module", params=[test_1_wav, test_1_96k_wav])
def valid_wav_files(request):
    return request.param


@pytest.fixture(scope="module",
                params=[test_1_mp3, test_1_mp4, test_1_wav, test_1_96k_wav])
def valid_media_files(request):
    """
    ultimate one to pass for get_samplerate(...) ... etc
    """
    return request.param


def test_valid_wav_metadata(valid_wav_files):
    """ Test au.read_wavefile_metadata(...)"""

    filepath = valid_wav_files.filepath

    assert au.read_wavefile_metadata(filepath) == valid_wav_files


def test_valid_media_metadata_ffmpeg(valid_media_files):
    """ test au.read_audio_metadata_ffmpeg(...)
    The function does not return exact nsamples or seconds
    It is expected that the function will raise a RuntimeWarning for that
    Such files will be converted to wav before reading anyway
    """
    filepath = valid_media_files.filepath
    correct_sr = valid_media_files.samplerate
    correct_noc = valid_media_files.nchannels
    correct_duration = valid_media_files.seconds

    # TODO: [A] Test for raised warnings
    metadata = au.read_audio_metadata_ffmpeg(filepath)

    assert metadata.samplerate == correct_sr
    assert metadata.nchannels == correct_noc

    assert_almost_equal(correct_duration, metadata.seconds, decimal=1)


def test_valid_audio_metadata(valid_media_files):
    """ Test the audio_utils.get_audio_metadata(...) for valid wav file"""
    filepath = valid_media_files.filepath
    fmt = valid_media_files.format

    metadata = au.get_audio_metadata(filepath)
    if fmt == 'wav':
        assert valid_media_files == metadata
    else:
        assert metadata.samplerate == valid_media_files.samplerate
        assert metadata.nchannels == valid_media_files.nchannels


def test_AudioIO_from_audiometadata(valid_media_files):
    """Test if the returned updated metadata is accurate"""

    # known unsipported functionality for >48kHz files
    if valid_media_files.samplerate <= 48000:
        _, updated_metadata = au.AudioIO.from_audiometadata(valid_media_files)

        assert valid_media_files == updated_metadata
    else:
        pytest.skip(">48khz audio not supported by AudioIO")


def test_AudioIO_get_numpy_data(valid_media_files):
    """ Test for correct nsamples and nchannels """

    correct_ns = valid_media_files.nsamples
    correct_noc = valid_media_files.nchannels

    if valid_media_files.samplerate <= 48000:
        data = au.AudioIO.from_audiometadata(valid_media_files)[
            0].get_numpy_data()

        assert data.shape == (correct_ns, correct_noc)
    else:
        pytest.skip(">48khz audio not supported by AudioIO")
