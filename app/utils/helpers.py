from fastapi import Request
from urllib.parse import urlparse
from app.core.config import settings

def get_client_base_url(request: Request = None) -> str:
    """
    Dynamically determines the frontend base URL from the incoming request headers (Origin or Referer).
    Supports both local development (http://localhost:5173) and production deployments (https://url-frontend-two.vercel.app).
    Falls back to settings.BASE_URL if headers are not present.
    """
    if request:
        origin = request.headers.get("origin")
        if origin:
            return origin.rstrip("/")
        referer = request.headers.get("referer")
        if referer:
            parsed = urlparse(referer)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
    return settings.BASE_URL.rstrip("/")
