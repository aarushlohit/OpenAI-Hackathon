from app.demo.scenarios import DemoScenario


class DemoReliabilityMode:
    def normalize(self, scenario: DemoScenario) -> DemoScenario:
        return scenario.model_copy(update={"beats": list(scenario.beats)})

