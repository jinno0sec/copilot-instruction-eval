# Python Code Review Automation with GitHub Copilot

This repository is dedicated to researching and developing methods for automating Python code reviews using the official GitHub Copilot CLI.

**Note:** The principles, architecture, and rules governing this repository are strictly defined in [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md). This README serves as a practical guide for setup and usage, but `SYSTEM_CONSTITUTION.md` is the supreme source of truth.

## 🎯 Project Purpose

The single purpose of this repository is: **To research, develop, and evaluate methods for automating Python code reviews using the GitHub Copilot family of tools.**

The primary output is runnable proof-of-concept scripts and technical documentation that validate effective automation strategies. Production-grade services are explicitly out of scope.

## 🏛️ Architecture & Core Technology

This project operates on a few key principles:

*   **Core Tool:** The **sole approved technology** for automation is the official NPM package: **`@github/copilot`**. The use of GUI automation or deprecated tools is strictly forbidden. For more details, see [`COPILOT_CLI_UPDATE.md`](COPILOT_CLI_UPDATE.md).
*   **Dual Stack:** The project uses a hybrid environment:
    *   **Python:** For scripting, orchestration, and analysis. Dependencies are managed in `requirements.txt`.
    *   **Node.js:** Required for the `@github/copilot` tool itself. Dependencies are managed in `package.json`.
*   **Directory Structure:**
    *   `/`: Contains primary, runnable automation scripts and key documentation.
    *   `/code/`: Contains sample Python code intended for review by the automation scripts.
    *   `/results/`: Contains output artifacts from evaluation runs (e.g., `.json`, `.md` reports).
    *   `/archive/`: Contains deprecated, non-functional, or historical scripts.

## 🚀 Quick Start

### 1. Prerequisites

*   Python (version 3.10+ recommended)
*   Node.js (version 22+ recommended)
*   An active GitHub Copilot subscription.

### 2. Installation

```bash
# 1. Clone the repository
git clone <repository_url>
cd <repository_name>

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node.js dependencies (for tooling)
npm install

```

### 3. Authentication

Before first use, you must authenticate the Copilot CLI with your GitHub account.

```bash
# After running `npm install`, the Copilot CLI is available locally.
# Start the interactive Copilot CLI using npx
npx copilot

# Inside the Copilot prompt, log in
> /login
```
Follow the on-screen instructions to authorize the device.

## 💻 Usage

The primary script, `copilot_cli_new_automation.py`, now fully automates the code review process.

### Automated Code Review

On Unix-like systems (Linux, macOS), you can run the end-to-end automated review with a single command.

```bash
# Run the fully automated code review script
python copilot_cli_new_automation.py
```

The script will:
1.  Read the sample code from `/code/sample.py`.
2.  Interact with the GitHub Copilot CLI to perform a code review.
3.  Save the complete review results to `/results/review_result.json`.
4.  Display a summary of the review in the console.

### Manual Mode on Windows

Due to technical limitations, the automated interaction is not supported on Windows. The script will detect the OS and, on Windows, provide guidance for running the review manually.

## 📚 Canonical Documents

The following documents are the official sources of truth for the project:

*   [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md): The supreme law of the repository.
*   [`README.md`](README.md) (This file): The entry point for understanding WHAT the project is and HOW to use it.
*   [`COPILOT_CLI_UPDATE.md`](COPILOT_CLI_UPDATE.md): The canonical reference for the core `@github/copilot` tool.
*   [`TECHNICAL_VERIFICATION.md`](TECHNICAL_VERIFICATION.md): The historical record of technical decisions and rejected alternatives.
