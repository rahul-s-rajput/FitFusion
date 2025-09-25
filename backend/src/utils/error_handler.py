"""
Error Handling and Logging System for FitFusion AI Workout App
Comprehensive error handling, logging, and monitoring utilities
"""

import os
import sys
import traceback
import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import asyncio
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

class ErrorCode(str, Enum):
    """Standardized error codes for the application"""
    
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    
    # AI/ML errors
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    AI_QUOTA_EXCEEDED = "AI_QUOTA_EXCEEDED"
    AI_INVALID_REQUEST = "AI_INVALID_REQUEST"
    
    # Business logic errors
    INVALID_WORKOUT_DATA = "INVALID_WORKOUT_DATA"
    EQUIPMENT_NOT_AVAILABLE = "EQUIPMENT_NOT_AVAILABLE"
    SESSION_ALREADY_COMPLETED = "SESSION_ALREADY_COMPLETED"
    PROGRAM_NOT_ACTIVE = "PROGRAM_NOT_ACTIVE"
    
    # External service errors
    SUPABASE_ERROR = "SUPABASE_ERROR"
    GEMINI_API_ERROR = "GEMINI_API_ERROR"
    SYNC_ERROR = "SYNC_ERROR"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Context information for errors"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class FitFusionError:
    """Standardized error structure"""
    code: ErrorCode
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    context: Optional[ErrorContext] = None
    stack_trace: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert error to JSON string"""
        return json.dumps(self.to_dict(), default=str)

class FitFusionLogger:
    """Enhanced logger for FitFusion application"""
    
    def __init__(self, name: str = "fitfusion"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        
        # Set log level from environment
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level))
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
            '[%(filename)s:%(lineno)d] - %(funcName)s()'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if configured)
        log_file = os.getenv("LOG_FILE")
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # JSON handler for structured logging
        if os.getenv("STRUCTURED_LOGGING", "false").lower() == "true":
            json_handler = logging.StreamHandler(sys.stdout)
            json_handler.setFormatter(self.JsonFormatter())
            self.logger.addHandler(json_handler)
    
    class JsonFormatter(logging.Formatter):
        """JSON formatter for structured logging"""
        
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
            
            return json.dumps(log_entry)
    
    def log_error(self, error: FitFusionError):
        """Log a FitFusion error"""
        extra = {
            "error_code": error.code.value,
            "severity": error.severity.value,
            "correlation_id": error.correlation_id,
            "context": asdict(error.context) if error.context else None
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(error.message, extra=extra)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(error.message, extra=extra)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(error.message, extra=extra)
        else:
            self.logger.info(error.message, extra=extra)
    
    def log_request(self, request: Request, response_time: float, status_code: int):
        """Log HTTP request"""
        extra = {
            "method": request.method,
            "url": str(request.url),
            "status_code": status_code,
            "response_time": response_time,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "request_id": getattr(request.state, "request_id", None)
        }
        
        if status_code >= 500:
            self.logger.error(f"Server error: {request.method} {request.url.path}", extra=extra)
        elif status_code >= 400:
            self.logger.warning(f"Client error: {request.method} {request.url.path}", extra=extra)
        else:
            self.logger.info(f"Request: {request.method} {request.url.path}", extra=extra)

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        self.logger = FitFusionLogger()
        self.setup_sentry()
    
    def setup_sentry(self):
        """Setup Sentry error tracking"""
        sentry_dsn = (os.getenv("SENTRY_DSN") or "").strip()
        if not sentry_dsn or "://" not in sentry_dsn:
            self.logger.logger.info("Sentry DSN not configured or invalid; skipping Sentry setup")
            return

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration()
            ],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("APP_VERSION", "unknown")
        )
    
    def create_error(
        self,
        code: ErrorCode,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        exception: Optional[Exception] = None,
        correlation_id: Optional[str] = None
    ) -> FitFusionError:
        """Create a standardized error"""
        
        stack_trace = None
        if exception:
            stack_trace = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
            stack_trace = ''.join(stack_trace)
        
        error = FitFusionError(
            code=code,
            message=message,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            context=context,
            stack_trace=stack_trace,
            correlation_id=correlation_id
        )
        
        # Log the error
        self.logger.log_error(error)
        
        # Send to Sentry for high/critical errors
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            sentry_sdk.capture_exception(exception) if exception else sentry_sdk.capture_message(message)
        
        return error
    
    def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        
        context = self.extract_context_from_request(request)
        
        # Map HTTP status codes to error codes
        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_ERROR,
            403: ErrorCode.AUTHORIZATION_ERROR,
            404: ErrorCode.NOT_FOUND,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        severity = ErrorSeverity.HIGH if exc.status_code >= 500 else ErrorSeverity.MEDIUM
        
        error = self.create_error(
            code=error_code,
            message=str(exc.detail),
            severity=severity,
            context=context
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error.code.value,
                    "message": error.message,
                    "timestamp": error.timestamp.isoformat(),
                    "correlation_id": error.correlation_id
                }
            }
        )
    
    def handle_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors"""
        
        context = self.extract_context_from_request(request)
        
        error = self.create_error(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            severity=ErrorSeverity.LOW,
            context=context
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": error.code.value,
                    "message": error.message,
                    "details": exc.errors(),
                    "timestamp": error.timestamp.isoformat(),
                    "correlation_id": error.correlation_id
                }
            }
        )
    
    def handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions"""
        
        context = self.extract_context_from_request(request)
        
        error = self.create_error(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            severity=ErrorSeverity.CRITICAL,
            context=context,
            exception=exc
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": error.code.value,
                    "message": error.message,
                    "timestamp": error.timestamp.isoformat(),
                    "correlation_id": error.correlation_id
                }
            }
        )
    
    def extract_context_from_request(self, request: Request) -> ErrorContext:
        """Extract context information from request"""
        return ErrorContext(
            user_id=getattr(request.state, "user_id", None),
            session_id=getattr(request.state, "session_id", None),
            request_id=getattr(request.state, "request_id", None),
            endpoint=request.url.path,
            method=request.method,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )

# Global error handler instance
_error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_errors(func):
    """Decorator for handling errors in async functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_handler = get_error_handler()
            
            # Determine error code based on exception type
            if isinstance(e, HTTPException):
                raise e  # Let FastAPI handle it
            elif "database" in str(e).lower():
                error_code = ErrorCode.DATABASE_QUERY_ERROR
            elif "gemini" in str(e).lower() or "ai" in str(e).lower():
                error_code = ErrorCode.AI_SERVICE_UNAVAILABLE
            else:
                error_code = ErrorCode.INTERNAL_SERVER_ERROR
            
            error = error_handler.create_error(
                code=error_code,
                message=str(e),
                severity=ErrorSeverity.HIGH,
                exception=e
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error.message
            )
    
    return wrapper

