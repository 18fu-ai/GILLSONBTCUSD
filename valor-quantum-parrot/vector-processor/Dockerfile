FROM python:3.9-alpine

WORKDIR /app

RUN pip install flask

COPY vector-processor_server.py .

EXPOSE 8889

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8889/health || exit 1

CMD ["python", "vector-processor_server.py"]
