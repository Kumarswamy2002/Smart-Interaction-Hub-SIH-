# Smart Interaction Hub (SIH)

**Smart Interaction Hub (SIH)** is a production-grade, domain-driven interaction and automation platform designed to operate as an **Interaction Operating Layer** between users and digital systems.

## Core Architectural Principle

```
USER
  ↓
INTERACTION
  ↓
INTENT
  ↓
CONTEXT
  ↓
PLAN
  ↓
POLICY
  ↓
PERMISSION
  ↓
ACTION
  ↓
EXECUTION
  ↓
VERIFICATION
  ↓
MEMORY / AUDIT
  ↓
USER
```

## Architecture Domains

1. **Identity Domain**: User accounts, organizations, workspaces, auth, RBAC/ABAC.
2. **Interaction Domain**: Conversations, sessions, streaming responses, input/output gateway.
3. **Intelligence Domain**: Intent extraction, entity parsing, reasoning engine, AI abstractions.
4. **Context Engine**: Unified context resolver across conversation, user, tasks, temporal, device, and external states.
5. **Memory Engine**: 5-Tier Memory (Short-Term, Episodic, Semantic, Preference, Operational).
6. **Knowledge Platform**: Document indexing, vector search, entities, provenance, source tracking.
7. **Intent Engine**: Natural language intent parser to structured intent contracts.
8. **Planning Engine**: Intent-to-DAG execution planner with risk and approval checks.
9. **Policy Platform**: Multi-tier policy evaluator (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
10. **Approval System**: Human-in-the-loop review, approval workflows, delegation, expiration.
11. **Action Platform**: Tool registry, controlled executor, verification, audit linking.
12. **Workflow Platform**: Automated DAG workflows with triggers, conditions, branching, retries.
13. **Task Platform**: First-class task manager with subtasks, dependencies, and automation.
14. **Scheduler**: One-time, cron recurring, delayed execution runner.
15. **Event Architecture**: Decoupled async domain event bus (`UserCreated`, `ActionApproved`, etc.).
16. **Integration Platform**: Standardized connector framework (Email, Calendar, Storage, Messaging, REST API, IoT).
17. **Developer Platform**: Public REST API, API Keys, Webhooks, SDK contracts.
18. **Notification Platform**: Multi-channel notification dispatcher and user preferences.
19. **Audit Platform**: Immutable, queryable audit trail for all security and operational events.
20. **Observability**: Metrics collection, distributed health checks, and latency tracking.
21. **Security Architecture**: AES-256 secrets encryption, JWT auth, RBAC/ABAC guards.
22. **Experience Layer**:
    - Modern Glassmorphic Web Dashboard (`/`)
    - Command-line Interface (`sih-cli`)
    - REST & SSE Gateway (`/api/v1`)

## Getting Started

### Prerequisites
- Python 3.12+

### Installation & Run

```bash
# Install dependencies
python -m pip install -e .

# Run Web & API server
python -m uvicorn sih.api.app:app --reload --port 8000

# Run CLI objective execution
python -m sih.cli.main objective "Prepare for tomorrow's project meeting"
```

### Running Tests

```bash
python -m pytest
```
