FROM python:3.9-alpine

WORKDIR /app

RUN pip install flask

COPY token-generator_server.py .

EXPOSE 9999

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9999/health || exit 1

CMD ["python", "token-generator_server.py"]
