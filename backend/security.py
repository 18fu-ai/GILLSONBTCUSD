# backend/security.py - ENHANCED SECURITY
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import secrets
import hashlib
from datetime import datetime, timedelta

class EnhancedSecurity:
    """Production security features"""

    def __init__(self):
        self.api_keys = self.load_api_keys()
        self.rate_limit_data = {}

    def load_api_keys(self):
        # In a real application, load these from a secure store
        return {}

    def generate_api_key(self, client_name: str):
        """Generate secure API key for external integrations"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Store in secure database (simplified)
        self.api_keys[key_hash] = {
            "client_name": client_name,
            "created_at": datetime.utcnow(),
            "permissions": ["read_progress", "read_metrics"]
        }

        return api_key

    async def rate_limit_middleware(self, request: Request, call_next):
        """Basic rate limiting middleware"""
        client_ip = request.client.host
        current_time = datetime.utcnow()

        # Clean old entries
        self.rate_limit_data = {
            ip: data for ip, data in self.rate_limit_data.items()
            if current_time - data["last_request"] < timedelta(minutes=1)
        }

        # Check rate limit
        if client_ip in self.rate_limit_data:
            if self.rate_limit_data[client_ip]["count"] > 100:  # 100 requests per minute
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            self.rate_limit_data[client_ip]["count"] += 1
        else:
            self.rate_limit_data[client_ip] = {
                "count": 1,
                "last_request": current_time
            }

        response = await call_next(request)
        return response

    def validate_api_key(self, credentials: HTTPAuthorizationCredentials):
        """Validate API key for external access"""
        key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
        return key_hash in self.api_keys
