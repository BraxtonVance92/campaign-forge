import pytest

from app.security import (
    content_type_matches_signature,
    detect_video_signature_family,
    sanitize_filename,
)
from app.storage import LocalDiskStorage
from tests.conftest import make_fake_mp4_bytes


@pytest.mark.parametrize(
    "malicious,expected_safe",
    [
        ("../../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system32\\config", "config"),
        ("/etc/passwd", "passwd"),
        ("....//....//etc/passwd", "passwd"),
        ("..", "upload"),
        ("...", "upload"),
        ("", "upload"),
        ("clip.mp4", "clip.mp4"),
        ("my video (final) v2.mov", "my_video__final__v2.mov"),
    ],
)
def test_sanitize_filename_defeats_traversal(malicious, expected_safe):
    result = sanitize_filename(malicious)
    assert "/" not in result
    assert "\\" not in result
    assert ".." not in result
    assert result == expected_safe


def test_local_disk_storage_refuses_to_escape_root(tmp_path):
    storage = LocalDiskStorage(root=str(tmp_path / "store"))
    with pytest.raises(ValueError, match="Refusing to write outside storage root"):
        storage.put_object("../../outside.txt", b"data", "text/plain")

    # Confirm nothing was written above the storage root.
    assert not (tmp_path / "outside.txt").exists()


def test_local_disk_storage_allows_legitimate_nested_keys(tmp_path):
    storage = LocalDiskStorage(root=str(tmp_path / "store"))
    storage.put_object("projects/p1/sources/s1/original/clip.mp4", b"data", "video/mp4")
    assert storage.get_object("projects/p1/sources/s1/original/clip.mp4") == b"data"


def test_detect_video_signature_family_mp4():
    assert detect_video_signature_family(make_fake_mp4_bytes()) == "mp4-or-mov"


def test_detect_video_signature_family_webm():
    webm_bytes = b"\x1a\x45\xdf\xa3" + b"\x00" * 100
    assert detect_video_signature_family(webm_bytes) == "webm"


def test_detect_video_signature_family_none_for_garbage():
    assert detect_video_signature_family(b"NOT A REAL VIDEO FILE" * 10) is None


def test_content_type_matches_signature_true_for_matching_mp4():
    assert content_type_matches_signature("video/mp4", make_fake_mp4_bytes()) is True


def test_content_type_matches_signature_false_for_mp4_claim_with_wrong_bytes():
    assert content_type_matches_signature("video/mp4", b"NOT A VIDEO" * 10) is False


def test_content_type_matches_signature_false_for_webm_claim_with_mp4_bytes():
    assert content_type_matches_signature("video/webm", make_fake_mp4_bytes()) is False


def test_content_type_matches_signature_unknown_content_type():
    assert content_type_matches_signature("application/pdf", make_fake_mp4_bytes()) is False
