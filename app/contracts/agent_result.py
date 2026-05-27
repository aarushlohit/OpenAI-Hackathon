from typing import TypeAlias

from app.models.behavior_result import BehaviorResult
from app.models.osint_result import OSINTResult
from app.models.vision_result import VisionResult

AgentResult: TypeAlias = BehaviorResult | OSINTResult | VisionResult

