from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import url_service
from app.utils.qr_generator import generate_qr_code
from app.core.config import settings

router = APIRouter()

@router.get("/{short_code}/qr")
def get_qr_code(short_code: str, db: Session = Depends(get_db)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    full_url = f"{settings.BASE_URL}/s/{db_url.short_code}"
    return generate_qr_code(full_url)
