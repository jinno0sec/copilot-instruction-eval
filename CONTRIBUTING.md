# Contributing to this Project

Thank you for your interest in contributing! All contributions must align with the foundational principles and rules set forth in our governing document, [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md). This document provides practical guidelines to help you get started.

## 🏛️ Guiding Principle: The Constitution is Law

Before making any changes, you **must** read and understand [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md). It is the supreme source of truth for this repository, and all contributions will be reviewed for strict compliance.

## 🚀 Development Workflow

1.  **Set Up Your Environment**: Follow the installation instructions in the [`README.md`](README.md) to set up the necessary Python and Node.js environments.
    ```bash
    # Install Python dependencies
    pip install -r requirements.txt

    # Install Node.js tooling dependencies
    npm install
    ```

2.  **Create a Branch**: Create a new branch for your feature or bugfix.
    ```bash
    git checkout -b your-branch-name
    ```

3.  **Make Your Changes**:
    *   Ensure your code adheres to the architectural boundaries defined in the constitution (e.g., automation logic in the root, sample code in `/code`).
    *   Remember the **Evidence-Based Change Rule** (Constitution, Section 3). Any new dependencies, tools, or significant architectural changes must be supported by verifiable evidence.

4.  **Ensure Code Quality**:
    *   **Linting**: Ensure your Python code is compliant with `flake8`.
        ```bash
        flake8 .
        ```
    *   **Testing**: Run the existing tests to ensure you haven't introduced any regressions.
        ```bash
        pytest
        ```

5.  **Write Clear Commit Messages**: Your commit messages must be descriptive and explain the "what" and the "why" of your change, as required by the constitution (Section 2.3).

    *   **Good Example**:
        ```
        feat: Add rouge score to evaluation metrics

        Adds the ROUGE score calculation to the AgentEvaluator to provide a more comprehensive comparison of text generation quality between agents. This aligns with our goal of robust, evidence-based evaluation.
        ```
    *   **Bad Example**:
        ```
        fix: script update
        ```

6.  **Submit a Pull Request (PR)**: Push your branch to the repository and create a Pull Request.

## ✅ Pull Request Requirements

A PR will only be considered for merge if it meets the **Definition of Done** (Constitution, Section 5). This includes:

*   [ ] **Constitutional Compliance**: The PR fully complies with all "MUST" / "MUST NOT" rules.
*   [ ] **Runnable Code**: All new or modified scripts are runnable and have been tested.
*   [ ] **Evidence Summary (if applicable)**: If you are introducing a new tool, dependency, or major architectural change, your PR description **must** include an "Evidence Summary" as required by the constitution (Section 3.2). This summary should justify the change with links to documentation, execution proof, or other evidence.
*   [ ] **Updated Documentation**: If your change affects how the project is used or its technical direction, you must update the `README.md` or other relevant documentation.
*   [ ] **Passing CI Checks**: All automated checks (linting, testing, vulnerability scans) must pass. (Note: CI is TBD).

By contributing, you agree that your work will be licensed under the MIT License of this project.
