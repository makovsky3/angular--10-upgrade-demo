from datetime import datetime, timedelta
from io import BytesIO
import uuid

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.models import (
    Company, Competitor, IndustryReport, EmployeeMovement,
    JobPosting, FundingRound, ProductLaunch, SocialMediaActivity, NewsArticle
)
from app.services.data_collection import data_collection_service


class ReportGenerationService:
    """Service for generating competitive intelligence reports."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d')
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2d3748')
        ))
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor('#4a5568')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=5,
            textColor=colors.HexColor('#2d3748')
        ))
        self.styles.add(ParagraphStyle(
            name='Insight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20,
            textColor=colors.HexColor('#2b6cb0'),
            backColor=colors.HexColor('#ebf8ff')
        ))
    
    async def generate_report(
        self,
        company: Company,
        competitors: list[Competitor],
        days_back: int = 30
    ) -> IndustryReport:
        """Generate a comprehensive industry report."""
        
        all_companies = [company.name] + [c.name for c in competitors]
        
        # Collect all intelligence data
        employee_movements = await data_collection_service.get_employee_movements(all_companies, days_back)
        job_postings = await data_collection_service.get_job_postings(all_companies)
        funding_rounds = await data_collection_service.get_funding_rounds(all_companies, days_back * 3)
        product_launches = await data_collection_service.get_product_launches(all_companies, days_back * 2)
        social_activity = await data_collection_service.get_social_activity(all_companies, days_back)
        news_articles = await data_collection_service.get_news_articles(all_companies, days_back)
        
        # Generate insights
        key_insights = self._generate_key_insights(
            employee_movements, job_postings, funding_rounds, 
            product_launches, news_articles, company, competitors
        )
        
        recommendations = self._generate_recommendations(
            employee_movements, job_postings, funding_rounds,
            product_launches, company, competitors
        )
        
        executive_summary = self._generate_executive_summary(
            company, competitors, employee_movements, job_postings,
            funding_rounds, product_launches, news_articles
        )
        
        competitor_analysis = [
            {
                "name": c.name,
                "domain": c.domain,
                "similarity_score": c.similarity_score,
                "recent_hires": len([em for em in employee_movements if em.new_company == c.name]),
                "open_positions": len([jp for jp in job_postings if jp.company_name == c.name]),
                "recent_funding": next((fr for fr in funding_rounds if fr.company_name == c.name), None),
                "recent_launches": [pl for pl in product_launches if pl.company_name == c.name]
            }
            for c in competitors
        ]
        
        return IndustryReport(
            id=str(uuid.uuid4()),
            company_id=company.id,
            company_name=company.name,
            generated_date=datetime.now(),
            period_start=datetime.now() - timedelta(days=days_back),
            period_end=datetime.now(),
            executive_summary=executive_summary,
            competitor_analysis=competitor_analysis,
            employee_movements=employee_movements,
            job_postings=job_postings,
            funding_rounds=funding_rounds,
            product_launches=product_launches,
            social_activity=social_activity,
            news_coverage=news_articles,
            key_insights=key_insights,
            recommendations=recommendations
        )
    
    def _generate_executive_summary(
        self,
        company: Company,
        competitors: list[Competitor],
        employee_movements: list[EmployeeMovement],
        job_postings: list[JobPosting],
        funding_rounds: list[FundingRound],
        product_launches: list[ProductLaunch],
        news_articles: list[NewsArticle]
    ) -> str:
        """Generate executive summary for the report."""
        
        total_funding = sum(fr.amount or 0 for fr in funding_rounds)
        total_hires = len([em for em in employee_movements if em.movement_type == "hire"])
        total_departures = len([em for em in employee_movements if em.movement_type == "departure"])
        
        summary = f"""This report provides a comprehensive analysis of {company.name} and {len(competitors)} key competitors in the {company.industry or 'technology'} industry.

Key Highlights:
- Tracked {len(competitors)} competitors with varying similarity scores
- Identified {total_hires} new hires and {total_departures} departures across the competitive landscape
- Monitored {len(job_postings)} open positions indicating growth areas
- Recorded ${total_funding/1000000:.1f}M in total funding activity
- Tracked {len(product_launches)} product launches and updates
- Analyzed {len(news_articles)} news articles for market sentiment

