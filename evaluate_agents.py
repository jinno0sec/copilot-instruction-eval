"""
GitHub Copilot Agent Evaluation Script

This script evaluates two versions of GitHub Copilot agents (v1 and v2)
using a set of predefined instructions. It collects responses, calculates
metrics, and generates a comparison report with visualizations.
"""

import json
import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional, Tuple

import requests
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import seaborn as sns

# Load environment variables from .env before anything else
load_dotenv()

# Ensure the output directory exists
os.makedirs("results", exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 設定
CONFIG = {
    "agent_v1_endpoint": os.getenv("AGENT_V1_ENDPOINT"),
    "agent_v2_endpoint": os.getenv("AGENT_V2_ENDPOINT"),
    "agent_v2_model": os.getenv("AGENT_V2_MODEL"),
    "api_key_v1": os.getenv("AGENT_V1_API_KEY"),
    "api_key_v2": os.getenv("AGENT_V2_API_KEY"),
    "instructions_file": "instructions.json",
    "results_dir": "results",
    "timeout": 60,  # 秒
    "max_retries": 3,  # リトライ回数
    "retry_delay": 5,  # リトライ間隔（秒）
}


class AgentEvaluator:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the evaluator with configuration."""
        self.config = config
        self._validate_config()
        self.instructions = self._load_instructions()
        self.results = []
        self._setup_directories()
        self.rouge = Rouge()  # ROUGEスコア計算用

        # Download required NLTK data
        try:
            import nltk
            nltk.download('punkt', quiet=True)
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")

    def _validate_config(self) -> None:
        """Validate the configuration."""
        required_vars = [
            "agent_v1_endpoint", "agent_v2_endpoint",
            "api_key_v1", "api_key_v2"
        ]

        missing_vars = [
            var for var in required_vars if not self.config.get(var)
        ]
        if missing_vars:
            msg = (
                "Missing required configuration variables: "
                f"{', '.join(missing_vars)}\n"
                "Please set these in your .env file or environment variables."
            )
            raise ValueError(msg)

    def _load_instructions(self) -> List[Dict[str, Any]]:
        """Load instructions from the JSON file."""
        try:
            filepath = self.config["instructions_file"]
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                instructions = data.get("instructions", [])
                logger.info(
                    f"Loaded {len(instructions)} instructions from {filepath}"
                )
                return instructions
        except FileNotFoundError:
            logger.error(f"Instructions file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in instructions file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading instructions: {e}")
            raise

    def _setup_directories(self) -> None:
        """Create necessary directories for storing results."""
        os.makedirs(self.config["results_dir"], exist_ok=True)

    def _get_sanitized_config(self) -> Dict[str, Any]:
        """Return a copy of the config with sensitive values removed."""
        sanitized_config = self.config.copy()
        if "api_key_v1" in sanitized_config:
            sanitized_config["api_key_v1"] = "***REDACTED***"
        if "api_key_v2" in sanitized_config:
            sanitized_config["api_key_v2"] = "***REDACTED***"
        return sanitized_config

    def _call_agent_with_retry(
            self, agent_version: str, instruction_text: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Make API call with retry mechanism.

        Returns:
            A tuple of (response_text, error_message).
        """
        api_key = self.config[f"api_key_{agent_version}"]
        headers = {}
        params = {}
        payload = {}
        endpoint = self.config[f"agent_{agent_version}_endpoint"]

        if agent_version == 'v2':
            model_name = self.config.get("agent_v2_model")
            if not model_name:
                url_parts = endpoint.split('/')
                if len(url_parts) > 7 and url_parts[6] == 'completions':
                    model_name = '/'.join(url_parts[7:])
                    logger.info(
                        "AGENT_V2_MODEL not set, parsed model "
                        f"'{model_name}' from endpoint URL."
                    )
                else:
                    model_name = 'llama3-8b-8192'  # Fallback
                    logger.warning(
                        "AGENT_V2_MODEL not set and couldn't parse from URL. "
                        f"Using default model: {model_name}"
                    )

            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": [{"role": "user", "content": instruction_text}],
                "model": model_name
            }
            params = None
        else:  # agent_version == 'v1'
            headers = {"Content-Type": "application/json"}
            params = {'key': api_key}
            payload = {"contents": [{"parts": [{"text": instruction_text}]}]}

        last_error = None
        for attempt in range(self.config["max_retries"]):
            try:
                logger.debug(
                    f"--- API Request Details (Attempt {attempt + 1}) ---"
                )
                logger.debug(f"Agent: {agent_version}, URL: {endpoint}")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Params: {params}")
                payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
                logger.debug(f"Payload: {payload_str}")

                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.config["timeout"],
                    params=params
                )
                response.raise_for_status()

                if agent_version == 'v2':
                    content = response.json()['choices'][0]['message']['content']
                    return content, None
                else:  # agent_version == 'v1'
                    content = (
                        response.json()["candidates"][0]["content"]
                        ["parts"][0]["text"]
                    )
                    return content, None

            except requests.exceptions.RequestException as e:
                last_error = e
                wait_time = self.config["retry_delay"] * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed for {agent_version}. "
                    f"Retrying in {wait_time} seconds... Error: {e}"
                )
                time.sleep(wait_time)

        error_message = (
            f"Failed after {self.config['max_retries']} attempts: "
            f"{str(last_error)}"
        )
        logger.error(f"Error with {agent_version}: {error_message}")
        return None, error_message

    def _calculate_metrics(
            self, response: str, expected: str,
            response_tokens: list, expected_tokens: list,
            response_lower_words: set, expected_lower_words: set
    ) -> Dict[str, float]:
        """
        Calculate evaluation metrics for the response.
        This method is optimized to accept pre-tokenized inputs
        to avoid redundant text processing in a loop.
        """
        metrics = {
            "response_length": len(response),
            "expected_length": len(expected),
            "length_ratio": len(response) / max(len(expected), 1),
        }

        intersection = len(response_lower_words.intersection(expected_lower_words))
        union = len(response_lower_words.union(expected_lower_words))
        metrics["jaccard_similarity"] = intersection / union if union > 0 else 0

        try:
            smoothie = SmoothingFunction().method4
            metrics["bleu_score"] = sentence_bleu(
                [expected_tokens],
                response_tokens,
                smoothing_function=smoothie
            )
        except Exception as e:
            logger.warning(f"Error calculating BLEU score: {e}")
            metrics["bleu_score"] = 0.0

        try:
            if response.strip() and expected.strip():
                rouge_scores = self.rouge.get_scores(response, expected)[0]
                metrics.update({
                    "rouge_1": rouge_scores["rouge-1"]["f"],
                    "rouge_2": rouge_scores["rouge-2"]["f"],
                    "rouge_l": rouge_scores["rouge-l"]["f"],
                })
            else:
                metrics.update({
                    "rouge_1": 0.0, "rouge_2": 0.0, "rouge_l": 0.0,
                })
        except Exception as e:
            logger.warning(f"Error calculating ROUGE scores: {e}")
            metrics.update({
                "rouge_1": 0.0, "rouge_2": 0.0, "rouge_l": 0.0,
            })

        return metrics

    def run_evaluation(self) -> None:
        """Run evaluation on all instructions for both agents."""
        logger.info(
            f"Starting evaluation of {len(self.instructions)} instructions..."
        )

        for instruction in tqdm(self.instructions,
                                desc="Evaluating instructions"):
            instruction_id = instruction["id"]
            logger.info(
                f"\nEvaluating instruction: {instruction['title']} "
                f"({instruction['type']})"
            )

            logger.info("  Testing agent_v1...")
            result_v1 = self._evaluate_instruction(instruction, "v1")

            logger.info("  Testing agent_v2...")
            result_v2 = self._evaluate_instruction(instruction, "v2")

            self.results.append({
                "instruction_id": instruction_id,
                "instruction_type": instruction["type"],
                "difficulty": instruction["difficulty"],
                "v1_success": result_v1["success"],
                "v2_success": result_v2["success"],
                "v1_metrics": result_v1.get("metrics", {}),
                "v2_metrics": result_v2.get("metrics", {})
            })

        # Save results once after all instructions are processed
        self._save_results()

    def _evaluate_instruction(
            self, instruction: Dict[str, Any], agent_version: str
    ) -> Dict[str, Any]:
        """Evaluate a single instruction with the specified agent version."""
        result = {"success": False}

        prompt_parts = []
        if instruction.get("description"):
            prompt_parts.append(instruction["description"])
        if instruction.get("code"):
            prompt_parts.append(f'\n\n```\n{instruction["code"]}\n```')
        if instruction.get("requirements"):
            req_text = "\n".join(f'- {r}' for r in instruction["requirements"])
            prompt_parts.append(f'\n\nRequirements:\n{req_text}')
        instruction_text = "\n".join(prompt_parts)

        start_time = time.time()
        response_text, error = self._call_agent_with_retry(
            agent_version, instruction_text
        )
        duration = time.time() - start_time

        if error is None and response_text is not None:
            result["success"] = True
            if "expected_response" in instruction:
                # Pre-computation for optimization
                expected_response = instruction["expected_response"]
                response_tokens = response_text.split()
                expected_tokens = expected_response.split()
                response_lower_words = set(response_text.lower().split())
                expected_lower_words = set(expected_response.lower().split())

                metrics = self._calculate_metrics(
                    response_text,
                    expected_response,
                    response_tokens,
                    expected_tokens,
                    response_lower_words,
                    expected_lower_words
                )
                metrics["response_time"] = duration
                result["metrics"] = metrics
            logger.info(f"  {agent_version} completed in {duration:.2f}s")
        else:
            error_msg = (
                f"Error with {agent_version}: {error or 'Unknown error'}"
            )
            logger.error(f"  {error_msg}")
            result["error"] = error_msg

        return result

    def _save_results(self) -> None:
        """Save current results to JSON and CSV files."""
        results_file = os.path.join(
            self.config["results_dir"], "evaluation_results.json"
        )
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "config": self._get_sanitized_config(),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)

        self._save_results_csv()
        logger.info(f"Results saved to {results_file}")

    def _save_results_csv(self) -> None:
        """Save flattened results to CSV for easier analysis."""
        if not self.results:
            return

        flattened = []
        for result in self.results:
            row = {
                "instruction_id": result["instruction_id"],
                "instruction_type": result["instruction_type"],
                "difficulty": result["difficulty"],
                "v1_success": int(result["v1_success"]),
                "v2_success": int(result["v2_success"]),
            }

            for version in ["v1", "v2"]:
                prefix = f"{version}_"
                metrics = result.get(f"{prefix}metrics", {})
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        row[f"{prefix}{key}"] = value

            flattened.append(row)

        csv_file = os.path.join(
            self.config["results_dir"], "evaluation_results.csv"
        )
        df = pd.DataFrame(flattened)
        df.to_csv(csv_file, index=False)
        logger.info(f"CSV results saved to {csv_file}")

    def generate_report(self) -> None:
        """Generate a comprehensive markdown report with visualizations."""
        if not self.results:
            logger.warning("No results to generate report.")
            return

        report_file = os.path.join(
            self.config["results_dir"], "evaluation_report.md"
        )
        self._generate_visualizations()

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# GitHub Copilot Agent Evaluation Report\n\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n\n")

            total = len(self.results)
            v1_success = sum(1 for r in self.results if r["v1_success"])
            v2_success = sum(1 for r in self.results if r["v2_success"])
            improvement = (v2_success - v1_success) / total if total > 0 else 0

            f.write("## 📊 Summary\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Total Instructions | {total} |\n")
            v1_rate = v1_success / total if total > 0 else 0
            v2_rate = v2_success / total if total > 0 else 0
            f.write(
                f"| Agent v1 Success Rate | {v1_rate:.1%} "
                f"({v1_success}/{total}) |\n"
            )
            f.write(
                f"| Agent v2 Success Rate | {v2_rate:.1%} "
                f"({v2_success}/{total}) |\n"
            )
            f.write(f"| Improvement | {improvement:+.1%} points |\n\n")

            f.write("## 📈 Success Rate Comparison\n\n")
            f.write(
                "![Success Rate Comparison](success_rate_comparison.png)\n\n"
            )

            f.write("## 📊 Metrics Comparison\n\n")
            f.write("### Average Metrics\n")
            f.write("| Metric | Agent v1 | Agent v2 | Difference |\n")
            f.write("|--------|----------|----------|------------|\n")

            metrics_to_avg = [
                "jaccard_similarity", "bleu_score", "rouge_1", "rouge_2",
                "rouge_l", "response_time"
            ]
            for metric in metrics_to_avg:
                v1_avg = self._calculate_average_metric(metric, "v1")
                v2_avg = self._calculate_average_metric(metric, "v2")
                diff = v2_avg - v1_avg
                diff_str = f"{diff:+.3f}"
                if metric == "response_time":
                    f.write(
                        f"| {metric} (s) | {v1_avg:.3f} | {v2_avg:.3f} | "
                        f"{diff_str} |\n"
                    )
                else:
                    f.write(
                        f"| {metric} | {v1_avg:.3f} | {v2_avg:.3f} | "
                        f"{diff_str} |\n"
                    )

            f.write("\n![Metrics Comparison](metrics_comparison.png)\n\n")

            f.write("## 📋 Detailed Results\n\n")
            f.write("<details>")
            f.write("<summary>Click to expand detailed results</summary>\n\n")
            self._write_detailed_results_table(f)
            f.write("</details>\n\n")

            f.write("## ⚙️ Configuration\n\n")
            f.write("<details>")
            f.write("<summary>Click to view evaluation configuration</summary>\n\n")
            f.write("```json\n")
            f.write(json.dumps(self._get_sanitized_config(), indent=2))
            f.write("\n```\n")
            f.write("</details>\n")

        logger.info(f"Report generated at {report_file}")

    def _write_detailed_results_table(self, file_handle) -> None:
        """Write the detailed results markdown table to the file."""
        file_handle.write(
            "| ID | Type | Difficulty | v1 Success | v2 Success | "
            "v1 Jaccard | v2 Jaccard | v1 BLEU | v2 BLEU | v1 ROUGE-L | "
            "v2 ROUGE-L | v1 Time (s) | v2 Time (s) |\n"
        )
        file_handle.write(
            "|----|------|------------|------------|------------|--"
            "----------|------------|---------|---------|------------|--"
            "----------|-------------|-------------|\n"
        )

        for result in sorted(self.results, key=lambda x: x["instruction_id"]):
            v1_m = result.get("v1_metrics", {})
            v2_m = result.get("v2_metrics", {})
            file_handle.write(
                f"| {result['instruction_id']} | "
                f"{result['instruction_type']} | {result['difficulty']} | "
                f"{'✅' if result['v1_success'] else '❌'} | "
                f"{'✅' if result['v2_success'] else '❌'} | "
                f"{v1_m.get('jaccard_similarity', 0):.3f} | "
                f"{v2_m.get('jaccard_similarity', 0):.3f} | "
                f"{v1_m.get('bleu_score', 0):.3f} | "
                f"{v2_m.get('bleu_score', 0):.3f} | "
                f"{v1_m.get('rouge_l', 0):.3f} | "
                f"{v2_m.get('rouge_l', 0):.3f} | "
                f"{v1_m.get('response_time', 0):.2f} | "
                f"{v2_m.get('response_time', 0):.2f} |\n"
            )

    def _calculate_average_metric(self, metric_name: str,
                                  version: str) -> float:
        """Calculate average of a specific metric for a version."""
        total = 0
        count = 0

        for result in self.results:
            metrics = result.get(f"{version}_metrics", {})
            if metric_name in metrics and metrics[metric_name] is not None:
                total += metrics[metric_name]
                count += 1

        return total / count if count > 0 else 0.0

    def _generate_visualizations(self) -> None:
        """Generate visualization charts for the evaluation results."""
        try:
            sns.set_theme(style="whitegrid")

            self._plot_success_rate()
            self._plot_metrics_comparison()
            self._plot_response_time_comparison()

            logger.info("Visualizations generated successfully")

        except Exception as e:
            logger.error(f"Error generating visualizations: {e}",
                         exc_info=True)

    def _plot_success_rate(self):
        """Plot and save the success rate comparison chart."""
        total = len(self.results)
        v1_success = sum(1 for r in self.results if r["v1_success"])
        v2_success = sum(1 for r in self.results if r["v2_success"])
        v1_rate = v1_success / total * 100 if total > 0 else 0
        v2_rate = v2_success / total * 100 if total > 0 else 0

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(1)
        width = 0.35

        rects1 = ax.bar(x - width / 2, v1_rate, width, label='Agent v1')
        rects2 = ax.bar(x + width / 2, v2_rate, width, label='Agent v2')

        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Agent Success Rate Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([''])
        ax.legend()

        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(rect.get_x() + rect.get_width() / 2,
                                height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        plt.tight_layout()
        plt.savefig(
            os.path.join(self.config["results_dir"],
                         "success_rate_comparison.png")
        )
        plt.close()

    def _plot_metrics_comparison(self):
        """Plot and save the metrics comparison chart."""
        metrics = ["jaccard_similarity", "bleu_score", "rouge_1",
                   "rouge_2", "rouge_l"]
        v1_avgs = [self._calculate_average_metric(m, "v1") for m in metrics]
        v2_avgs = [self._calculate_average_metric(m, "v2") for m in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        rects1 = ax.bar(x - width/2, v1_avgs, width, label='Agent v1')
        rects2 = ax.bar(x + width/2, v2_avgs, width, label='Agent v2')

        ax.set_ylabel('Score')
        ax.set_title('Average Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
        ax.legend()

        def autolabel_metrics(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.3f}',
                            xy=(rect.get_x() + rect.get_width() / 2,
                                height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)

        autolabel_metrics(rects1)
        autolabel_metrics(rects2)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.config["results_dir"], "metrics_comparison.png")
        )
        plt.close()

    def _plot_response_time_comparison(self):
        """Plot and save the response time comparison chart."""
        v1_times = [
            r.get("v1_metrics", {}).get("response_time")
            for r in self.results
            if r.get("v1_metrics", {}).get("response_time") is not None
        ]
        v2_times = [
            r.get("v2_metrics", {}).get("response_time")
            for r in self.results
            if r.get("v2_metrics", {}).get("response_time") is not None
        ]

        if v1_times and v2_times:
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(2)

            v1_mean, v1_std = np.mean(v1_times), np.std(v1_times, ddof=1)
            v2_mean, v2_std = np.mean(v2_times), np.std(v2_times, ddof=1)

            rects1 = ax.bar(x[0], v1_mean, width=0.6, yerr=v1_std,
                            capsize=10, label='Agent v1', alpha=0.7)
            rects2 = ax.bar(x[1], v2_mean, width=0.6, yerr=v2_std,
                            capsize=10, label='Agent v2', alpha=0.7)

            ax.set_ylabel('Response Time (s)')
            ax.set_title('Average Response Time Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels(['Agent v1', 'Agent v2'])
            ax.legend()

            ax.annotate(f'{v1_mean:.2f} ± {v1_std:.2f}s',
                        xy=(rects1[0].get_x() + rects1[0].get_width() / 2,
                            v1_mean),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')
            ax.annotate(f'{v2_mean:.2f} ± {v2_std:.2f}s',
                        xy=(rects2[0].get_x() + rects2[0].get_width() / 2,
                            v2_mean),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig(
                os.path.join(self.config["results_dir"],
                             "response_time_comparison.png")
            )
            plt.close()


def main():
    """Main function to run the evaluation and generate reports."""
    print("GitHub Copilot Agent Evaluation")
    print("=" * 50)

    try:
        evaluator = AgentEvaluator(CONFIG)

        print("\n[START] Starting evaluation...")
        start_time = time.time()
        evaluator.run_evaluation()

        print("\n[REPORT] Generating report...")
        evaluator.generate_report()

        duration = time.time() - start_time
        print(f"\n[DONE] Evaluation completed in {duration:.1f} seconds!")
        print(
            "[RESULTS] Report and results saved to: "
            f"{os.path.abspath(CONFIG['results_dir'])}"
        )

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Evaluation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {str(e)}")
        logging.exception("Evaluation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
