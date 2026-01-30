# API Reference (v1)

Base URL (dev): `http://localhost:8000/api/v1`

## Users

### `POST /users/`

Create (or get existing) user identity and derived wallets.

Request:

```json
{ "email": "user@example.com", "name": "User" }
```

Response includes:

- `id`
- `derivation_index`
- `wallets[]` with `chain`, `address`, `derivation_path`

## Wallets

### `GET /wallets/{user_id}/balances`

Returns native balance per custodial wallet record.

Response shape:

```json
[{"chain":"bsc","address":"0x...","balance":0.0,"symbol":"BNB"}]
```

## Agreements (DB)

### `POST /agreements/{user_id}/create`

Creates an off-chain agreement record in Postgres.

Note: this endpoint applies a token-gated access check (TST holdings) via `access_control`.

### `GET /agreements/{user_id}/list`

Lists DB agreements where the user is creator or counterparty.

## Transactions

### `POST /transactions/{user_id}/withdraw`

Processes a withdrawal request (internal ledger model).

### `GET /transactions/{user_id}/history`

Returns deposit/withdrawal records.

## Hearing (Entities)

### `GET /hearing/example`

Returns a deterministic-shaped example `HearingRecord`.

### `GET /hearing/schema`

Returns JSON Schema for the `HearingRecord` contract.

### `POST /hearing/run`

Runs the entity pipeline.

Request fields include perception booleans and operational context.

Supports `persist: true` to write into `hearing_records`.

### `POST /hearing/gate`

Checks a named action (transfer/escrow_create/escrow_release) and returns:

- `allowed`
- `reason`
- `hearing` (full record)

Also supports `persist: true`.
