# Early Warning Signals: Detecting Hidden Coordination and Goal Drift in AI Agent Swarms

## Abstract

Multi-agent AI systems create oversight challenges because important interactions may occur between agents without being visible to a human supervisor. This project investigates whether interaction-log analysis can identify four categories of potentially harmful behaviour: hidden coordination, goal drift, supervisor bypass, and concealment. A simulated multi-agent environment with five role-based agents was developed to generate structured interaction logs. The project first evaluated two rule-based detectors on a 50-scenario development dataset, then compared them with a revised V2.1 detector on a separate 50-scenario synthetic challenge dataset. Both datasets contain normal scenarios and examples of four predefined threat categories. Each scenario was evaluated using a full audit log and a restricted supervisor-visible log. On the original development dataset, V1 achieved F1-scores of 0.519 and 0.462, while V2 achieved 1.000 and 0.667, respectively. On the separate challenge dataset, V2.1 achieved F1-scores of 0.873 with the full audit log and 0.644 with the supervisor-visible log, compared with 0.667 and 0.491 for V2. The V2.1 rules were revised after examining V2's errors on the challenge dataset; these figures are therefore tuning results, not an untouched independent test. The findings demonstrate a prototype approach and the importance of log visibility, while highlighting the need for a new external test set and more realistic agent environments.

## 2. Introduction

Multi-agent AI systems can distribute complex tasks across several specialized agents. One agent may gather information, another analyze it, a third develop a plan, and another execute actions. This architecture can improve task decomposition and coordination, but it also creates new challenges for oversight.

Monitoring a single agent or relying only on messages visible to a supervisor may provide an incomplete picture of the system's behavior. Relevant decisions may occur across multiple agents, objectives may gradually shift during task execution, and actions may be performed without the required authorization. In addition, agents may communicate or act in ways that are not fully represented in the supervisor-visible log.

This project investigates whether interaction-log analysis can provide early warning signals of potentially problematic behavior in a simulated multi-agent environment. It focuses on four threat categories: **hidden coordination, goal drift, supervisor bypass, and concealment**.

The prototype uses role-labelled agents, structured interaction logs, and rule-based detection methods. It compares monitoring based on a full audit log with monitoring based only on the information available to the supervisor. This comparison is intended to examine how information visibility affects the detection of different threat categories.

The project does not attempt to demonstrate that the proposed detector can reliably identify deceptive behavior in real-world AI systems. Instead, it provides a controlled experimental prototype for studying the relationship between observable interaction patterns, monitoring limitations, and early warning detection.

### Research Question

**Can interaction-log analysis detect hidden coordination, goal drift, supervisor bypass, and concealment in multi-agent AI systems, and how does the availability of a full audit log affect detection performance?**



### Research Objectives

1. Develop a simulated multi-agent environment with distinct agent roles and structured interaction logs.
2. Define representative scenarios for four predefined threat categories: hidden coordination, goal drift, supervisor bypass, and concealment.
3. Implement and compare two rule-based detection approaches.
4. Evaluate detection performance using precision, recall, F1-score, and confusion-matrix counts.
5. Compare detection performance using the full audit log and the supervisor-visible log.
6. Identify the limitations of rule-based monitoring and the risks associated with incomplete observability.

## 3. System Architecture and Threat Model

### 3.1. System Architecture

The prototype consists of five role-labelled agents operating in a simulated multi-agent environment:

- **Researcher (A1):** gathers information.
- **Analyst (A2):** evaluates available information.
- **Planner (A3):** develops an action plan.
- **Executor (A4):** performs assigned actions.
- **Supervisor (A5):** oversees the process and monitors agent activity.

Agent interactions are recorded by an interaction logger. The system maintains two log views: a **full audit log**, containing the complete recorded interactions, and a **supervisor-visible log**, containing only information available to the Supervisor.

