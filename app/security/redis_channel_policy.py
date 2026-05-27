from pydantic import BaseModel


class RedisChannelValidation(BaseModel):
    allowed: bool
    reason: str = ""


class RedisChannelPolicy:
    def validate(self, channel: str) -> RedisChannelValidation:
        if not channel.startswith("hermes:"):
            return RedisChannelValidation(allowed=False, reason="channel outside hermes namespace")
        if any(character.isspace() for character in channel):
            return RedisChannelValidation(allowed=False, reason="channel contains whitespace")
        return RedisChannelValidation(allowed=True)
