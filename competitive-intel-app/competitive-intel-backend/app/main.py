from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from io import BytesIO

from app.models import (
    Company, Competitor, IndustryReport,
    IntelligenceFeedItem, SubscriptionTier, SubscriptionPlan, User
)
from app.services.data_collection import data_collection_service
from app.services.report_generation import report_generation_service
from app.services.billing import billing_service

app = FastAPI(
    title="Competitive Intelligence API",
    description="API for competitive intelligence gathering and reporting",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for POC
companies_db: dict[str, Company] = {}
competitors_db: dict[str, list[Competitor]] = {}
reports_db: dict[str, IndustryReport] = {}


# Request/Response Models
class AnalyzeCompanyRequest(BaseModel):
    url: str
    name: Optional[str] = None


class CreateUserRequest(BaseModel):
    email: str
    company_url: Optional[str] = None


class CheckoutRequest(BaseModel):
    user_id: str
    tier: SubscriptionTier
    billing_period: str = "monthly"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class UpgradeRequest(BaseModel):
    user_id: str
    new_tier: SubscriptionTier


# Health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# Company Analysis Endpoints
@app.post("/api/companies/analyze", response_model=Company)
async def analyze_company(request: AnalyzeCompanyRequest):
    """Analyze a company from its URL and store it."""
    try:
        company = await data_collection_service.analyze_company(request.url)
        if request.name:
            company.name = request.name
        companies_db[company.id] = company
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """Get a company by ID."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.get("/api/companies", response_model=list[Company])
async def list_companies():
    """List all analyzed companies."""
    return list(companies_db.values())


# Competitor Discovery Endpoints
@app.get("/api/companies/{company_id}/competitors", response_model=list[Competitor])
async def discover_competitors(
    company_id: str,
    limit: int = Query(default=5, ge=1, le=20)
):
    """Discover competitors for a company."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if company_id in competitors_db:
        return competitors_db[company_id][:limit]
    
    try:
        competitors = await data_collection_service.discover_competitors(company, limit)
        competitors_db[company_id] = competitors
        return competitors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Intelligence Feed Endpoints
@app.get("/api/companies/{company_id}/feed", response_model=list[IntelligenceFeedItem])
async def get_intelligence_feed(
    company_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    type_filter: Optional[str] = Query(default=None, description="Filter by type"),
    importance: Optional[str] = Query(default=None, description="Filter by importance")
):
    """Get the intelligence feed for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    if not competitors:
        competitors = await data_collection_service.discover_competitors(company, 5)
        competitors_db[company_id] = competitors
    
    try:
        feed = await data_collection_service.get_intelligence_feed(company, competitors, limit)
        
        if type_filter:
            feed = [item for item in feed if item.type == type_filter]
        if importance:
            feed = [item for item in feed if item.importance == importance]
        
        return feed[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Report Generation Endpoints
@app.post("/api/companies/{company_id}/reports", response_model=IndustryReport)
async def generate_report(
    company_id: str,
    days_back: int = Query(default=30, ge=7, le=90)
):
    """Generate a comprehensive industry report for a company."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    if not competitors:
        competitors = await data_collection_service.discover_competitors(company, 5)
        competitors_db[company_id] = competitors
    
    try:
        report = await report_generation_service.generate_report(company, competitors, days_back)
        reports_db[report.id] = report
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_id}", response_model=IndustryReport)
async def get_report(report_id: str):
    """Get a report by ID."""
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/api/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Download a report as PDF."""
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        pdf_bytes = report_generation_service.generate_pdf(report)
        filename = f"competitive_intel_report_{report.company_name.replace(' ', '_')}_{report.generated_date.strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{company_id}/reports", response_model=list[IndustryReport])
async def list_company_reports(company_id: str):
    """List all reports for a company."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_reports = [r for r in reports_db.values() if r.company_id == company_id]
    return sorted(company_reports, key=lambda x: x.generated_date, reverse=True)


# Billing Endpoints
@app.get("/api/billing/plans", response_model=list[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans."""
    return billing_service.get_plans()


@app.post("/api/billing/users", response_model=User)
async def create_user(request: CreateUserRequest):
    """Create a new user."""
    existing = billing_service.get_user_by_email(request.email)
    if existing:
        return existing
    return billing_service.create_user(request.email, request.company_url)


@app.get("/api/billing/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a user by ID."""
    user = billing_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/billing/checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Create a Stripe checkout session."""
    try:
        session = await billing_service.create_checkout_session(
            user_id=request.user_id,
            tier=request.tier,
            billing_period=request.billing_period,
            success_url=request.success_url or "http://localhost:5173/billing/success",
            cancel_url=request.cancel_url or "http://localhost:5173/billing/cancel"
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/billing/webhook")
async def stripe_webhook(
    payload: dict,
    stripe_signature: Optional[str] = Header(default=None)
):
    """Handle Stripe webhook events."""
    try:
        result = await billing_service.handle_webhook(payload, stripe_signature or "")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/billing/cancel/{user_id}")
async def cancel_subscription(user_id: str):
    """Cancel a user's subscription."""
    try:
        result = await billing_service.cancel_subscription(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/billing/users/{user_id}/limits")
async def get_user_limits(user_id: str):
    """Get the limits for a user based on their subscription."""
    return billing_service.get_user_limits(user_id)


@app.post("/api/billing/upgrade")
async def upgrade_subscription(request: UpgradeRequest):
    """Upgrade a user's subscription (demo endpoint)."""
    try:
        result = await billing_service.upgrade_subscription(
            user_id=request.user_id,
            new_tier=request.new_tier
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data Collection Endpoints
@app.get("/api/companies/{company_id}/employee-movements")
async def get_employee_movements(
    company_id: str,
    days_back: int = Query(default=30, ge=7, le=90)
):
    """Get employee movements for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    all_companies = [company.name] + [c.name for c in competitors]
    
    movements = await data_collection_service.get_employee_movements(all_companies, days_back)
    return movements


@app.get("/api/companies/{company_id}/job-postings")
async def get_job_postings(
    company_id: str,
    limit_per_company: int = Query(default=5, ge=1, le=20)
):
    """Get job postings for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    all_companies = [company.name] + [c.name for c in competitors]
    
    postings = await data_collection_service.get_job_postings(all_companies, limit_per_company)
    return postings


@app.get("/api/companies/{company_id}/funding-rounds")
async def get_funding_rounds(
    company_id: str,
    days_back: int = Query(default=90, ge=30, le=365)
):
    """Get funding rounds for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    all_companies = [company.name] + [c.name for c in competitors]
    
    rounds = await data_collection_service.get_funding_rounds(all_companies, days_back)
    return rounds


@app.get("/api/companies/{company_id}/product-launches")
async def get_product_launches(
    company_id: str,
    days_back: int = Query(default=60, ge=30, le=180)
):
    """Get product launches for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    all_companies = [company.name] + [c.name for c in competitors]
    
    launches = await data_collection_service.get_product_launches(all_companies, days_back)
    return launches


@app.get("/api/companies/{company_id}/news")
async def get_news_articles(
    company_id: str,
    days_back: int = Query(default=30, ge=7, le=90)
):
    """Get news articles for a company and its competitors."""
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    competitors = competitors_db.get(company_id, [])
    all_companies = [company.name] + [c.name for c in competitors]
    
    articles = await data_collection_service.get_news_articles(all_companies, days_back)
    return articles
