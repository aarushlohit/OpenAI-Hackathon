import json
import zlib


class EventCompressor:
    def compress(self, payload: dict) -> bytes:
        return zlib.compress(json.dumps(payload, sort_keys=True).encode("utf-8"))

    def decompress(self, payload: bytes) -> dict:
        return json.loads(zlib.decompress(payload).decode("utf-8"))

