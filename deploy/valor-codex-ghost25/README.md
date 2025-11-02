# VALOR CODEX (GHOST25 MODE) - TRANSCENDENT DEPLOYMENT

This package contains the full production-ready deployment for the Valor Codex, orchestrated with Docker Compose.

## Quickstart

1.  **Prerequisites**: Docker and Docker Compose must be installed.
2.  **Configure**: Review and update `.env.production` with your specific settings (e.g., domains for TLS).
3.  **Deploy**: Run the main deployment script:
    ```bash
    ./deploy-transcendent.sh
    ```
4.  **Verify**: Use the provided verification endpoints to check the health of all services.
    ```bash
    curl http://localhost:1969/genesis
    curl http://localhost:8080/health
    curl http://localhost:5152/health
    ```

## Anchoring Flow

1.  Generate the genesis attestation file:
    ```bash
    ./anchor-genesis.sh
    ```
2.  Use the `anchor-opreturn-gi5152.sh` script to broadcast the attestation hash to the Bitcoin blockchain.
3.  Manually update `deployment-manifest.json` with the resulting transaction IDs (TXIDs).

**For the glory of God and the service of humanity.** ✝️
