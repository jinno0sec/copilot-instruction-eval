# SYSTEM_CONSTITUTION.md

## 0. Scope & Enforcement (適用範囲と強制)

### 0.1 Scope
This constitution applies to all content within this repository, including but not limited to:
- All source code (e.g., `.py`, `.js`, `.ts` files).
- All configuration files (e.g., `package.json`, `requirements.txt`).
- All documentation (e.g., `.md` files).
- All automation scripts and CI/CD configurations.
- All contributions made by human developers or automated AI agents.

### 0.2 Precedence
If any conflict arises between this document and any other document or convention in the repository (e.g., `README.md`, `CONTRIBUTING.md`), **this SYSTEM_CONSTITUTION.md shall always take precedence**.

### 0.3 Enforcement
- **Automated Checks**: Where possible, rules will be enforced via a CI pipeline (e.g., GitHub Actions). The following checks MUST be implemented:
  - **Python Linting**: Using `flake8`.
  - **Python Testing**: Using `pytest`.
  - **Dependency Vulnerability Scanning**: Using `pip-audit` and `npm audit`.
- **Mandatory Review**: All pull requests (PRs) MUST be reviewed for compliance with this constitution.
- **Invalidity Clause**: Any PR that violates a "MUST" or "MUST NOT" rule defined herein is considered invalid and **MUST NOT be merged**.

## 1. Purpose (目的)

### 1.1 This repo exists to do (存在理由)
This repository exists for a single purpose: **To research, develop, and evaluate methods for automating Python code reviews using the GitHub Copilot family of tools.**
The primary output of this repository is runnable proof-of-concept scripts and technical documentation that validate effective automation strategies.

### 1.2 This repo must not do (やらないこと)
This repository MUST NOT be used to:
- Develop production-grade services or libraries.
- Host code unrelated to the evaluation of code review automation.
- Implement automation techniques explicitly rejected in `TECHNICAL_VERIFICATION.md` (e.g., Playwright for VS Code UI automation).

### 1.3 Rejection of Out-of-Scope PRs
Any PR whose primary purpose does not align with section 1.1 WILL be rejected.

## 2. Non-Negotiables (絶対制約)

### 2.1 Security & Privacy
- **No Secrets**: Secrets (API keys, tokens, credentials) MUST NOT be committed to the repository, even temporarily. Use environment variables or a secure vault system. The `.env.example` file is the template for required variables.
- **Dependency Security**: Dependencies listed in `requirements.txt` and `package.json` MUST be periodically scanned for known vulnerabilities using `pip-audit` and `npm audit` respectively as part of the CI process.

### 2.2 Reliability & Safety
- **Runnable Code**: All scripts in the root directory MUST be runnable. Non-functional or purely conceptual code (like the original `copilot_gui_poc.py`) MUST be placed in an `archive/` or `deprecated/` directory.
- **No Destructive Operations**: Scripts MUST NOT perform destructive operations on the local environment or external services without explicit user confirmation.

### 2.3 Reproducibility & Auditability
- **Dependency Pinning**: All direct dependencies in `requirements.txt` and `package.json` SHOULD be pinned to specific versions to ensure reproducible environments.
- **Traceable Changes**: All code changes MUST be associated with a descriptive commit message that explains the "what" and "why" of the change.

## 3. Evidence-Based Change Rule (ノー推測ルール)

### 3.1 Evidence Before Change
All significant technical decisions or changes MUST be supported by evidence. Evidence includes:
- **Execution Proof**: Scripts or commands that successfully run and produce verifiable output.
- **Reference to Official Documentation**: Links to documentation confirming the feasibility of an approach (as seen in `COPILOT_CLI_UPDATE.md`).
- **Prior Art**: Links to existing implementations or technical articles.

### 3.2 Evidence Summary in PRs
All PRs introducing a new tool, dependency, or architectural pattern MUST include a brief "Evidence Summary" in the PR description, justifying the change based on the criteria in 3.1.

### 3.3 Rejection of Speculative Changes
PRs based on unverified assumptions or "it might work" logic are subject to immediate rejection. All work must be grounded in the reality of the tools, as documented in `TECHNICAL_VERIFICATION.md`.

