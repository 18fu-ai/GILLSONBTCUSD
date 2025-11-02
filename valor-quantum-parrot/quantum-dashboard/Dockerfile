FROM nginx:alpine

# Install dependencies
RUN apk add --no-cache \
    curl \
    bash \
    openssl

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Generate self-signed SSL certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=Quantum/L=Transcendent/O=VALOR Ai/CN=quantum-parrot.local"

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for HTML content
RUN mkdir -p /usr/share/nginx/html

# Copy HTML file (will be mounted via volume)
# The actual index.html will be provided via volume mount

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
