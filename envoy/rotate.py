"""Key rotation support for envoy: re-encrypt stored envs with a new password."""

from __future__ import annotations

from typing import List

from envoy.storage import _get_store_path, _load_raw, _save_raw, list_projects
from envoy.crypto import decrypt, encrypt
from envoy.audit import record


def rotate_project(
    project: str,
    old_password: str,
    new_password: str,
) -> None:
    """Re-encrypt a single project's stored env blob with *new_password*.

    Raises
    ------
    KeyError
        If *project* does not exist in the store.
    ValueError
        If *old_password* is incorrect (propagated from crypto.decrypt).
    """
    store_path = _get_store_path()
    raw = _load_raw(store_path, project)  # raises KeyError if missing
    plaintext = decrypt(bytes.fromhex(raw), old_password)
    new_blob = encrypt(plaintext, new_password)
    _save_raw(store_path, project, new_blob.hex())
    record("rotate", project)


def rotate_all(
    old_password: str,
    new_password: str,
) -> List[str]:
    """Rotate encryption for every project in the store.

    Returns the list of project names that were successfully rotated.
    Raises on the first project whose decryption fails.
    """
    projects = list_projects()
    rotated: List[str] = []
    for project in projects:
        rotate_project(project, old_password, new_password)
        rotated.append(project)
    return rotated
