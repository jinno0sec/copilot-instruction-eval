"""
Tests for the GitHub Copilot evaluation setup.
"""

import unittest
import json
import os
import shutil
from unittest.mock import patch, MagicMock

from evaluate_agents import AgentEvaluator


class TestEvaluationSetup(unittest.TestCase):
    """Test cases for the evaluation setup."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.instructions_file = os.path.join(cls.test_dir, "instructions.json")

    def test_instructions_file_exists(self):
        """Test that the instructions file exists."""
        self.assertTrue(
            os.path.exists(self.instructions_file),
            f"Instructions file not found at {self.instructions_file}"
        )

    def test_instructions_file_format(self):
        """Test that the instructions file has the correct format."""
        try:
            with open(self.instructions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertIn("instructions", data)
            self.assertIsInstance(data["instructions"], list)
            self.assertGreater(
                len(data["instructions"]), 0, "No instructions found"
            )

            # Check each instruction has required fields
            for instruction in data["instructions"]:
                self.assertIn("id", instruction)
                self.assertIn("type", instruction)
                self.assertIn("title", instruction)
                self.assertIn("description", instruction)

        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in instructions file: {e}")

    def test_required_packages(self):
        """Test that required Python packages can be imported."""
        try:
            import pandas  # noqa: F401
            import numpy as np  # noqa: F401
            import matplotlib  # noqa: F401
            import nltk  # noqa: F401
            import openai  # noqa: F401
            import pytest  # noqa: F401
            import requests  # noqa: F401
        except ImportError as e:
            self.fail(f"Failed to import required package: {e}")


class TestAgentEndpoints(unittest.TestCase):
    """Test cases for agent API endpoints."""

    def test_agent_v1_endpoint(self):
        """Test that agent_v1 endpoint is accessible."""
        # This is a placeholder test
        self.skipTest("Agent endpoint tests require actual API endpoints")

    def test_agent_v2_endpoint(self):
        """Test that agent_v2 endpoint is accessible."""
        # This is a placeholder test
        self.skipTest("Agent endpoint tests require actual API endpoints")


class TestAgentEvaluatorLogic(unittest.TestCase):
    """Tests the core logic of the AgentEvaluator class."""

    def setUp(self):
        """Set up for each test."""
        # Create a dummy instructions file for testing
        self.instructions_data = {
            "instructions": [
                {
                    "id": "test-001",
                    "type": "test",
                    "title": "Test Instruction",
                    "description": "A test instruction.",
                    "difficulty": "easy",
                    "expected_response": "expected response"
                }
            ]
        }
        self.test_instructions_file = "test_instructions.json"
        with open(self.test_instructions_file, "w") as f:
            json.dump(self.instructions_data, f)

        # Create a dummy config that passes validation
        self.config = {
            "agent_v1_endpoint": "http://dummy.url/v1",
            "agent_v2_endpoint": "http://dummy.url/v2",
            "api_key_v1": "dummy_key_v1",
            "api_key_v2": "dummy_key_v2",
            "instructions_file": self.test_instructions_file,
            "results_dir": "test_results",
            "timeout": 1,
            "max_retries": 1,
            "retry_delay": 1,
        }

        # Clean up results directory before test
        if os.path.exists(self.config["results_dir"]):
            shutil.rmtree(self.config["results_dir"])

    def tearDown(self):
        """Clean up after each test."""
        os.remove(self.test_instructions_file)
        if os.path.exists(self.config["results_dir"]):
            shutil.rmtree(self.config["results_dir"])

    @patch('evaluate_agents.AgentEvaluator._call_agent_with_retry')
    @patch('evaluate_agents.AgentEvaluator._save_results')
    def test_run_evaluation_calls_save_once(self, mock_save_results, mock_call_agent):
        """
        Verify that run_evaluation calls _save_results only once after processing all instructions.
        """
        # Arrange: Mock the agent API call to return a successful dummy response
        mock_call_agent.return_value = ("dummy agent response", None)

        # Act: Initialize the evaluator and run the evaluation
        evaluator = AgentEvaluator(self.config)
        evaluator.run_evaluation()

        # Assert: Check that the agent was called for each version
        self.assertEqual(mock_call_agent.call_count, 2) # v1 and v2

        # Assert: Check that results were populated
        self.assertEqual(len(evaluator.results), 1)
        self.assertEqual(evaluator.results[0]['instruction_id'], 'test-001')

        # Assert: Crucially, check that _save_results was called exactly once
        mock_save_results.assert_called_once()


if __name__ == "__main__":
    unittest.main()
