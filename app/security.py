"""Upload-boundary security checks: filename sanitization and real file
signature validation. Both operate on user-controlled input (the upload
route) and must not trust it -- see CF-RUN-001 review findings.
"""

from __future__ import annotations

import re

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_filename(filename: str) -> str:
    """Reduce a user-supplied filename to a safe basename.

    Defeats path traversal (`../../etc/passwd`, `..\\..\\file`, absolute
    paths) by taking only the final path segment for both `/` and `\\`
    separators, then restricting to a safe character set. Never returns
    an empty, dot-only, or traversal-capable string.
    """
    name = (filename or "").replace("\x00", "")
    name = name.replace("\\", "/").split("/")[-1]
    name = _UNSAFE_CHARS.sub("_", name)
    name = name.strip(".")
    if not name:
        name = "upload"
    return name[:255]


# Magic-byte signatures, checked against the actual uploaded bytes --
# never trust the client-supplied Content-Type header alone.
_MP4_MOV_SIGNATURE_OFFSET = 4
_MP4_MOV_SIGNATURE = b"ftyp"
_WEBM_SIGNATURE = b"\x1a\x45\xdf\xa3"

CONTENT_TYPE_TO_SIGNATURE_FAMILY = {
    "video/mp4": "mp4-or-mov",
    "video/quicktime": "mp4-or-mov",
    "video/webm": "webm",
}


def detect_video_signature_family(data: bytes) -> str | None:
    """Return 'mp4-or-mov', 'webm', or None based on real file bytes."""
    if len(data) >= _MP4_MOV_SIGNATURE_OFFSET + 4 and (
        data[_MP4_MOV_SIGNATURE_OFFSET : _MP4_MOV_SIGNATURE_OFFSET + 4]
        == _MP4_MOV_SIGNATURE
    ):
        return "mp4-or-mov"
    if len(data) >= 4 and data[:4] == _WEBM_SIGNATURE:
        return "webm"
    return None


def content_type_matches_signature(content_type: str, data: bytes) -> bool:
    expected_family = CONTENT_TYPE_TO_SIGNATURE_FAMILY.get(content_type)
    if expected_family is None:
        return False
    return detect_video_signature_family(data) == expected_family
