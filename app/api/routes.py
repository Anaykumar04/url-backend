from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.url import URLCreate, URLInfo
from app.services import url_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.helpers import get_client_base_url

router = APIRouter()

@router.post("/api/shorten", response_model=URLInfo, status_code=status.HTTP_201_CREATED)
def create_url(url: URLCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_url = url_service.create_short_url(db, url, owner_id=current_user.id)
    
    # Create the full short URL dynamically based on client origin (localhost vs Vercel)
    base_url = get_client_base_url(request)
    short_url = f"{base_url}/s/{db_url.short_code}"
    
    return {
        "id": db_url.id,
        "short_code": db_url.short_code,
        "clicks": db_url.clicks,
        "created_at": db_url.created_at,
        "original_url": db_url.original_url,
        "short_url": short_url
    }

@router.get("/api/urls/{short_code}/stats", response_model=URLInfo)
def get_url_stats(short_code: str, request: Request, db: Session = Depends(get_db)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
        
    base_url = get_client_base_url(request)
    short_url = f"{base_url}/s/{db_url.short_code}"
    
    return {
        "id": db_url.id,
        "short_code": db_url.short_code,
        "clicks": db_url.clicks,
        "created_at": db_url.created_at,
        "original_url": db_url.original_url,
        "short_url": short_url
    }

@router.delete("/api/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(short_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if db_url.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")
    
    db.delete(db_url)
    db.commit()
    return None

@router.get("/s/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
        
    url_service.increment_click_count(db, db_url)
    
    # Record analytics
    from app.schemas.analytics import AnalyticsCreate
    from app.services import analytics_service
    analytics_data = AnalyticsCreate(
        url_id=db_url.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        country=None
    )
    analytics_service.record_click(db, analytics_data)
    
    user_agent_lower = (request.headers.get("user-agent") or "").lower()
    social_bots = ["whatsapp", "telegram", "twitterbot", "facebookexternalhit", "slackbot", "discordbot", "linkedinbot", "bot", "crawler", "spider", "preview", "slurp", "googlebot", "meta"]
    is_bot = any(bot in user_agent_lower for bot in social_bots)
    
    if is_bot:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SwiftLink | Redirecting...</title>
    <meta property="og:title" content="SwiftLink — Shortened Link Preview">
    <meta property="og:description" content="Destination: {db_url.original_url}">
    <meta property="og:url" content="{db_url.original_url}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="SwiftLink">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="SwiftLink — Shortened Link">
    <meta name="twitter:description" content="Destination: {db_url.original_url}">
    <meta http-equiv="refresh" content="0;url={db_url.original_url}">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 3rem; text-align: center; background: #0f172a; color: #f8fafc;">
    <h2 style="margin-bottom: 1rem;">Redirecting to destination...</h2>
    <p style="color: #94a3b8; word-break: break-all; max-width: 600px; margin: 0 auto;">{db_url.original_url}</p>
    <script>window.location.replace("{db_url.original_url}");</script>
</body>
</html>"""
        return HTMLResponse(content=html_content, status_code=200)
    
    return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
