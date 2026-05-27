from hashlib import sha256


class StateFingerprint:
    def hash_text(self, value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()

    def hash_json(self, value: dict | list) -> str:
        return self.hash_text(repr(value))

