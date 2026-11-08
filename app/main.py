import os
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, USING_SQLITE_FALLBACK
from .models import Enquiry, BookingProposal
from .security import create_session_token, verify_password, verify_session_token

SESSION_COOKIE = "phi_admin_session"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Professional Home Inspection API", version="0.2.0", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory="app/static/assets"), name="assets")

class EnquiryIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=40)
    property_address: str = Field(min_length=5, max_length=300)
    property_type: str = Field(default="Detached", max_length=40)
    approximate_size_sqft: int = Field(default=0, ge=0, le=50000)
    message: str = Field(default="", max_length=4000)
    preferred_dates: str = Field(default="", max_length=1000)

class ProposalIn(BaseModel):
    option_1: str = Field(min_length=5, max_length=80)
    option_2: str = Field(default="", max_length=80)
    option_3: str = Field(default="", max_length=80)

class LoginIn(BaseModel):
    password: str = Field(min_length=1, max_length=256)

def _check_same_origin(request: Request):
    origin = request.headers.get("origin")
    if not origin:
        return
    parsed = urlsplit(origin)
    if parsed.scheme not in {"https", "http"} or parsed.netloc.lower() != request.headers.get("host", "").lower():
        raise HTTPException(status_code=403, detail="Cross-origin request blocked.")

def require_admin(request: Request):
    secret = os.getenv("ADMIN_SESSION_SECRET", "")
    token = request.cookies.get(SESSION_COOKIE, "")
    if len(secret) < 32 or not token or not verify_session_token(token, secret):
        raise HTTPException(status_code=401, detail="Please sign in to the admin dashboard.")
    return True

@app.get("/")
def home():
    return FileResponse("app/static/index.html")

@app.get("/admin")
def admin():
    return FileResponse("app/static/admin.html")

@app.get("/api/health")
def health():
    admin_configured = bool(os.getenv("ADMIN_PASSWORD_HASH", "").strip()) and len(os.getenv("ADMIN_SESSION_SECRET", "")) >= 32
    return {
        "status": "ok",
        "service": "professional-home-inspection",
        "version": app.version,
        "database_mode": "sqlite-demo-only" if USING_SQLITE_FALLBACK else "postgresql",
        "persistent_storage_configured": not USING_SQLITE_FALLBACK,
        "admin_configured": admin_configured,
        "submissions_enabled": os.getenv("ALLOW_PUBLIC_SUBMISSIONS", "false").lower() == "true" and not USING_SQLITE_FALLBACK and admin_configured,
        "timezone": os.getenv("TIMEZONE", "America/Vancouver"),
    }

@app.post("/api/admin/login")
def admin_login(payload: LoginIn, request: Request, response: Response):
    _check_same_origin(request)
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
    secret = os.getenv("ADMIN_SESSION_SECRET", "")
    if not password_hash or len(secret) < 32:
        raise HTTPException(status_code=503, detail="Admin login is not configured.")
    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid password.")
    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(secret),
        max_age=8 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/admin",
    )
    return {"authenticated": True}

@app.post("/api/admin/logout")
def admin_logout(request: Request, response: Response):
    _check_same_origin(request)
    response.delete_cookie(key=SESSION_COOKIE, path="/api/admin", secure=True, httponly=True, samesite="strict")
    return {"authenticated": False}

@app.post("/api/enquiries")
def create_enquiry(payload: EnquiryIn, db: Session = Depends(get_db)):
    admin_configured = bool(os.getenv("ADMIN_PASSWORD_HASH", "").strip()) and len(os.getenv("ADMIN_SESSION_SECRET", "")) >= 32
    if USING_SQLITE_FALLBACK or not admin_configured or os.getenv("ALLOW_PUBLIC_SUBMISSIONS", "false").lower() != "true":
        raise HTTPException(status_code=503, detail="Online submissions are not enabled yet. Please contact the business directly.")
    item = Enquiry(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": item.status, "message": "Your enquiry has been received. An inspector will review it."}

@app.post("/api/assistant")
def assistant(payload: dict):
    question = str(payload.get("question", "")).strip().lower()
    if not question or len(question) > 1000:
        raise HTTPException(status_code=400, detail="Please enter a question (maximum 1,000 characters).")
    answers = [
        (("cost", "price", "quote", "fee"), "Inspection pricing depends on the property's size, type, age, location, and complexity. Send an enquiry with the property details and the inspector will review a quote before it is sent."),
        (("duration", "long", "hours"), "A standard inspection appointment is planned for approximately five hours. The actual time depends on the property's size and condition."),
        (("book", "booking", "schedule", "availability", "appointment"), "You can submit your preferred dates through the enquiry form. An administrator reviews availability and may propose up to three appointment options. A booking is not confirmed until approved."),
        (("report", "what", "include"), "A home inspection is intended to help identify visible conditions and potential concerns in accessible areas. The exact scope and limitations will be explained before the inspection."),
        (("area", "where", "location", "british columbia", "bc"), "Professional Home Inspection serves customers in British Columbia. Please include the property address so the service area can be confirmed."),
    ]
    for keys, answer in answers:
        if any(k in question for k in keys):
            return {"answer": answer, "mode": "guided-faq"}
    return {"answer": "Thanks for your question. I can help with pricing, inspection duration, booking steps, and service areas. For property-specific advice, please send an enquiry so the inspector can review the details.", "mode": "guided-faq"}

@app.get("/api/admin/enquiries")
def list_enquiries(
    page: int = Query(default=1, ge=1),
    status: str = Query(default="active", pattern="^(active|deleted|all)$"),
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Enquiry)
    if status == "deleted":
        query = query.filter(Enquiry.status == "deleted")
    elif status == "active":
        query = query.filter(Enquiry.status != "deleted")
    total = query.count()
    rows = query.order_by(Enquiry.created_at.desc()).offset((page - 1) * 10).limit(10).all()
    items = [{"id": x.id, "name": x.name, "email": x.email, "phone": x.phone, "property_address": x.property_address, "property_type": x.property_type, "approximate_size_sqft": x.approximate_size_sqft, "message": x.message, "preferred_dates": x.preferred_dates, "status": x.status, "created_at": x.created_at.isoformat()} for x in rows]
    return {"items": items, "page": page, "per_page": 10, "total": total, "pages": (total + 9) // 10}

@app.patch("/api/admin/enquiries/{enquiry_id}/status")
def update_status(enquiry_id: int, payload: dict, request: Request, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    _check_same_origin(request)
    status = str(payload.get("status", ""))
    if status not in {"new", "reviewing", "awaiting_customer", "approved", "declined", "deleted"}:
        raise HTTPException(status_code=400, detail="Unsupported status.")
    item = db.get(Enquiry, enquiry_id)
    if not item:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    item.status = status
    db.commit()
    return {"id": item.id, "status": item.status}

@app.post("/api/admin/enquiries/{enquiry_id}/proposals")
def propose_times(enquiry_id: int, payload: ProposalIn, request: Request, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    _check_same_origin(request)
    if not db.get(Enquiry, enquiry_id):
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    item = BookingProposal(enquiry_id=enquiry_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": item.status, "options": [x for x in [item.option_1, item.option_2, item.option_3] if x]}

@app.get("/api/admin/bookings")
def list_bookings(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(BookingProposal).order_by(BookingProposal.created_at.desc()).limit(100).all()
    return [{"id": x.id, "enquiry_id": x.enquiry_id, "options": [v for v in [x.option_1, x.option_2, x.option_3] if v], "status": x.status, "created_at": x.created_at.isoformat()} for x in rows]
