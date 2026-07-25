from sqlalchemy.orm import Session
from app.models.analytics import Analytics
from app.schemas.analytics import AnalyticsCreate
from collections import defaultdict
from typing import List

def record_click(db: Session, analytics: AnalyticsCreate):
    db_analytics = Analytics(
        url_id=analytics.url_id,
        ip_address=analytics.ip_address,
        user_agent=analytics.user_agent,
        country=analytics.country
    )
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def get_url_analytics(db: Session, url_id: int):
    return db.query(Analytics).filter(Analytics.url_id == url_id).all()

def aggregate_analytics(analytics_list: List[Analytics]):
    clicks_over_time = defaultdict(int)
    countries = defaultdict(int)
    browsers = defaultdict(int)
    os_dict = defaultdict(int)
    devices = defaultdict(int)
    referrers = defaultdict(int)

    for a in analytics_list:
        if a.clicked_at:
            date_str = a.clicked_at.strftime("%Y-%m-%d")
            clicks_over_time[date_str] += 1
        
        country = a.country or "Unknown"
        countries[country] += 1
        
        ua = a.user_agent or ""
        ua_lower = ua.lower()
        
        if "chrome" in ua_lower and "edg" not in ua_lower:
            browsers["Chrome"] += 1
        elif "safari" in ua_lower and "chrome" not in ua_lower:
            browsers["Safari"] += 1
        elif "firefox" in ua_lower:
            browsers["Firefox"] += 1
        elif "edg" in ua_lower:
            browsers["Edge"] += 1
        else:
            if ua:
                browsers["Other"] += 1
            else:
                browsers["Unknown"] += 1
            
        if "windows" in ua_lower:
            os_dict["Windows"] += 1
        elif "mac" in ua_lower:
            os_dict["macOS"] += 1
        elif "linux" in ua_lower and "android" not in ua_lower:
            os_dict["Linux"] += 1
        elif "android" in ua_lower:
            os_dict["Android"] += 1
        elif "iphone" in ua_lower or "ipad" in ua_lower:
            os_dict["iOS"] += 1
        else:
            if ua:
                os_dict["Other"] += 1
            else:
                os_dict["Unknown"] += 1
            
        if "mobi" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            devices["Mobile"] += 1
        elif "ipad" in ua_lower or "tablet" in ua_lower:
            devices["Tablet"] += 1
        elif ua:
            devices["Desktop"] += 1
        else:
            devices["Unknown"] += 1
            
        referrers["Direct"] += 1

    return {
        "clicksOverTime": [{"date": k, "count": v} for k, v in sorted(clicks_over_time.items())],
        "countries": [{"country": k, "count": v} for k, v in countries.items()],
        "browsers": [{"browser": k, "count": v} for k, v in browsers.items()],
        "os": [{"os": k, "count": v} for k, v in os_dict.items()],
        "devices": [{"device": k, "count": v} for k, v in devices.items()],
        "referrers": [{"referrer": k, "count": v} for k, v in referrers.items()]
    }
