from uuid import uuid4

from app.autonomous.alerting import EscalationRules
from app.autonomous.watchers import EntityWatcher, WatchTarget
from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.intelligence import ThreatFeed, ThreatFeedItem


class AutonomousMonitorEngine:
    def __init__(
        self,
        watcher: EntityWatcher,
        escalation_rules: EscalationRules,
        event_bus: InMemoryEventBus,
        threat_feed: ThreatFeed,
    ) -> None:
        self._watcher = watcher
        self._escalation_rules = escalation_rules
        self._event_bus = event_bus
        self._threat_feed = threat_feed

    async def monitor(self, target: WatchTarget) -> None:
        related = await self._watcher.check(target)
        if not related:
            return
        feed_item = ThreatFeedItem(
            title="Recurring entity detected",
            detail=f"{target.entity} appears in prior investigations",
            severity="high" if len(related) > 1 else "medium",
        )
        await self._threat_feed.publish(feed_item)
        await self._publish(EventName.THREAT_FEED_UPDATE, target, {"feed": feed_item.model_dump(mode="json")})
        await self._publish(EventName.RECURRING_PATTERN_DETECTED, target, {"related_investigations": related})
        escalation = self._escalation_rules.evaluate(target.entity, related)
        if escalation is not None:
            await self._publish(EventName(escalation.event), target, escalation.model_dump(mode="json"))

    async def _publish(self, event: EventName, target: WatchTarget, payload: dict) -> None:
        await self._event_bus.publish(
            EventEnvelope(
                event=event,
                correlation_id=uuid4(),
                payload={"entity": target.entity, "entity_type": target.entity_type, **payload},
            )
        )

