## 2025-12-21 - I/O Optimization vs. Fault Tolerance

**Learning:** When optimizing I/O operations by removing incremental saves from a loop, I introduced a critical regression. The original code, while slow, was fault-tolerant; an interruption would only cause the loss of the current item's data. My optimization to save only at the end made the entire process vulnerable—any failure before completion would result in the loss of all data.

**Action:** For long-running processes, never remove incremental saving entirely. Instead, implement a periodic save (e.g., every N iterations) to balance performance gains with data safety. This provides a robust compromise, ensuring that most progress is preserved in case of failure while still significantly reducing I/O overhead.
