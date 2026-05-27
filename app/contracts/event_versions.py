from app.events.models import EventName

CURRENT_EVENT_VERSION = "1.0"
DEFAULT_PRODUCER = "hermes-x"

EVENT_VERSIONS: dict[EventName, str] = {event: CURRENT_EVENT_VERSION for event in EventName}