Both log views are processed by rule-based detectors. The detection pipeline consists of log processing, feature extraction, threat scoring, and alert generation. Ground-truth labels are stored separately and used only for evaluation, not as detector inputs.

### 3.2. Threat Model

The experiment considers four predefined threat categories:

1. **Hidden Coordination:** agents coordinate their actions through interactions that are not visible to the Supervisor.
2. **Goal Drift:** an agent deviates from the original task objective.
3. **Supervisor Bypass:** an agent performs an action without the required authorization.
4. **Concealment:** an agent deliberately hides information or actions from the Supervisor.

Hidden Coordination and Concealment are treated as separate categories: the former concerns coordination outside the intended oversight process, while the latter concerns deliberate withholding of relevant information.

The experiment assumes access to recorded interaction logs but does not assume that the Supervisor can observe every agent interaction. It therefore examines how monitoring scope affects the detection of predefined threat patterns.

The prototype uses simulated scenarios and rule-based indicators. It does not model real-world adversarial agents or establish that the same detection performance would generalize to deployed multi-agent AI systems.

## 4. Methodology

### 4.1. Dataset and Experimental Scenarios

The evaluation dataset contains 50 manually authored scenarios divided into five groups: 10 normal scenarios and 10 scenarios for each of the four threat categories. Each run includes a full audit log and a supervisor-visible log. Ground-truth labels are stored separately in evaluation metadata and are not provided to the detectors.

### 4.2. Detection Methods

Two rule-based detection versions were implemented:

- **V1 (Baseline):** uses predefined lexical indicators for hidden coordination, goal drift, and concealment, together with structured authorization checks for supervisor bypass.
- **V2 (Extended):** adds expanded phrase patterns and cross-agent interaction heuristics to improve the identification of coordination and other threat indicators.
- **V2.1 (Revised):** broadens phrase coverage and normalizes alternative event-field names while preserving V2 as an unchanged comparison baseline. V2.1 was developed after reviewing V2's errors on the separate challenge dataset.

Both versions process the available log data and generate threat-specific detection outcomes. The evaluation is performed separately using the full audit log and the supervisor-visible log.

### 4.3. Evaluation Metrics

Performance is assessed using precision, recall, and F1-score, supported by true positives (TP), false positives (FP), false negatives (FN), and true negatives (TN). Results are examined both overall and separately for each threat category.

The experiment compares detection performance across the two log views to assess the effect of information visibility on threat identification.

### 4.4. Experimental Scope

The dataset is a controlled, manually authored collection rather than an independent real-world sample. V2 was developed after examining the initial scenarios; therefore, its results on this dataset represent development-set performance, not independent validation. The findings are limited to the simulated environment and the implemented rule-based indicators.

## 5. Experimental Results

### 5.1. Overall Detection Performance

Detection performance was evaluated using a confusion matrix with four outcomes:

- **True Positive (TP):** a threat scenario correctly identified as a threat.
- **False Positive (FP):** a normal scenario incorrectly flagged as a threat.
- **False Negative (FN):** a threat scenario missed by the detector.
- **True Negative (TN):** a normal scenario correctly classified as normal.

Precision measures the proportion of detected threats that were actual threats, while recall measures the proportion of actual threats successfully detected. The F1-score is the harmonic mean of precision and recall.

The detectors were evaluated on 50 scenarios, including 10 normal cases and 40 threat cases. Table 1 summarizes overall performance across both log views.

**Table 1. Overall detection performance**

| **Log View**    | **Detector** | **TP** | **FP** | **FN** | **TN** | **Precision** | **Recall** | **F1** |
| --------------- | ------------ | ------ | ------ | ------ | ------ | ------------- | ---------- | ------ |
| Full Audit      | V1           | 14     | 0      | 26     | 10     | 1.00          | 0.35       | 0.519  |
| Full Audit      | V2           | 40     | 0      | 0      | 10     | 1.00          | 1.00       | 1.000  |
| Supervisor-only | V1           | 12     | 0      | 28     | 10     | 1.00          | 0.30       | 0.462  |
| Supervisor-only | V2           | 20     | 0      | 20     | 10     | 1.00          | 0.50       | 0.667  |