## 4. Architecture Boundaries & Invariants (境界と不変条件)

### 4.1 Core Technology Invariant
- The **sole approved technology** for interacting with GitHub Copilot for code review automation is the official NPM package: **`@github/copilot`**.
- The use of the deprecated `gh copilot` extension or any form of GUI automation (e.g., Playwright, pyautogui) for this purpose is **strictly forbidden** for any new development. This is based on the conclusive findings in `TECHNICAL_VERIFICATION.md` and `COPILOT_CLI_UPDATE.md`.

### 4.2 Directory Boundaries
- **/ (root)**: Contains primary, runnable automation scripts (e.g., `copilot_cli_new_automation.py`) and key documentation.
- **/code/**: Contains sample Python code intended for review by the automation scripts. It MUST NOT contain automation logic.
- **/results/**: Contains output artifacts from evaluation runs, such as `.json` or `.md` reports. It MUST NOT contain source code.
- **/archive/ (TBD)**: A directory for deprecated or non-functional scripts. This should be created if needed.

### 4.3 Dependency & Environment
- **Dual Stack Environment**: This project requires both **Python (for scripting) and Node.js (for `@github/copilot`)**. Both environments are considered first-class.
- **Python Dependencies**: Managed via `requirements.txt`.
- **Node.js Dependencies**: Managed via `package.json`.

## 5. Definition of Done / Quality Gates (完了定義)

A PR is considered "Done" and ready to merge only when it meets all the following criteria:
- [ ] It fully complies with all "MUST" / "MUST NOT" rules in this constitution.
- [ ] All new or modified scripts (`.py`) are runnable and have been tested by the author.
- [ ] It includes an "Evidence Summary" if required by section 3.2.
- [ ] It updates relevant documentation (`README.md`, etc.) if the change impacts usage or technical direction.
- [ ] All automated CI checks (linting, testing, vulnerability scanning) must pass.

## 6. Decision System (トレードオフと優先順位)

When making technical decisions, the following priorities MUST be followed, in order:
1.  **Correctness & Reproducibility**: The solution must work reliably and be reproducible by others.
2.  **Simplicity & Maintainability**: Prefer the simplest possible solution that meets the requirements. Use official, stable tools over complex, brittle workarounds.
3.  **Automation Level**: Prefer fully automatable, command-line solutions over those requiring manual intervention.
4.  **Performance**: Performance is not a primary concern for this research project.

The guiding principle is **YAGNI (You Ain't Gonna Need It)**. Do not implement features or abstractions not immediately required for the task at hand.

## 7. Governance & Exceptions (統治と例外)

### 7.1 Exception Process
No exceptions to this constitution are permitted unless they follow this explicit process:
1.  **Create an Issue**: An issue must be created to propose the exception, detailing the rule to be bypassed and the justification.
2.  **Provide Evidence**: The proposal must include strong evidence (as per Section 3) for why the exception is necessary.
3.  **Maintainer Approval**: The exception must be explicitly approved by a repository maintainer, as defined in [`MAINTAINERS.md`](MAINTAINERS.md).
4.  **Document in PR**: The approved issue number MUST be referenced in the PR that implements the exception.

### 7.2 High-Risk Areas
There are currently no high-risk areas like payments or PII. However, any change related to authentication with GitHub services is considered sensitive and requires careful review.

## 8. Canonical Documents (正典ドキュメント)

The following documents serve as the official sources of truth for their respective areas:
- **`SYSTEM_CONSTITUTION.md` (This file)**: The supreme law of the repository.
- **`README.md`**: The primary entry point for understanding WHAT the project is and HOW to use it.
- **`CONTRIBUTING.md`**: Practical guidelines and workflow for contributors.
- **`COPILOT_CLI_UPDATE.md`**: The canonical reference for the core `@github/copilot` tool.
- **`TECHNICAL_VERIFICATION.md`**: The historical record of technical decisions and rejected alternatives.

No other document can override the rules established in this constitution.
