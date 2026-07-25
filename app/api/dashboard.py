from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.url import URL
from app.models.analytics import Analytics
from app.services.analytics_service import aggregate_analytics

router = APIRouter()

@router.get("/")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_urls = db.query(URL).filter(URL.owner_id == current_user.id).all()
    total_links = len(user_urls)
    total_clicks = sum(url.clicks for url in user_urls)
    
    all_analytics = []
    url_ids = [u.id for u in user_urls]
    if url_ids:
        all_analytics = db.query(Analytics).filter(Analytics.url_id.in_(url_ids)).all()
    
    global_analytics_data = aggregate_analytics(all_analytics)
    
    urls_response = []
    for u in user_urls:
        u_analytics = [a for a in all_analytics if a.url_id == u.id]
        urls_response.append({
            "short_code": u.short_code,
            "original_url": u.original_url,
            "created_at": u.created_at,
            "clicks": u.clicks,
            "analytics": aggregate_analytics(u_analytics)
        })
        
    return {
        "user_email": current_user.email,
        "total_links": total_links,
        "total_clicks": total_clicks,
        "global_analytics": global_analytics_data,
        "urls": urls_response
    }
