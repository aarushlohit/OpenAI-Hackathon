from pydantic import BaseModel, Field


class BenchmarkScenario(BaseModel):
    name: str
    input_text: str = Field(min_length=1)
    expected_severity: str


class ScenarioSuite:
    def scenarios(self) -> list[BenchmarkScenario]:
        return [
            BenchmarkScenario(name="telegram_refund", input_text="Pay refundable deposit on Telegram", expected_severity="high"),
            BenchmarkScenario(name="fake_offer_letter", input_text="Offer letter asks for security deposit", expected_severity="medium"),
            BenchmarkScenario(name="cloned_domain", input_text="Verify at https://new-careers.xyz", expected_severity="medium"),
            BenchmarkScenario(name="recruiter_impersonation", input_text="HR director direct offer no interview", expected_severity="medium"),
        ]

