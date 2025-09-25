"""
CORS and Security Middleware for FitFusion AI Workout App
Handles Cross-Origin Resource Sharing, security headers, and request validation
"""

import os
import time
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urlparse
import logging

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    
    def __init__(self, app, enable_csp: bool = True, enable_hsts: bool = True):
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Content Security Policy
        if self.enable_csp:
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https://api.supabase.co https://*.supabase.co https://generativelanguage.googleapis.com; "
                "frame-src 'none'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response.headers["Content-Security-Policy"] = csp_policy
        
        # HTTP Strict Transport Security
        if self.enable_hsts and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )
        
        # Remove server information (if present)
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    """
    
    def __init__(
        self, 
        app, 
        requests_per_minute: int = 60,
        burst_requests: int = 10,
        enable_rate_limiting: bool = True
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.enable_rate_limiting = enable_rate_limiting
        self.request_counts: Dict[str, List[float]] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        if not self.enable_rate_limiting:
            return False
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Get or create request history for this IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        requests = self.request_counts[client_ip]
        
        # Remove requests older than 1 minute
        requests[:] = [req_time for req_time in requests if req_time > minute_ago]
        
        # Check burst limit (last 10 seconds)
        ten_seconds_ago = current_time - 10
        recent_requests = [req_time for req_time in requests if req_time > ten_seconds_ago]
        
        if len(recent_requests) >= self.burst_requests:
            return True
        
        # Check per-minute limit
        if len(requests) >= self.requests_per_minute:
            return True
        
        # Add current request
        requests.append(current_time)
        
        return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self.get_client_ip(request)

        if request.method in {'OPTIONS', 'HEAD'}:
            return await call_next(request)

        if self.is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    def __init__(self, app, log_body: bool = False, log_headers: bool = False):
        super().__init__(app)
        self.log_body = log_body
        self.log_headers = log_headers
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.log_headers:
            log_data["headers"] = dict(request.headers)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            log_data.update({
                "status_code": response.status_code,
                "process_time": round(process_time * 1000, 2)  # in milliseconds
            })
            
            # Log based on status code
            if response.status_code >= 500:
                logger.error(f"Server error: {log_data}")
            elif response.status_code >= 400:
                logger.warning(f"Client error: {log_data}")
            else:
                logger.info(f"Request processed: {log_data}")
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            log_data.update({
                "status_code": 500,
                "process_time": round(process_time * 1000, 2),
                "error": str(e)
            })
            logger.error(f"Request failed: {log_data}")
            raise

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware for protected endpoints
    """
    
    def __init__(
        self, 
        app, 
        secret_key: str,
        algorithm: str = "HS256",
        protected_paths: List[str] = None
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.protected_paths = protected_paths or ["/api/"]
        self.excluded_paths = [
            "/",
            "/api/health",
            "/api/info",
            "/api/docs",
            "/api/openapi.json",
            "/api/redoc",
            "/api/sessions/health",
            "/api/programs/health",
            "/api/profile/health",
            "/api/equipment/health",
            "/api/ai/health"
        ]
    
    def is_protected_path(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Check excluded paths first
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return False
        
        # Check protected paths
        for protected in self.protected_paths:
            if path.startswith(protected):
                return True
        
        return False
    
    def extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        # Check cookie (fallback)
        return request.cookies.get("access_token")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return None
            
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Always allow OPTIONS requests (CORS preflight) to pass through
        # This is critical for CORS to work properly
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip authentication for non-protected paths
        if not self.is_protected_path(request.url.path):
            return await call_next(request)
        
        # Extract and verify token
        token = self.extract_token(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Authentication required",
                    "message": "Access token is missing"
                }
            )
        
        payload = self.verify_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid token",
                    "message": "Access token is invalid or expired"
                }
            )
        
        # Add user info to request state
        request.state.user = payload
        
        return await call_next(request)

def setup_cors_middleware(
    app: FastAPI,
    allowed_origins: List[str] = None,
    allow_credentials: bool = True,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None
) -> None:
    """
    Setup CORS middleware with appropriate configuration
    """
    
    # Default allowed origins
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",  # Next.js dev server
            "http://localhost:3001",  # Alternative dev port
            "https://fitfusion.vercel.app",  # Production frontend
            "https://*.vercel.app",  # Vercel preview deployments
        ]
        
        # Add environment-specific origins
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url:
            allowed_origins.append(frontend_url)
    
    # Default allowed methods
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    
    # Default allowed headers
    if allow_headers is None:
        allow_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=["X-Process-Time", "X-Rate-Limit-Remaining"],
        max_age=86400,  # 24 hours
    )

def setup_security_middleware(
    app: FastAPI,
    enable_rate_limiting: bool = True,
    enable_auth: bool = True,
    enable_logging: bool = True,
    enable_compression: bool = True,
    enable_trusted_hosts: bool = True
) -> None:
    """
    Setup all security middleware
    """
    
    # Trusted hosts middleware
    if enable_trusted_hosts:
        allowed_hosts = ["*"]  # Configure based on environment
        if os.getenv("ENVIRONMENT") == "production":
            allowed_hosts = [
                "fitfusion-api.herokuapp.com",  # Example production domain
                "api.fitfusion.com",
                "localhost"
            ]
        
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )
    
    # Compression middleware
    if enable_compression:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Security headers middleware
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_csp=True,
        enable_hsts=os.getenv("ENVIRONMENT") == "production"
    )
    
    # Rate limiting middleware
    if enable_rate_limiting:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            burst_requests=int(os.getenv("RATE_LIMIT_BURST", "10")),
            enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        )
    
    # Authentication middleware
    if enable_auth and os.getenv("ENABLE_AUTH", "true").lower() == "true":
        secret_key = os.getenv("JWT_SECRET_KEY")
        # Only enable auth in production or when JWT_SECRET_KEY is properly set
        if secret_key and secret_key != "your_super_secret_jwt_key_here":
            app.add_middleware(
                AuthenticationMiddleware,
                secret_key=secret_key,
                protected_paths=["/api/profile", "/api/equipment", "/api/programs", "/api/sessions"]
            )
            logger.info("JWT authentication enabled")
        else:
            logger.warning("JWT authentication disabled - no valid secret key found")
    else:
        logger.info("JWT authentication disabled via ENABLE_AUTH setting")
    
    # Request logging middleware
    if enable_logging:
        app.add_middleware(
            RequestLoggingMiddleware,
            log_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
            log_headers=os.getenv("LOG_REQUEST_HEADERS", "false").lower() == "true"
        )

def setup_all_middleware(app: FastAPI) -> None:
    """
    Setup all middleware for the FitFusion API
    """
    
    # Setup CORS
    setup_cors_middleware(app)
    
    # Setup security middleware
    setup_security_middleware(
        app,
        enable_rate_limiting=True,
        enable_auth=True,
        enable_logging=True,
        enable_compression=True,
        enable_trusted_hosts=True
    )
    
    logger.info("All middleware configured successfully")

# Health check endpoint for middleware testing
async def middleware_health_check() -> Dict[str, Any]:
    """Health check endpoint to test middleware functionality"""
    return {
        "status": "healthy",
        "middleware": {
            "cors": "enabled",
            "security_headers": "enabled",
            "rate_limiting": "enabled",
            "authentication": "enabled",
            "logging": "enabled",
            "compression": "enabled"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
