"""
Tests for the GitHub Copilot evaluation setup.
"""

import unittest
import json
import os


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


import numpy as np
from evaluate_agents import AgentEvaluator

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

class TestMetricsCalculation(unittest.TestCase):
    """Test cases for the metrics calculation."""

    def setUp(self):
        """Set up the evaluator with a mock configuration."""
        # Mock configuration that avoids hitting real endpoints
        self.config = {
            "agent_v1_endpoint": "mock_v1",
            "agent_v2_endpoint": "mock_v2",
            "api_key_v1": "mock_key",
            "api_key_v2": "mock_key",
            "instructions_file": "instructions.json",
            "results_dir": "test_results",  # Add mock results directory
        }
        # We need to initialize the evaluator to get access to _calculate_metrics
        # It will try to load instructions.json, which is fine.
        self.evaluator = AgentEvaluator(self.config)

    def test_calculate_metrics_precomputation(self):
        """
        Verify that _calculate_metrics works correctly with pre-computed inputs.
        This tests the core logic that was refactored.
        """
        response = "the quick brown fox"
        expected = "the quick brown dog"

        # Pre-compute tokens and sets, simulating what run_evaluation now does
        response_tokens = response.split()
        expected_tokens = expected.split()
        response_lower_words = set(response.lower().split())
        expected_lower_words = set(expected.lower().split())

        metrics = self.evaluator._calculate_metrics(
            response,
            expected,
            response_tokens,
            expected_tokens,
            response_lower_words,
            expected_lower_words,
        )

        # Verify some key metrics
        self.assertAlmostEqual(metrics["jaccard_similarity"], 3 / 5, places=5)
        self.assertTrue(0 < metrics["bleu_score"] < 1)
        self.assertTrue(0 < metrics["rouge_l"] < 1)
        self.assertEqual(metrics["response_length"], len(response))


if __name__ == "__main__":
    unittest.main()
