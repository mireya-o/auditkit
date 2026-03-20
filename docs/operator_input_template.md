Product name: Support Review Surface for a regulated fintech.

Purpose:
- Help customer support agents draft responses and retrieve relevant policy/knowledge-base information.
- Summarize tickets and propose next actions for agents (human approval required).

Users:
- Internal customer support agents and team leads.
- Compliance team reviews policies and risk controls.

Data:
- Inputs may include customer messages, account metadata, and personal data (PII).
- Outputs are draft replies, internal summaries, and suggested resolutions (never sent automatically).

Deployment:
- Internal web app accessible to authenticated employees only.
- Logs and audit trails are required.
- The system uses retrieval over approved internal documents (policies, procedures, FAQs).

AI behavior:
- Must cite sources when answering policy questions.
- Must refuse requests that involve illegal actions, sensitive data exfiltration, or bypassing controls.
- Must not fabricate policy statements; if context is insufficient, it must say so.

Constraints:
- Human-in-the-loop is mandatory (no autonomous actions).
- Security: prompt injection, data leakage, and unsafe tool use must be mitigated and tested.
