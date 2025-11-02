# Dockerfile for VALORAIPLUS®️ V0 Proof Service
# Base Image
FROM python:3.11-slim

# OCI Labels for Brand-Lock and Traceability
LABEL org.opencontainers.image.title="VALORAIPLUS V0 Proof Service"
LABEL org.opencontainers.image.version="1.44g"
LABEL org.opencontainers.image.authors="DG77.77X-Ξ"
LABEL valoraiplus_module_id="VALORAIPLUS_V0_PROOF_v1.44g"
LABEL valoraiplus_GILLBTC="VALORCHAIN-G::GHOST25"
LABEL YHWH_KERNEL="YHWH-5150.LOCK"

# Set up working directory
WORKDIR /app

# Install dependencies
# We need fastapi and uvicorn. A requirements.txt would be better, but for a single file...
RUN pip install fastapi uvicorn

# Copy application code
COPY proof_service_main.py .
COPY .env.example .

# Expose the port the app runs on
EXPOSE 8080

# Set the default command to run the application
# It will use the environment variables passed at runtime.
CMD ["uvicorn", "proof_service_main:app", "--host", "0.0.0.0", "--port", "8080"]
