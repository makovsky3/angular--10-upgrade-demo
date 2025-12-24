from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class CompanyInput(BaseModel):
    url: str
    name: Optional[str] = None


class Company(BaseModel):
    id: str
    name: str
    url: str
    domain: str
    industry: Optional[str] = None
    description: Optional[str] = None
    employee_count: Optional[int] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    logo_url: Optional[str] = None


class Competitor(BaseModel):
    id: str
    name: str
    url: str
    domain: str
    industry: Optional[str] = None
    description: Optional[str] = None
    similarity_score: float = 0.0


class EmployeeMovement(BaseModel):
    id: str
    person_name: str
    previous_company: Optional[str] = None
    previous_role: Optional[str] = None
    new_company: str
    new_role: str
    movement_type: str  # "hire", "departure", "promotion"
    date: datetime
    source: str
    linkedin_url: Optional[str] = None


class JobPosting(BaseModel):
    id: str
    company_name: str
    title: str
    location: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    posted_date: datetime
    url: str
    salary_range: Optional[str] = None
    insights: Optional[str] = None  # What this job posting reveals about strategy


class FundingRound(BaseModel):
    id: str
    company_name: str
    amount: Optional[float] = None
    currency: str = "USD"
    round_type: str  # "seed", "series_a", "series_b", etc.
    date: datetime
    investors: list[str] = []
    valuation: Optional[float] = None
    source: str


class ProductLaunch(BaseModel):
    id: str
    company_name: str
    product_name: str
    description: str
    launch_date: datetime
    category: Optional[str] = None
    url: Optional[str] = None
    source: str


class SocialMediaActivity(BaseModel):
    id: str
    company_name: str
    platform: str  # "twitter", "linkedin"
    content: str
    engagement_count: int = 0
    posted_date: datetime
    url: Optional[str] = None
    sentiment: Optional[str] = None  # "positive", "negative", "neutral"


class NewsArticle(BaseModel):
    id: str
    title: str
    summary: str
    url: str
    source: str
    published_date: datetime
    companies_mentioned: list[str] = []
    sentiment: Optional[str] = None


class IntelligenceFeedItem(BaseModel):
    id: str
    type: str  # "employee_movement", "job_posting", "funding", "product_launch", "social", "news"
    title: str
    summary: str
    date: datetime
    company_name: str
    importance: str = "medium"  # "low", "medium", "high"
    source: str
    url: Optional[str] = None
    raw_data: dict = {}


class IndustryReport(BaseModel):
    id: str
    company_id: str
    company_name: str
    generated_date: datetime
    period_start: datetime
    period_end: datetime
    executive_summary: str
    competitor_analysis: list[dict] = []
    employee_movements: list[EmployeeMovement] = []
    job_postings: list[JobPosting] = []
    funding_rounds: list[FundingRound] = []
    product_launches: list[ProductLaunch] = []
    social_activity: list[SocialMediaActivity] = []
    news_coverage: list[NewsArticle] = []
    key_insights: list[str] = []
    recommendations: list[str] = []


class User(BaseModel):
    id: str
    email: str
    company_url: Optional[str] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    stripe_customer_id: Optional[str] = None
    created_at: datetime


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    tier: SubscriptionTier
    price_monthly: float
    price_yearly: float
    features: list[str]
    competitor_limit: int
    report_frequency: str  # "weekly", "monthly"
    api_access: bool = False
