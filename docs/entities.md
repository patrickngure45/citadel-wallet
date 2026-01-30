# Entities (Cross‑Examination Control Plane)

This repo implements a 5-entity pipeline designed to prevent “single-agent blob” behavior.

Core rule:

> Entities do not collaborate. They cross-examine.

## Why entities exist

For a trading/wallet product, most losses come from:

- acting under uncertainty
- operational mistakes (no gas, wrong chain, missing allowance)
- irreversible actions without constraints

Entities create a repeatable process that can:

- gate actions (Risk veto)
- generate a calm explanation (HearingRecord)
- persist decision traces (audit)

## Canonical pipeline (one-way)

Perception → Memory → Risk → Strategy → Execution

Orchestrator (not an entity): **Arena Compiler**.

### Invariants

- Non-overlapping mandates (each entity answers one question)
- One-way flow (no downstream queries)
- Disagreement is first-class (contradiction dominates agreement)
- Risk has absolute veto power
- Execution has zero discretion

## Code locations

- Schema contract: `backend/app/schemas/hearing.py`
- Arena compiler: `backend/app/entities/arena.py`
- Entity modules:
  - `backend/app/entities/perception.py`
  - `backend/app/entities/memory.py`
  - `backend/app/entities/risk.py`
  - `backend/app/entities/strategy.py`
  - `backend/app/entities/execution.py`
- Gate service: `backend/app/services/entity_gate.py`
- API:
  - `POST /api/v1/hearing/run`
  - `POST /api/v1/hearing/gate`
  - persistence: `GET /api/v1/hearing/list`, `GET /api/v1/hearing/{id}`

## What “perfect entities” means in practice

Perfection here is not “more intelligence.” It is **structural integrity**:

### 1) Each output must be falsifiable

- Perception must admit “Unknown” and enumerate contradictions.
- Memory must cite which archetypes were triggered (and why).
- Risk must cite explicit veto rules (rule ids + reasons).
- Strategy must propose reversible, time-boxed options and always include Observe.
- Execution must only translate allowed instructions into procedure and logs.

### 2) Explicit uncertainty beats forced coherence

- Prefer abstention over confident guesses.
- Contradictions should tighten constraints, not get smoothed over.

### 3) The HearingRecord is the product surface

Users should be able to answer:

- “Why didn’t it act?”
- “What exactly blocked it?”
- “What would need to be true for it to proceed?”

If the record can’t answer those, the institution is not real.

## Recommended upgrades (next iteration)

Without breaking the current architecture, the highest-value improvements are:

- Add explicit fields for:
  - “strongest counterargument”
  - “what would change my mind”
  - evidence checklist / sources used
- Make Risk constraints more operational:
  - gas buffer rules
  - allowance sanity
  - slippage caps
  - cooldowns after veto
- Add a Learning Governor (offline only):
  - evaluates calibration and failure cases
  - proposes rule updates
  - never feeds outcome metrics back into entities in production
