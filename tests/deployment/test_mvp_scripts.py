from pathlib import Path
import stat
import unittest


class MvpScriptTests(unittest.TestCase):
    def test_ship_scripts_exist_and_are_executable(self) -> None:
        for script in [
            "scripts/start_hermes.sh",
            "scripts/dev_bootstrap.sh",
            "scripts/demo_mode.sh",
            "scripts/reset_runtime.sh",
            "scripts/validate_live_providers.py",
        ]:
            path = Path(script)
            self.assertTrue(path.exists(), script)
            self.assertTrue(path.stat().st_mode & stat.S_IXUSR, script)

    def test_reset_runtime_requires_explicit_volume_confirmation(self) -> None:
        content = Path("scripts/reset_runtime.sh").read_text(encoding="utf-8")

        self.assertIn("CONFIRM_RESET", content)
        self.assertIn("--volumes", content)


if __name__ == "__main__":
    unittest.main()
