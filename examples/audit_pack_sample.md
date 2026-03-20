# Audit Pack — Support Review Surface for Regulated Fintech

> This audit pack is for internal use only and does not constitute legal or regulatory advice.

## System Card
- **Summary:** AI‑assisted drafting and retrieval tool for customer support agents, with mandatory human approval.
- **Intended use:**
  - Draft agent responses
  - Retrieve policy/KB info
  - Summarize tickets
- **Out of scope:**
  - Automated customer communication
  - External data ingestion
- **Users:**
  - Internal support agents
  - Team leads
  - Compliance team
- **Data inputs:**
  - Customer messages
  - Account metadata
  - PII
- **Data outputs:**
  - Draft replies
  - Internal summaries
  - Suggested actions
- **Deployment:** Authenticated internal web app with audit logging
- **Assumptions:**
  - All users are authenticated
  - Data stays within corporate network
- **Limitations:**
  - No autonomous actions
  - Limited to approved documents
- **Human oversight:**
  - Agents must approve all outputs

## Risk Register
### R1 — Data Leakage (Security) [S1]
- **Threat:** Unintentional PII exposure via model output [S1]
- **Impact:** High [S1]
- **Likelihood:** Medium
- **Severity:** High
- **Controls:**
  - Prompt sanitization [S1]
  - Output filtering [S1]
- **Tests:**
  - Leakage test with synthetic PII [S1]

### R2 — Prompt Injection (Security) [S1]
- **Threat:** Adversary manipulates model behavior [S1]
- **Impact:** High [S1]
- **Likelihood:** Medium
- **Severity:** High
- **Controls:**
  - Input validation [S1]
  - Sandboxed execution [S1]
- **Tests:**
  - Injection resilience test [S1]

