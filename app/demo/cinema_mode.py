from uuid import uuid4

from app.demo.scenarios import DemoScenario
from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName


class CinemaMode:
    def __init__(self, event_bus: InMemoryEventBus) -> None:
        self._event_bus = event_bus

    async def play(self, scenario: DemoScenario) -> None:
        correlation_id = uuid4()
        for index, beat in enumerate(scenario.beats):
            await self._event_bus.publish(
                EventEnvelope(
                    event=EventName.DEMO_CINEMA_FRAME,
                    correlation_id=correlation_id,
                    payload={
                        "scenario": scenario.name,
                        "frame": index,
                        "title": scenario.title,
                        "beat": beat,
                    },
                )
            )

