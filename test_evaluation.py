"""
Tests for the GitHub Copilot evaluation setup.
"""

import unittest
import json
import os
from unittest.mock import patch
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
    """Test cases for the core logic of AgentEvaluator."""

    @patch('evaluate_agents.AgentEvaluator._validate_config')
    @patch('evaluate_agents.AgentEvaluator._load_instructions')
    def test_preprocess_instructions_optimization(
        self, mock_load_instructions, mock_validate_config
    ):
        """
        Verify that the _preprocess_instructions method correctly adds
        pre-computed values to the instruction objects. This is key to
        the performance optimization.
        """
        # Arrange: Mock the necessary setup methods
        mock_validate_config.return_value = None
        mock_instructions = [
            {
                "id": "test01",
                "type": "debug",
                "title": "Test Instruction",
                "description": "A test.",
                "expected_response": "Hello World",
            },
            {
                "id": "test02",
                "type": "debug",
                "title": "Another Test",
                "description": "Another test without an expected response.",
            },
        ]
        mock_load_instructions.return_value = mock_instructions

        mock_config = {
            "agent_v1_endpoint": "mock",
            "agent_v2_endpoint": "mock",
            "api_key_v1": "mock",
            "api_key_v2": "mock",
            "instructions_file": "mock",
            "results_dir": "mock_results"
        }

        # Act: Initialize the AgentEvaluator, which triggers the
        # _preprocess_instructions method.
        evaluator = AgentEvaluator(mock_config)

        # Assert: Check that the pre-computed keys were added correctly
        processed_instruction = evaluator.instructions[0]
        self.assertIn("_expected_tokens", processed_instruction)
        self.assertIn("_expected_lower_words", processed_instruction)
        self.assertEqual(
            processed_instruction["_expected_tokens"], ["Hello", "World"]
        )
        self.assertEqual(
            processed_instruction["_expected_lower_words"], {"hello", "world"}
        )

        # Assert: Check that instructions without an expected_response are skipped
        unprocessed_instruction = evaluator.instructions[1]
        self.assertNotIn("_expected_tokens", unprocessed_instruction)
        self.assertNotIn("_expected_lower_words", unprocessed_instruction)


if __name__ == "__main__":
    unittest.main()
