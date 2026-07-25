import nanoid
from sqlalchemy.orm import Session
from app.models.url import URL
from app.schemas.url import URLCreate
def generate_short_code(size: int = 8) -> str:
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return nanoid.generate(alphabet, size)

def create_short_url(db: Session, url: URLCreate, owner_id: int | None = None) -> URL:
    code = generate_short_code()
    while db.query(URL).filter(URL.short_code == code).first() is not None:
        code = generate_short_code()

    db_url = URL(
        original_url=str(url.original_url),
        short_code=code,
        owner_id=owner_id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()

def increment_click_count(db: Session, db_url: URL) -> URL:
    db_url.clicks += 1  
    db.commit()
    db.refresh(db_url)
    return db_url