### R3 — Policy Fabrication (Reliability) [S1]
- **Threat:** Model generates incorrect policy statements [S1]
- **Impact:** Medium [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Source citation requirement [S1]
- **Tests:**
  - Citation accuracy test [S1]

### R4 — Compliance Gap (Compliance) [S2]
- **Threat:** Non‑adherence to EU AI Act high‑risk requirements [S2]
- **Impact:** High [S2]
- **Likelihood:** Low
- **Severity:** High
- **Controls:**
  - Regulatory mapping [S2]
  - Audit trail [S2]
- **Tests:**
  - Compliance audit simulation [S2]

### R5 — Unauthorized Access (Security) [S1]
- **Threat:** Insider misuse of system [S1]
- **Impact:** High [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Role‑based access control [S1]
  - Activity monitoring [S1]
- **Tests:**
  - RBAC penetration test [S1]

### R6 — Model Bias (Privacy) [S1]
- **Threat:** Unequal treatment in support responses [S1]
- **Impact:** Medium [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Bias monitoring [S1]
- **Tests:**
  - Fairness audit [S1]

### R7 — Operational Downtime (Operations) [S1]
- **Threat:** Service interruption affecting support [S1]
- **Impact:** High [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Redundancy [S1]
  - Health checks [S1]
- **Tests:**
  - Failover test [S1]

### R8 — Tool Misuse (Abuse) [S1]
- **Threat:** Model used to execute malicious commands [S1]
- **Impact:** High [S1]
- **Likelihood:** Low
- **Severity:** High
- **Controls:**
  - Tool access restriction [S1]
- **Tests:**
  - Command execution test [S1]

### R9 — Audit Trail Tampering (Security) [S1]
- **Threat:** Alteration of logs to hide incidents [S1]
- **Impact:** High [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Immutable logging [S1]
- **Tests:**
  - Log integrity test [S1]

### R10 — Data Retention Violation (Compliance) [S1]
- **Threat:** Storing PII beyond allowed period [S1]
- **Impact:** High [S1]
- **Likelihood:** Low
- **Severity:** Medium
- **Controls:**
  - Retention policy enforcement [S1]
- **Tests:**
  - Retention audit [S1]

## OWASP LLM Top 10 Mapping (2025)
### R2 [S1]
- **Recommended controls:**
  - Input validation [S1]
  - Output filtering [S1]
- **Tests:**
  - Injection resilience test [S1]

### R1 [S1]
- **Recommended controls:**
  - Prompt sanitization [S1]
  - Output filtering [S1]
- **Tests:**
  - Leakage test with synthetic PII [S1]

### R8 [S1]
- **Recommended controls:**
  - Tool access restriction [S1]
- **Tests:**
  - Command execution test [S1]

### R3 [S1]
- **Recommended controls:**
  - Source citation requirement [S1]
- **Tests:**
  - Citation accuracy test [S1]

### R4 [S2]
- **Recommended controls:**
  - Regulatory mapping [S2]
  - Audit trail [S2]
- **Tests:**
  - Compliance audit simulation [S2]

### R5 [S1]
- **Recommended controls:**
  - RBAC [S1]
  - Activity monitoring [S1]
- **Tests:**
  - RBAC penetration test [S1]

### R6 [S1]
- **Recommended controls:**
  - Bias monitoring [S1]
- **Tests:**
  - Fairness audit [S1]

### R7 [S1]
- **Recommended controls:**
  - Redundancy [S1]
  - Health checks [S1]
- **Tests:**
  - Failover test [S1]

### R9 [S1]
- **Recommended controls:**
  - Immutable logging [S1]
- **Tests:**
  - Log integrity test [S1]

### R10 [S1]
- **Recommended controls:**
  - Retention policy enforcement [S1]
- **Tests:**
  - Retention audit [S1]

## NIST Mapping (AI RMF functions)
### GOVERN [S1]
- Define AI governance framework [S1]

### MAP [S1]
- Map risks to controls [S1]

### MEASURE [S1]
- Assess control effectiveness [S1]

### MANAGE [S1]
- Continuous monitoring and improvement [S1]

## EU AI Act Timeline (selected milestones)
- **02 Feb 2025 — General provisions apply:** All AI systems must comply with basic definitions and prohibitions [S2]
- **02 Aug 2025 — Rules for general‑purpose AI apply:** Providers must establish governance and risk management [S2]
- **02 Aug 2027 — High‑risk AI rules apply to regulated products:** Support Review Surface must meet high‑risk compliance if classified as such [S4]

## Operational Checklist
### Pre-release
- Verify source citation logic
- Test refusal for illegal requests
- Validate prompt injection defenses
- Confirm audit trail logging
- Ensure human‑in‑the‑loop workflow

### Post-release
- Conduct periodic security scans
- Review audit logs weekly
- Update threat model annually
- Maintain SBOM for AI components
- Audit compliance with EU AI Act

### Monitoring
- Track model drift metrics
- Monitor for policy violations in outputs
- Log all user interactions
- Alert on anomalous request patterns
- Review model performance quarterly

### Incident response
- Activate incident playbook for data leakage
- Notify compliance team immediately
- Contain affected sessions
- Perform root cause analysis
- Document remediation steps

## Sources (snippets used)
- [S1] nist_ir_8596_cyber_ai_profile_iprd.pdf p83 — NIST IR 8596 irpd (Initial Preliminary Draft) Cybersecurity AI Profile December 2025 NIST Community Profile 74 CSF 2.0 Core: DETECT General Considerations Focus Area Proposed Priorities & Considerations Secure Defend Thwart References pe...
- [S2] eu_ai_act_timeline_implementation.pdf p1 — AI Act Service Desk Timeline for theImplementation of the EU AIAct The EU's AI Act legislation applies progressively, with a full roll-out foreseen by 2 August 2027. 02 Feb 2025 General provisions (definitions & AI literacy) and prohibit...
- [S4] eu_ai_act_timeline_implementation.pdf p2 — 02 Aug 2027 Rules for high-risk AI embedded in regulated products apply ** ** In the context of the Digital Omnibus package, the Commission has proposed linking the application of rules governing high-risk AI systems to the availability...