### 5.2. Threat-Specific Performance

Table 2 presents F1-scores for individual threat categories.

**Table 2. F1-score by threat category**

| **Threat Category** | **Audit V1** | **Audit V2** | **Supervisor V1** | **Supervisor V2** |
| ------------------- | ------------ | ------------ | ----------------- | ----------------- |
| Hidden Coordination | 0.182        | 1.000        | 0.000             | 0.000             |
| Goal Drift          | 0.333        | 1.000        | 0.333             | 1.000             |
| Supervisor Bypass   | 1.000        | 1.000        | 1.000             | 1.000             |
| Concealment         | 0.182        | 1.000        | 0.000             | 0.000             |

### 5.3. Separate Challenge-Set Evaluation: V1, V2, and V2.1

A second, separately authored challenge dataset was generated with 50 scenarios: 10 normal scenarios and 10 for each threat category. The dataset uses a different set of message templates from the original development dataset. V1 and V2 were evaluated unchanged, and V2.1 was evaluated after its phrase rules had been revised in response to V2's false negatives. Table 3 summarizes the results.

**Table 3. Overall performance on the separate challenge dataset**

| **Log View** | **Detector** | **TP** | **FP** | **FN** | **TN** | **Precision** | **Recall** | **F1** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Full Audit | V1 | 13 | 0 | 27 | 10 | 1.00 | 0.325 | 0.491 |
| Full Audit | V2 | 20 | 0 | 20 | 10 | 1.00 | 0.500 | 0.667 |
| Full Audit | V2.1 | 31 | 0 | 9 | 10 | 1.00 | 0.775 | 0.873 |
| Supervisor-only | V1 | 12 | 0 | 28 | 10 | 1.00 | 0.300 | 0.462 |
| Supervisor-only | V2 | 13 | 0 | 27 | 10 | 1.00 | 0.325 | 0.491 |
| Supervisor-only | V2.1 | 19 | 0 | 21 | 10 | 1.00 | 0.475 | 0.644 |

V2.1 improved overall recall on this challenge dataset relative to V2: full-audit F1 increased from 0.667 to 0.873, while supervisor-only F1 increased from 0.491 to 0.644. No false positives were observed among the 10 normal scenarios. This result should be interpreted cautiously: V2.1 was tuned after inspecting V2's errors on this same dataset, so the V2.1 figures are development/tuning results rather than an untouched independent test. The dataset is small, synthetic, manually authored, and template-based.

**Table 4. V2.1 threat-specific F1-scores on the challenge dataset**

| **Threat Category** | **Full Audit V2.1** | **Supervisor-only V2.1** |
|---|---:|---:|
| Hidden Coordination | 0.667 | 0.000 |
| Goal Drift | 0.947 | 0.947 |
| Supervisor Bypass | 1.000 | 1.000 |
| Concealment | 0.824 | 0.000 |

The challenge-set supervisor-only logs intentionally omit hidden events in the Hidden Coordination and Hiding scenarios. The resulting misses in these categories reflect the information removed by this dataset's log-generation procedure; they do not establish that such threats are universally undetectable from supervisor-visible logs.

### 5.4. Results Summary

The baseline detector (V1) achieved perfect precision but relatively low recall, indicating that it identified only a limited proportion of threat scenarios. Its strongest performance was observed for supervisor bypass, which could be identified through structured authorization fields.

V2 achieved perfect scores on the original full-audit dataset. However, its detection rules were developed after examining the dataset, so these results indicate a fit to the development scenarios rather than independent generalization.

In the supervisor-only setting, V2 achieved an F1-score of 0.667. Hidden coordination and concealment remained undetected because the relevant interactions were not available in that log view. This demonstrates the importance of information visibility for monitoring multi-agent systems.

