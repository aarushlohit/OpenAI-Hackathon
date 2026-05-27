from dataclasses import dataclass
from uuid import UUID, uuid4

from app.events.models import EventEnvelope


@dataclass(frozen=True)
class Subscription:
    subscription_id: UUID
    correlation_id: UUID
    replay: bool = True


class SubscriptionRegistry:
    def __init__(self) -> None:
        self._subscriptions: dict[UUID, Subscription] = {}

    def create(self, correlation_id: UUID, replay: bool = True) -> Subscription:
        subscription = Subscription(uuid4(), correlation_id, replay)
        self._subscriptions[subscription.subscription_id] = subscription
        return subscription

    def remove(self, subscription_id: UUID) -> None:
        self._subscriptions.pop(subscription_id, None)

    def accepts(self, subscription: Subscription, event: EventEnvelope) -> bool:
        return event.correlation_id == subscription.correlation_id

