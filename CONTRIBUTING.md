# Contributing to this Project

Thank you for your interest in contributing! All contributions must align with the foundational rules and principles set forth in our [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md). This document provides a practical guide for developers.

## 📜 Core Principles

Before you begin, please familiarize yourself with the constitution. Key principles include:

-   **Purpose**: We exist solely to research and evaluate Python code review automation using GitHub Copilot tools.
-   **Evidence-Based Changes**: All technical decisions must be backed by evidence (e.g., execution proof, official documentation). No speculative changes.
-   **Core Technology**: The **only** approved tool for automation is the `@github/copilot` NPM package. GUI automation is forbidden.

## 🚀 How to Contribute

We follow a standard GitHub flow for contributions.

### 1. Branching Strategy

-   Create a new branch for every new feature, bugfix, or documentation update.
-   Branch names should be descriptive and use kebab-case (e.g., `feature/update-readme`, `fix/resolve-dependency-issue`).
-   Branches should be based on the `main` branch.

### 2. Making Changes

-   Ensure all code is runnable and tested.
-   Follow the existing code style. (Note: Linters will be enforced via CI in the future).
-   Update relevant documentation if your changes affect usage, architecture, or setup.

### 3. Commit Messages

Commit messages MUST follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This helps maintain a clear and automated version history.

-   **Format**: `type(scope): subject`
-   **Example `feat`**: `feat(automation): add new script for parsing review feedback`
-   **Example `fix`**: `fix(deps): pin dependency to resolve compatibility issue`
-   **Example `docs`**: `docs(contributing): create initial contributing guidelines`
-   **Allowed types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

### 4. Submitting a Pull Request (PR)

1.  **Create the PR**: Push your branch to the repository and open a pull request against the `main` branch.
2.  **Title and Description**:
    -   The PR title should be clear and concise.
    -   The description MUST explain the "what" and "why" of your changes.
    -   If your change is based on a new tool or major architectural shift, you MUST include an "Evidence Summary" as required by Section 3 of the constitution.
3.  **Compliance Check**: Ensure your PR adheres to all "MUST" / "MUST NOT" rules in [`SYSTEM_CONSTITUTION.md`](SYSTEM_CONSTITUTION.md).
4.  **Review**: A repository maintainer will review your PR. Any PR that violates the constitution will be rejected.

## ✅ Definition of Done

A PR is considered "Done" only when it:
-   Complies with the constitution.
-   Has been tested by the author.
-   Includes necessary documentation updates.
-   (Future) Passes all CI checks.

By contributing, you agree that your contributions will be licensed under the MIT License that covers the project.
