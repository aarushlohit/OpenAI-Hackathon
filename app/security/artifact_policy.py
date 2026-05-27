from pydantic import BaseModel, Field

from app.core.errors import UnsafeInputError


class ArtifactDescriptor(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=120)
    size_bytes: int = Field(ge=0, le=20_000_000)


class ArtifactPolicy:
    allowed_mime_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "application/pdf",
        "text/plain",
    }

    def validate(self, artifact: ArtifactDescriptor) -> None:
        if artifact.mime_type not in self.allowed_mime_types:
            raise UnsafeInputError(f"Unsupported MIME type: {artifact.mime_type}")
        if "\x00" in artifact.filename:
            raise UnsafeInputError("Filename contains null bytes")

