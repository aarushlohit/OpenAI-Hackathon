from uuid import uuid4


def new_investigation_id() -> str:
    return f"INV-{uuid4().hex[:8].upper()}"

