FROM python:3.9-alpine

WORKDIR /app

RUN pip install flask

COPY turing-validator_server.py .

EXPOSE 4242

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4242/health || exit 1

CMD ["python", "turing-validator_server.py"]
