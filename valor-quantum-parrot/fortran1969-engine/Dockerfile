FROM ubuntu:20.04

# Install FORTRAN and dependencies
RUN apt-get update && apt-get install -y \
    gfortran \
    netcat-openbsd \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy FORTRAN code
COPY code/ .

# Create a simple HTTP server in Python to simulate FORTRAN1969 engine
RUN pip3 install flask

# Create the FORTRAN1969 engine simulator
COPY fortran1969_server.py .

# Expose ports
EXPOSE 1969 5150

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD nc -z localhost 1969 || exit 1

CMD ["python3", "fortran1969_server.py"]