@contextmanager
def error_context(operation: str, **context_data):
    """Context manager for error handling"""
    try:
        yield
    except Exception as e:
        error_handler = get_error_handler()
        
        context = ErrorContext(
            additional_data={
                "operation": operation,
                **context_data
            }
        )
        
        error = error_handler.create_error(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Error in {operation}: {str(e)}",
            severity=ErrorSeverity.HIGH,
            context=context,
            exception=e
        )
        
        raise

def setup_error_handlers(app):
    """Setup error handlers for FastAPI app"""
    error_handler = get_error_handler()
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return error_handler.handle_http_exception(request, exc)
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        return error_handler.handle_http_exception(request, HTTPException(status_code=exc.status_code, detail=exc.detail))
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return error_handler.handle_validation_error(request, exc)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return error_handler.handle_general_exception(request, exc)

# Utility functions for common error scenarios
def create_ai_error(message: str, exception: Optional[Exception] = None) -> FitFusionError:
    """Create an AI-related error"""
    error_handler = get_error_handler()
    return error_handler.create_error(
        code=ErrorCode.AI_SERVICE_UNAVAILABLE,
        message=message,
        severity=ErrorSeverity.HIGH,
        exception=exception
    )

def create_database_error(message: str, exception: Optional[Exception] = None) -> FitFusionError:
    """Create a database-related error"""
    error_handler = get_error_handler()
    return error_handler.create_error(
        code=ErrorCode.DATABASE_QUERY_ERROR,
        message=message,
        severity=ErrorSeverity.HIGH,
        exception=exception
    )

def create_validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> FitFusionError:
    """Create a validation error"""
    error_handler = get_error_handler()
    context = ErrorContext(additional_data=details) if details else None
    return error_handler.create_error(
        code=ErrorCode.VALIDATION_ERROR,
        message=message,
        severity=ErrorSeverity.LOW,
        context=context
    )

# Initialize logging
logger = FitFusionLogger().logger
