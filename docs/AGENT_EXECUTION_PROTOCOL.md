# Agent Execution Protocol

## Purpose
Convert the master checklist into a persistent execution queue rather than a conversational plan.

## Scheduler contract
A scheduler/worker must:
- load MASTER_MISSION_CHECKLIST.md;
- identify highest-priority unresolved item;
- inspect dependencies;
- create/claim a task;
- execute implementation;
- run required tests;
- run adversarial checks;
- remediate failures;
- persist evidence;
- update Mission Control;
- rescan from checklist item 1;
- continue until blocked by a genuine external dependency.

## Worker states
QUEUED → CLAIMED → BUILDING → TESTING → RED_TEAM → REMEDIATING → VERIFYING → COMPLETE.

Blocked state requires blocker type, evidence, owner and next retry condition.

## Anti-stagnation rules
- A status update without a code/test/evidence change does not count as progress.
- Repeated failure requires root-cause analysis, not repeated identical runs.
- A green test cannot hide an unmet checklist acceptance criterion.
- Architecture documents do not count as implementation unless the corresponding executable contract/test exists.
- The coordinator must periodically rescan all checklist phases to detect neglected work.

## Blind-site operation
Production lead processing, campaigns and scheduled analytics run in the deployed application/worker infrastructure. ChatGPT does not need to be present for scheduled jobs to execute.

## Completion evidence
Each completed task records commit SHA, test command/result, acceptance criteria, and artifact/report location.
