import hashlib


def str_to_sha256(data: str):
    hash_object = hashlib.sha256(data.encode("utf-8"))
    hex_digest = hash_object.hexdigest()
    return hex_digest
