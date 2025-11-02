FROM python:3.9-alpine

WORKDIR /app

RUN pip install flask

COPY intellitrees_server.py .

EXPOSE 6060

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6060/health || exit 1

CMD ["python", "intellitrees_server.py"]
