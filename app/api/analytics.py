from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import url_service, analytics_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{short_code}")
def get_detailed_analytics(short_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    if db_url.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics for this URL")
        
    analytics = analytics_service.get_url_analytics(db, db_url.id)
    return {"url_info": db_url, "clicks": analytics}
