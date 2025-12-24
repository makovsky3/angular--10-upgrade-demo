import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid
import re
from typing import Optional
import asyncio

from app.models import (
    Company, Competitor, EmployeeMovement, JobPosting, 
    FundingRound, ProductLaunch, SocialMediaActivity, NewsArticle,
    IntelligenceFeedItem
)


class DataCollectionService:
    """Service for collecting competitive intelligence data from various sources."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def close(self):
        await self.client.aclose()
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        url = url.lower().strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else url
    
    async def analyze_company(self, url: str) -> Company:
        """Analyze a company from its URL."""
        domain = self.extract_domain(url)
        company_name = domain.split('.')[0].title()
        
        # Try to fetch company website for more info
        description = None
        try:
            response = await self.client.get(f"https://{domain}", headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to get title
                title_tag = soup.find('title')
                if title_tag:
                    company_name = title_tag.text.split('|')[0].split('-')[0].strip()
                
                # Try to get meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')
        except Exception:
            pass
        
        return Company(
            id=str(uuid.uuid4()),
            name=company_name,
            url=url,
            domain=domain,
            description=description,
            industry=self._infer_industry(domain, description)
        )
    
    def _infer_industry(self, domain: str, description: Optional[str]) -> str:
        """Infer industry from domain and description."""
        text = f"{domain} {description or ''}".lower()
        
        industry_keywords = {
            "Technology": ["tech", "software", "saas", "cloud", "ai", "ml", "data", "platform", "app"],
            "Finance": ["finance", "bank", "invest", "trading", "fintech", "payment", "crypto"],
            "Healthcare": ["health", "medical", "pharma", "biotech", "care", "hospital"],
            "E-commerce": ["shop", "store", "retail", "commerce", "buy", "sell", "marketplace"],
            "Education": ["edu", "learn", "course", "school", "university", "training"],
            "Marketing": ["marketing", "advertis", "brand", "media", "agency", "creative"],
            "Real Estate": ["real estate", "property", "home", "housing", "rent"],
            "Manufacturing": ["manufact", "industrial", "factory", "production"],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in text for kw in keywords):
                return industry
        
        return "Technology"  # Default
    
    async def discover_competitors(self, company: Company, limit: int = 5) -> list[Competitor]:
        """Discover competitors for a given company."""
        # In a real implementation, this would use APIs like Crunchbase, SimilarWeb, etc.
        # For the POC, we'll generate realistic mock competitors based on industry
        
        industry_competitors = {
            "Technology": [
                ("Acme Tech", "acmetech.com", "Enterprise software solutions"),
                ("CloudFirst", "cloudfirst.io", "Cloud infrastructure platform"),
                ("DataSync", "datasync.ai", "Data integration and analytics"),
                ("TechVenture", "techventure.com", "Technology consulting and development"),
                ("InnovateLabs", "innovatelabs.io", "Innovation and R&D services"),
            ],
            "Finance": [
                ("FinanceHub", "financehub.com", "Financial services platform"),
                ("PayFlow", "payflow.io", "Payment processing solutions"),
                ("InvestPro", "investpro.com", "Investment management platform"),
                ("CryptoTrade", "cryptotrade.io", "Cryptocurrency trading platform"),
                ("BankTech", "banktech.com", "Banking technology solutions"),
            ],
            "Healthcare": [
                ("HealthFirst", "healthfirst.com", "Healthcare management platform"),
                ("MedTech", "medtech.io", "Medical technology solutions"),
                ("CareConnect", "careconnect.com", "Patient care coordination"),
                ("PharmaSolutions", "pharmasolutions.com", "Pharmaceutical services"),
                ("BioInnovate", "bioinnovate.io", "Biotechnology research"),
            ],
            "E-commerce": [
                ("ShopNow", "shopnow.com", "Online retail platform"),
                ("MarketPlace", "marketplace.io", "Multi-vendor marketplace"),
                ("QuickBuy", "quickbuy.com", "Fast checkout solutions"),
                ("RetailTech", "retailtech.io", "Retail technology platform"),
                ("CommerceHub", "commercehub.com", "E-commerce infrastructure"),
            ],
        }
        
        competitors_data = industry_competitors.get(
            company.industry or "Technology", 
            industry_competitors["Technology"]
        )
        
        competitors = []
        for i, (name, domain, desc) in enumerate(competitors_data[:limit]):
            competitors.append(Competitor(
                id=str(uuid.uuid4()),
                name=name,
                url=f"https://{domain}",
                domain=domain,
                industry=company.industry,
                description=desc,
                similarity_score=0.95 - (i * 0.1)
            ))
        
        return competitors
    
    async def get_employee_movements(
        self, 
        companies: list[str], 
        days_back: int = 30
    ) -> list[EmployeeMovement]:
        """Get employee movements for specified companies."""
        # In production, this would use LinkedIn API or data providers
        # For POC, generate realistic mock data
        
        movements = []
        movement_templates = [
            ("hire", "Senior Engineer", "Tech Corp", "Software Engineer"),
            ("hire", "VP of Sales", "Sales Inc", "Director of Sales"),
            ("departure", "Product Manager", None, "Head of Product"),
            ("hire", "Data Scientist", "AI Labs", "ML Engineer"),
            ("promotion", "Engineering Manager", None, "Senior Engineer"),
            ("hire", "CFO", "Finance Co", "VP Finance"),
            ("departure", "CTO", None, "VP Engineering"),
            ("hire", "Marketing Director", "Brand Agency", "Marketing Manager"),
        ]
        
        for company in companies:
            for i, (move_type, new_role, prev_company, prev_role) in enumerate(movement_templates[:3]):
                days_ago = (i + 1) * 5
                movements.append(EmployeeMovement(
                    id=str(uuid.uuid4()),
                    person_name=f"John Smith {i+1}",
                    previous_company=prev_company,
                    previous_role=prev_role,
                    new_company=company,
                    new_role=new_role,
                    movement_type=move_type,
                    date=datetime.now() - timedelta(days=days_ago),
                    source="LinkedIn",
                    linkedin_url=f"https://linkedin.com/in/johnsmith{i+1}"
                ))
        
        return movements
    
    async def get_job_postings(
        self, 
        companies: list[str], 
        limit_per_company: int = 5
    ) -> list[JobPosting]:
        """Get job postings for specified companies."""
        # In production, this would scrape job boards or use APIs
        
        job_templates = [
            ("Senior Software Engineer", "Engineering", "Building next-gen platform features", "$150k-$200k"),
            ("Product Manager", "Product", "Leading product strategy and roadmap", "$130k-$170k"),
            ("Data Engineer", "Data", "Building data pipelines and infrastructure", "$140k-$180k"),
            ("DevOps Engineer", "Infrastructure", "Managing cloud infrastructure and CI/CD", "$130k-$160k"),
            ("Machine Learning Engineer", "AI/ML", "Developing ML models and systems", "$160k-$220k"),
            ("Sales Development Rep", "Sales", "Generating and qualifying leads", "$60k-$80k + commission"),
            ("Customer Success Manager", "Customer Success", "Ensuring customer satisfaction", "$80k-$110k"),
            ("Marketing Manager", "Marketing", "Driving growth and brand awareness", "$90k-$120k"),
        ]
        
        postings = []
        for company in companies:
            for i, (title, dept, desc, salary) in enumerate(job_templates[:limit_per_company]):
                days_ago = i * 3
                
                # Generate insights based on job type
                insights = self._generate_job_insights(title, dept)
                
                postings.append(JobPosting(
                    id=str(uuid.uuid4()),
                    company_name=company,
                    title=title,
                    location="San Francisco, CA (Remote)",
                    department=dept,
                    description=desc,
                    posted_date=datetime.now() - timedelta(days=days_ago),
                    url=f"https://jobs.example.com/{company.lower().replace(' ', '-')}/{i}",
                    salary_range=salary,
                    insights=insights
                ))
        
        return postings
    
    def _generate_job_insights(self, title: str, department: str) -> str:
        """Generate strategic insights from job posting."""
        insights_map = {
            "Engineering": "Indicates investment in product development and technical capabilities",
            "AI/ML": "Suggests focus on AI/ML capabilities, possibly new product features",
            "Data": "Points to data infrastructure investment, possibly for analytics or ML",
            "Sales": "Indicates growth phase and revenue expansion focus",
            "Marketing": "Suggests brand building or market expansion initiatives",
            "Product": "Points to product strategy evolution or new product lines",
            "Customer Success": "Indicates focus on retention and customer satisfaction",
            "Infrastructure": "Suggests scaling operations and technical infrastructure",
        }
        return insights_map.get(department, "General business expansion")
    
    async def get_funding_rounds(
        self, 
        companies: list[str], 
        days_back: int = 90
    ) -> list[FundingRound]:
        """Get funding rounds for specified companies."""
        # In production, this would use Crunchbase API or similar
        
        funding_templates = [
            ("Series A", 15000000, ["Sequoia Capital", "Andreessen Horowitz"]),
            ("Series B", 50000000, ["Tiger Global", "Coatue Management"]),
            ("Seed", 5000000, ["Y Combinator", "First Round Capital"]),
            ("Series C", 100000000, ["SoftBank Vision Fund", "General Atlantic"]),
        ]
        
        rounds = []
        for i, company in enumerate(companies):
            if i < len(funding_templates):
                round_type, amount, investors = funding_templates[i]
                rounds.append(FundingRound(
                    id=str(uuid.uuid4()),
                    company_name=company,
                    amount=amount,
                    currency="USD",
                    round_type=round_type,
                    date=datetime.now() - timedelta(days=(i + 1) * 15),
                    investors=investors,
                    valuation=amount * 5,
                    source="Crunchbase"
                ))
        
        return rounds
    
    async def get_product_launches(
        self, 
        companies: list[str], 
        days_back: int = 60
    ) -> list[ProductLaunch]:
        """Get product launches for specified companies."""
        
        launch_templates = [
            ("AI Assistant Pro", "AI-powered assistant for enterprise workflows", "AI/ML"),
            ("Cloud Platform 2.0", "Next-generation cloud infrastructure platform", "Infrastructure"),
            ("Analytics Dashboard", "Real-time business analytics and insights", "Analytics"),
            ("Mobile App Redesign", "Completely redesigned mobile experience", "Mobile"),
            ("API Gateway", "Unified API management and gateway solution", "Developer Tools"),
        ]
        
        launches = []
        for i, company in enumerate(companies):
            if i < len(launch_templates):
                name, desc, category = launch_templates[i]
                launches.append(ProductLaunch(
                    id=str(uuid.uuid4()),
                    company_name=company,
                    product_name=name,
                    description=desc,
                    launch_date=datetime.now() - timedelta(days=(i + 1) * 10),
                    category=category,
                    url=f"https://{company.lower().replace(' ', '')}.com/products/{name.lower().replace(' ', '-')}",
                    source="Product Hunt"
                ))
        
        return launches
    
    async def get_social_activity(
        self, 
        companies: list[str], 
        days_back: int = 30
    ) -> list[SocialMediaActivity]:
        """Get social media activity for specified companies."""
        
        activity_templates = [
            ("twitter", "Excited to announce our new partnership with @TechGiant!", 1500, "positive"),
            ("linkedin", "We're hiring! Join our growing team of innovators.", 800, "positive"),
            ("twitter", "Check out our latest blog post on industry trends.", 500, "neutral"),
            ("linkedin", "Proud to be recognized as a top workplace for 2024!", 2000, "positive"),
            ("twitter", "Thanks to all our customers for an amazing Q4!", 1200, "positive"),
        ]
        
        activities = []
        for company in companies:
            for i, (platform, content, engagement, sentiment) in enumerate(activity_templates[:3]):
                activities.append(SocialMediaActivity(
                    id=str(uuid.uuid4()),
                    company_name=company,
                    platform=platform,
                    content=content,
                    engagement_count=engagement,
                    posted_date=datetime.now() - timedelta(days=i * 2),
                    url=f"https://{platform}.com/{company.lower().replace(' ', '')}/status/{i}",
                    sentiment=sentiment
                ))
        
        return activities
    
    async def get_news_articles(
        self, 
        companies: list[str], 
        days_back: int = 30
    ) -> list[NewsArticle]:
        """Get news articles mentioning specified companies."""
        # In production, this would use news APIs like NewsAPI, Google News, etc.
        
        news_templates = [
            ("TechCrunch", "{company} Raises New Funding Round", "The company announced a significant funding round to accelerate growth."),
            ("Forbes", "{company} Named to Top 50 Innovators List", "Recognition for innovation and market leadership."),
            ("Bloomberg", "{company} Expands into European Markets", "Strategic expansion to capture new market opportunities."),
            ("VentureBeat", "{company} Launches AI-Powered Features", "New AI capabilities aim to transform user experience."),
            ("Business Insider", "{company} Hires Industry Veterans", "Key executive hires signal ambitious growth plans."),
        ]
        
        articles = []
        for company in companies:
            for i, (source, title_template, summary) in enumerate(news_templates[:3]):
                articles.append(NewsArticle(
                    id=str(uuid.uuid4()),
                    title=title_template.format(company=company),
                    summary=summary,
                    url=f"https://{source.lower().replace(' ', '')}.com/article/{uuid.uuid4().hex[:8]}",
                    source=source,
                    published_date=datetime.now() - timedelta(days=i * 5),
                    companies_mentioned=[company],
                    sentiment="positive"
                ))
        
        return articles
    
    async def get_intelligence_feed(
        self, 
        company: Company, 
        competitors: list[Competitor],
        limit: int = 50
    ) -> list[IntelligenceFeedItem]:
        """Get a unified intelligence feed for a company and its competitors."""
        
        all_companies = [company.name] + [c.name for c in competitors]
        
        # Collect all data in parallel
        employee_movements, job_postings, funding_rounds, product_launches, social_activity, news_articles = await asyncio.gather(
            self.get_employee_movements(all_companies),
            self.get_job_postings(all_companies),
            self.get_funding_rounds(all_companies),
            self.get_product_launches(all_companies),
            self.get_social_activity(all_companies),
            self.get_news_articles(all_companies)
        )
        
        feed_items = []
        
        # Convert employee movements to feed items
        for em in employee_movements:
            importance = "high" if em.movement_type == "departure" or "VP" in em.new_role or "C" in em.new_role[:1] else "medium"
            feed_items.append(IntelligenceFeedItem(
                id=em.id,
                type="employee_movement",
                title=f"{em.person_name} joins {em.new_company} as {em.new_role}",
                summary=f"Previously {em.previous_role} at {em.previous_company}" if em.previous_company else "New hire",
                date=em.date,
                company_name=em.new_company,
                importance=importance,
                source=em.source,
                url=em.linkedin_url,
                raw_data=em.model_dump()
            ))
        
        # Convert job postings to feed items
        for jp in job_postings:
            importance = "high" if "VP" in jp.title or "Director" in jp.title or "Head" in jp.title else "medium"
            feed_items.append(IntelligenceFeedItem(
                id=jp.id,
                type="job_posting",
                title=f"{jp.company_name} hiring {jp.title}",
                summary=jp.insights or jp.description or "",
                date=jp.posted_date,
                company_name=jp.company_name,
                importance=importance,
                source="Job Board",
                url=jp.url,
                raw_data=jp.model_dump()
            ))
        
        # Convert funding rounds to feed items
        for fr in funding_rounds:
            feed_items.append(IntelligenceFeedItem(
                id=fr.id,
                type="funding",
                title=f"{fr.company_name} raises ${fr.amount/1000000:.1f}M {fr.round_type}",
                summary=f"Investors: {', '.join(fr.investors)}",
                date=fr.date,
                company_name=fr.company_name,
                importance="high",
                source=fr.source,
                raw_data=fr.model_dump()
            ))
        
        # Convert product launches to feed items
        for pl in product_launches:
            feed_items.append(IntelligenceFeedItem(
                id=pl.id,
                type="product_launch",
                title=f"{pl.company_name} launches {pl.product_name}",
                summary=pl.description,
                date=pl.launch_date,
                company_name=pl.company_name,
                importance="high",
                source=pl.source,
                url=pl.url,
                raw_data=pl.model_dump()
            ))
        
        # Convert social activity to feed items
        for sa in social_activity:
            feed_items.append(IntelligenceFeedItem(
                id=sa.id,
                type="social",
                title=f"{sa.company_name} on {sa.platform.title()}",
                summary=sa.content,
                date=sa.posted_date,
                company_name=sa.company_name,
                importance="low",
                source=sa.platform.title(),
                url=sa.url,
                raw_data=sa.model_dump()
            ))
        
        # Convert news articles to feed items
        for na in news_articles:
            feed_items.append(IntelligenceFeedItem(
                id=na.id,
                type="news",
                title=na.title,
                summary=na.summary,
                date=na.published_date,
                company_name=na.companies_mentioned[0] if na.companies_mentioned else "Unknown",
                importance="medium",
                source=na.source,
                url=na.url,
                raw_data=na.model_dump()
            ))
        
        # Sort by date and limit
        feed_items.sort(key=lambda x: x.date, reverse=True)
        return feed_items[:limit]


# Singleton instance
data_collection_service = DataCollectionService()
