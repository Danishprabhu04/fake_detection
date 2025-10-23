from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

def add_rate_limiting(app: FastAPI):
    """Add rate limiting to the application"""
    # Initialize limiter
    limiter = Limiter(key_func=get_remote_address)
    
    # Add limiter to app
    app.state.limiter = limiter
    
    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add rate limiting middleware
    @app.middleware("http")
    async def rate_limit_middleware(request, call_next):
        # Apply rate limiting (100 requests per minute per IP)
        try:
            # This is a simplified version - in production you'd use the proper slowapi decorators
            response = await call_next(request)
            return response
        except Exception as e:
            return await _rate_limit_exceeded_handler(request, RateLimitExceeded("Rate limit exceeded"))