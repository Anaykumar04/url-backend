from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import url_service
from app.utils.qr_generator import generate_qr_code
from app.core.config import settings
from app.utils.helpers import get_client_base_url

router = APIRouter()

@router.get("/{short_code}/qr")
def get_qr_code(short_code: str, request: Request, db: Session = Depends(get_db)):
    db_url = url_service.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    base_url = get_client_base_url(request)
    full_url = f"{base_url}/s/{db_url.short_code}"
    return generate_qr_code(full_url)
