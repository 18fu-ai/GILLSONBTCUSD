FROM python:3.9-alpine

WORKDIR /app

RUN pip install flask

COPY neural-network_server.py .

EXPOSE 9090

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

CMD ["python", "neural-network_server.py"]