The competitive landscape shows significant activity in hiring and product development, suggesting an active growth phase across the industry."""
        
        return summary
    
    def _generate_key_insights(
        self,
        employee_movements: list[EmployeeMovement],
        job_postings: list[JobPosting],
        funding_rounds: list[FundingRound],
        product_launches: list[ProductLaunch],
        news_articles: list[NewsArticle],
        company: Company,
        competitors: list[Competitor]
    ) -> list[str]:
        """Generate key insights from the collected data."""
        
        insights = []
        
        # Hiring trends insight
        engineering_jobs = len([jp for jp in job_postings if "Engineer" in jp.title or "Developer" in jp.title])
        if engineering_jobs > 5:
            insights.append(f"High engineering hiring activity ({engineering_jobs} positions) indicates significant product development investment across competitors.")
        
        # Executive movement insight
        exec_moves = [em for em in employee_movements if any(title in em.new_role for title in ["VP", "Director", "Chief", "Head"])]
        if exec_moves:
            insights.append(f"Notable executive movements detected: {len(exec_moves)} senior hires/departures may signal strategic shifts.")
        
        # Funding insight
        if funding_rounds:
            total_funding = sum(fr.amount or 0 for fr in funding_rounds)
            insights.append(f"${total_funding/1000000:.1f}M raised across {len(funding_rounds)} funding rounds indicates strong investor confidence in the sector.")
        
        # Product launch insight
        ai_launches = [pl for pl in product_launches if "AI" in pl.product_name or "ML" in pl.description]
        if ai_launches:
            insights.append(f"AI/ML focus evident with {len(ai_launches)} AI-related product launches, suggesting industry-wide AI adoption trend.")
        
        # Sales hiring insight
        sales_jobs = len([jp for jp in job_postings if "Sales" in jp.title or "Business Development" in jp.title])
        if sales_jobs > 3:
            insights.append(f"Increased sales hiring ({sales_jobs} positions) suggests competitors are in growth/expansion mode.")
        
        # Default insights if none generated
        if not insights:
            insights = [
                "Competitive landscape remains stable with moderate activity across all tracked metrics.",
                "No significant strategic shifts detected in the reporting period.",
                "Continue monitoring for emerging trends and competitive moves."
            ]
        
        return insights
    
    def _generate_recommendations(
        self,
        employee_movements: list[EmployeeMovement],
        job_postings: list[JobPosting],
        funding_rounds: list[FundingRound],
        product_launches: list[ProductLaunch],
        company: Company,
        competitors: list[Competitor]
    ) -> list[str]:
        """Generate strategic recommendations based on competitive intelligence."""
        
        recommendations = []
        
        # Based on competitor hiring
        engineering_heavy = len([jp for jp in job_postings if "Engineer" in jp.title]) > 5
        if engineering_heavy:
            recommendations.append("Consider accelerating your engineering hiring to maintain competitive parity in product development.")
        
        # Based on funding activity
        if funding_rounds:
            recommendations.append("With significant funding activity in the market, consider your capital strategy to ensure competitive positioning.")
        
        # Based on product launches
        if product_launches:
            recommendations.append("Monitor competitor product launches closely and consider accelerating your product roadmap in response.")
        
        # Based on executive movements
        departures = [em for em in employee_movements if em.movement_type == "departure"]
        if departures:
            recommendations.append("Executive departures at competitors may present recruitment opportunities for experienced talent.")
        
        # General recommendations
        recommendations.extend([
            "Maintain regular competitive intelligence monitoring to stay ahead of market shifts.",
            "Consider engaging with industry analysts to understand broader market trends.",
            "Review your positioning against top competitors quarterly."
        ])
        
        return recommendations[:5]  # Limit to top 5
    
    def generate_pdf(self, report: IndustryReport) -> bytes:
        """Generate a PDF version of the report."""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            f"Competitive Intelligence Report",
            self.styles['CustomTitle']
        ))
        story.append(Paragraph(
            f"{report.company_name}",
            self.styles['CustomTitle']
        ))
        story.append(Paragraph(
            f"Report Period: {report.period_start.strftime('%B %d, %Y')} - {report.period_end.strftime('%B %d, %Y')}",
            self.styles['CustomBodyText']
        ))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        for para in report.executive_summary.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['CustomBodyText']))
        story.append(Spacer(1, 15))
        
        # Key Insights
        story.append(Paragraph("Key Insights", self.styles['SectionHeader']))
        for insight in report.key_insights:
            story.append(Paragraph(f"• {insight}", self.styles['Insight']))
        story.append(Spacer(1, 15))
        
        # Competitor Analysis
        story.append(Paragraph("Competitor Analysis", self.styles['SectionHeader']))
        if report.competitor_analysis:
            table_data = [["Company", "Similarity", "Open Positions", "Recent Hires"]]
            for comp in report.competitor_analysis:
                table_data.append([
                    comp["name"],
                    f"{comp['similarity_score']:.0%}",
                    str(comp["open_positions"]),
                    str(comp["recent_hires"])
                ])
            
            table = Table(table_data, colWidths=[2*inch, 1.2*inch, 1.3*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(table)
        story.append(Spacer(1, 15))
        
        # Funding Rounds
        if report.funding_rounds:
            story.append(Paragraph("Funding Activity", self.styles['SectionHeader']))
            for fr in report.funding_rounds[:5]:
                story.append(Paragraph(
                    f"<b>{fr.company_name}</b> - {fr.round_type}: ${fr.amount/1000000:.1f}M",
                    self.styles['CustomBodyText']
                ))
                story.append(Paragraph(
                    f"Investors: {', '.join(fr.investors)}",
                    self.styles['CustomBodyText']
                ))
            story.append(Spacer(1, 15))
        
        # Product Launches
        if report.product_launches:
            story.append(Paragraph("Product Launches", self.styles['SectionHeader']))
            for pl in report.product_launches[:5]:
                story.append(Paragraph(
                    f"<b>{pl.company_name}</b> - {pl.product_name}",
                    self.styles['CustomBodyText']
                ))
                story.append(Paragraph(pl.description, self.styles['CustomBodyText']))
            story.append(Spacer(1, 15))
        
        # Employee Movements
        if report.employee_movements:
            story.append(Paragraph("Notable Employee Movements", self.styles['SectionHeader']))
            for em in report.employee_movements[:10]:
                move_text = f"<b>{em.person_name}</b> joined {em.new_company} as {em.new_role}"
                if em.previous_company:
                    move_text += f" (from {em.previous_company})"
                story.append(Paragraph(move_text, self.styles['CustomBodyText']))
            story.append(Spacer(1, 15))
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        for i, rec in enumerate(report.recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBodyText']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
report_generation_service = ReportGenerationService()
