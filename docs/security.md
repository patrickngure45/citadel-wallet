# Security & Secrets

This project touches private keys and exchange API credentials. Treat secrets as production-grade from day one.

## Do not commit secrets

- Never commit `.env` containing:
  - mnemonics / seed phrases
  - deployer private keys
  - exchange API secrets
  - Pinata JWTs

If secrets have already been committed, rotate them immediately.

## Wallet custody

### Custodial seed phrase

If you use `CITADEL_MASTER_SEED` to derive user deposit addresses:

- you are running a custodial system
- the seed must be stored in a proper secret manager
- access must be restricted and audited

### MetaMask wallet

MetaMask keeps keys client-side; the app never sees private keys.

## Exchange APIs (Binance/Bybit)

If adding CEX integration:

- start with READ-ONLY keys
- require IP whitelisting
- support key rotation
- never log secrets

## Principle

Security is a product feature.

The entity system should treat operational security failures (no gas buffer, unsafe approval, suspicious token) as first-class veto reasons.
