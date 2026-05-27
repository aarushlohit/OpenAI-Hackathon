from pathlib import Path

from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content: str = Field(min_length=1)


class PromptRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self._root = root or Path(__file__).resolve().parent

    def load(self, category: str, name: str, version: str = "v1") -> PromptTemplate:
        path = self._root / category / f"{name}.md"
        content = path.read_text(encoding="utf-8")
        return PromptTemplate(name=f"{category}.{name}", version=version, content=content)

