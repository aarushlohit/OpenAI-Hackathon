import unittest
from pathlib import Path


class DeploymentFilesTests(unittest.TestCase):
    def test_deployment_files_exist(self) -> None:
        self.assertTrue(Path("Dockerfile").exists())
        self.assertTrue(Path("docker-compose.yml").exists())
        self.assertTrue(Path(".github/workflows/ci.yml").exists())

