from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, auth, users, analytics, qrcode, dashboard
from app.database.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwiftLink API",
    description="Professional URL Shortener Backend",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development, can restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to SwiftLink API"}

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(qrcode.router, prefix="/api/v1/qr", tags=["qr"])
app.include_router(routes.router)
