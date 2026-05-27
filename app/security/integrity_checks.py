from app.events.models import EventEnvelope


class IntegrityChecks:
    def verify_append_only_order(self, events: list[EventEnvelope]) -> bool:
        timestamps = [event.timestamp for event in events]
        return timestamps == sorted(timestamps)

    def verify_schema_hashes(self, events: list[EventEnvelope]) -> bool:
        return all(event.schema_hash == event.compute_schema_hash() for event in events)

