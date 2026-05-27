from pydantic import BaseModel, Field


class DemoScenario(BaseModel):
    name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    input_text: str = Field(min_length=1)
    beats: list[str] = Field(default_factory=list)


class DemoScenarioRegistry:
    def list(self) -> list[DemoScenario]:
        return [
            DemoScenario(
                name="telegram_onboarding_scam",
                title="Telegram Onboarding Scam",
                input_text="Join Telegram @fakehr for direct offer and pay refundable deposit to pay@upi.",
                beats=["Recruiter pressure detected", "Payment identifier extracted", "Threat graph updated"],
            ),
            DemoScenario(
                name="phishing_portal",
                title="Phishing Portal Analysis",
                input_text="Verify your account at https://new-careers.xyz/verify before interview.",
                beats=["Suspicious domain found", "Portal language analyzed", "Risk profile calculated"],
            ),
            DemoScenario(
                name="forged_offer_letter",
                title="Forged Offer Letter",
                input_text="Offer letter requires security deposit before joining confirmation.",
                beats=["Offer letter anomaly detected", "Deposit coercion detected"],
            ),
            DemoScenario(
                name="coordinated_campaign_replay",
                title="Coordinated Campaign Replay",
                input_text=(
                    "Multiple domains reuse @fakehr and pay@upi across cloned internship portals."
                ),
                beats=[
                    "Reused payment identifier linked",
                    "Domain cluster expanded",
                    "Campaign correlation raised",
                    "Replay timeline verified",
                ],
            ),
        ]

    def get(self, name: str) -> DemoScenario | None:
        return next((scenario for scenario in self.list() if scenario.name == name), None)
