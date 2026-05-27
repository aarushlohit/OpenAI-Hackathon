from collections.abc import Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, tool: Callable) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> Callable | None:
        return self._tools.get(name)

    def list(self) -> list[str]:
        return sorted(self._tools)

