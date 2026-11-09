import os
import time
from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, condecimal
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, USING_SQLITE_FALLBACK
from .models import Enquiry, BookingProposal, QuoteSettings, QuoteDraft
from .security import create_session_token, verify_password, verify_session_token

SESSION_COOKIE = "phi_admin_session"
_LOGIN_FAILURES: dict[str, list[float]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Professional Home Inspection API", version="0.3.0", lifespan=lifespan)
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

class QuoteSettingsIn(BaseModel):
    base_fee: condecimal(ge=0, le=100000) 
    per_sqft_rate: condecimal(ge=0, le=100)
    minimum_fee: condecimal(ge=0, le=100000)

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
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    recent = [stamp for stamp in _LOGIN_FAILURES.get(client_ip, []) if now - stamp < 900]
    _LOGIN_FAILURES[client_ip] = recent
    if len(recent) >= 5:
        raise HTTPException(status_code=429, detail="Too many sign-in attempts. Try again in 15 minutes.")
    if not verify_password(payload.password, password_hash):
        _LOGIN_FAILURES[client_ip] = recent + [now]
        raise HTTPException(status_code=401, detail="Invalid password.")
    _LOGIN_FAILURES.pop(client_ip, None)
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

def _quote_settings_payload(item: QuoteSettings | None):
    if item is None:
        return {"configured": False, "currency": "CAD", "base_fee": None, "per_sqft_rate": None, "minimum_fee": None}
    return {
        "configured": True,
        "currency": "CAD",
        "base_fee": str(item.base_fee),
        "per_sqft_rate": str(item.per_sqft_rate),
        "minimum_fee": str(item.minimum_fee),
    }

@app.get("/api/admin/quote-settings")
def get_quote_settings(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    return _quote_settings_payload(db.get(QuoteSettings, 1))

@app.put("/api/admin/quote-settings")
def update_quote_settings(payload: QuoteSettingsIn, request: Request, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    _check_same_origin(request)
    base = Decimal(payload.base_fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rate = Decimal(payload.per_sqft_rate).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    minimum = Decimal(payload.minimum_fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if base == 0 and rate == 0 and minimum == 0:
        raise HTTPException(status_code=422, detail="At least one pricing amount must be greater than zero.")
    item = db.get(QuoteSettings, 1)
    if item is None:
        item = QuoteSettings(id=1, base_fee=base, per_sqft_rate=rate, minimum_fee=minimum)
        db.add(item)
    else:
        item.base_fee, item.per_sqft_rate, item.minimum_fee = base, rate, minimum
    db.commit()
    return _quote_settings_payload(item)

@app.post("/api/admin/enquiries/{enquiry_id}/quote")
def create_quote_draft(enquiry_id: int, request: Request, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    _check_same_origin(request)
    enquiry = db.get(Enquiry, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    if enquiry.approximate_size_sqft <= 0:
        raise HTTPException(status_code=422, detail="A valid property size is required before calculating a quote.")
    settings = db.get(QuoteSettings, 1)
    if settings is None:
        raise HTTPException(status_code=409, detail="Quote pricing is not configured. Set the business pricing rules first.")
    base = Decimal(settings.base_fee)
    rate = Decimal(settings.per_sqft_rate)
    minimum = Decimal(settings.minimum_fee)
    raw = base + (rate * Decimal(enquiry.approximate_size_sqft))
    subtotal = max(minimum, raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    draft = QuoteDraft(
        enquiry_id=enquiry.id,
        property_type=enquiry.property_type,
        size_sqft=enquiry.approximate_size_sqft,
        base_fee=base,
        per_sqft_rate=rate,
        minimum_fee=minimum,
        subtotal=subtotal,
        currency="CAD",
        status="draft",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return {
        "id": draft.id,
        "enquiry_id": draft.enquiry_id,
        "property_type": draft.property_type,
        "size_sqft": draft.size_sqft,
        "base_fee": str(draft.base_fee),
        "per_sqft_rate": str(draft.per_sqft_rate),
        "minimum_fee": str(draft.minimum_fee),
        "subtotal": str(draft.subtotal),
        "currency": draft.currency,
        "status": draft.status,
        "note": draft.note,
        "created_at": draft.created_at.isoformat(),
    }

@app.get("/api/admin/quotes")
def list_quote_drafts(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(QuoteDraft).order_by(QuoteDraft.created_at.desc()).limit(100).all()
    return [{
        "id": x.id, "enquiry_id": x.enquiry_id, "property_type": x.property_type,
        "size_sqft": x.size_sqft, "base_fee": str(x.base_fee),
        "per_sqft_rate": str(x.per_sqft_rate), "minimum_fee": str(x.minimum_fee),
        "subtotal": str(x.subtotal), "currency": x.currency, "status": x.status,
        "note": x.note, "created_at": x.created_at.isoformat()
    } for x in rows]
