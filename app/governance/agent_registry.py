from pathlib import Path

from app.governance.permissions import AgentPermissions


class AgentContractRegistry:
    def __init__(self) -> None:
        self._contracts: dict[str, AgentPermissions] = {}

    def register(self, agent: str, permissions: AgentPermissions) -> None:
        self._contracts[agent] = permissions

    def get(self, agent: str) -> AgentPermissions | None:
        return self._contracts.get(agent)

    def load_yaml(self, path: Path) -> None:
        current: str | None = None
        data: dict[str, dict[str, object]] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line == "agents:":
                continue
            if not raw_line.startswith("    ") and line.endswith(":"):
                current = line[:-1]
                data[current] = {}
                continue
            if current and ":" in line:
                key, value = line.split(":", 1)
                data[current][key] = self._parse_value(value.strip())
        for agent, values in data.items():
            self.register(agent, AgentPermissions.model_validate(values))

    def _parse_value(self, value: str):
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            return [] if not inner else [item.strip() for item in inner.split(",")]
        try:
            return float(value)
        except ValueError:
            return value