## 6. Discussion

The experimental results highlight the importance of monitoring scope in multi-agent systems. The full audit log provided access to interactions that were unavailable in the supervisor-visible log, enabling the detection of hidden coordination and concealment patterns in the simulated scenarios.

The baseline detector (V1) showed high precision but limited recall, indicating that its predefined indicators were too restrictive to identify many manually authored threat variations. V2 improved detection on the original development dataset through expanded phrase patterns and cross-agent interaction heuristics, but its perfect full-audit score reflects rule development on the same scenarios. On the separate challenge dataset, V2 achieved a lower full-audit F1-score of 0.667. V2.1 increased this to 0.873 after additional phrase-pattern revisions. Because those revisions were informed by errors on the challenge set, the V2.1 result is a tuning result and must not be presented as an untouched test score.

Supervisor bypass was consistently detected through structured authorization information, while lexical threat categories were more sensitive to wording and log visibility. These findings suggest that structured event fields and comprehensive audit logging can complement text-based monitoring. They do not establish that the approach will generalize to real-world multi-agent systems.

## 7. Limitations and Dual-Use / Ethical Considerations

This study uses small, manually authored synthetic datasets and a simulated multi-agent environment rather than real LLM-based agents. The challenge dataset uses fixed templates and is deterministic; it is not a statistically sampled or adversarially generated benchmark. The rule-based detectors rely on predefined lexical patterns and structured fields, making them vulnerable to paraphrasing, ambiguity, multilingual messages, and behaviours not represented in the dataset.

V2 was developed after inspecting the original development dataset. V2.1 was further revised after inspecting V2's errors on the separate challenge dataset. Consequently, neither result constitutes an untouched independent validation of the final detector. A new, previously unseen dataset authored independently of the detector rules is required. The results should be treated as preliminary prototype findings, not as evidence of reliable threat detection in deployed systems. Zero false positives among only 10 normal scenarios is insufficient to establish a low real-world false-positive rate.

The proposed monitoring approach also has dual-use implications. Interaction-log analysis may support safety oversight and accountability, but it could also enable excessive surveillance or be misused to classify benign agent behavior as suspicious. Any practical deployment should include appropriate access controls, data minimization, human review, and safeguards against false accusations. The prototype is intended for research and defensive oversight, not autonomous enforcement or punitive decisions.

## 8. Conclusion

This project explored rule-based detection of hidden coordination, goal drift, supervisor bypass, and concealment in a simulated multi-agent environment. The experiments showed that detection performance depends on both the available log information and the design of detection rules. Full audit logs exposed patterns unavailable in supervisor-visible logs, while structured authorization checks were effective for identifying simulated supervisor bypass. V2 improved results on the original development dataset, and V2.1 improved recall on the separate challenge dataset after further rule refinement. However, the final detector has not yet been evaluated on a new untouched test set. Future work should use independently authored and more diverse scenarios, realistic LLM-based agents, multilingual and adversarial paraphrases, and larger normal-case samples to estimate false-positive rates more reliably.

## References

[1] O. Makins, O. Angelini, Z. Shams, and M. Phuong, “Multi-Agent AI Control: Distributed Attacks Hamper Per-Instance Monitors,” arXiv preprint arXiv:2607.07368, 2026. Available:[ https://arxiv.org/abs/2607.07368](https://arxiv.org/abs/2607.07368)

[2] E. Tabassi, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1. National Institute of Standards and Technology, 2023.[ https://doi.org/10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1)

[3] OWASP Foundation, “AI Agent Security Cheat Sheet.” OWASP Cheat Sheet Series. Available:[ https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) (accessed Nov. 8, 2026).

[4] OWASP GenAI Security Project, “Agentic AI – Threats and Mitigations,” Feb. 17, 2025. Available:[ https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)


