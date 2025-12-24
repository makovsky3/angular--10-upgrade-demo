import os
import stripe
from datetime import datetime
import uuid
from typing import Optional

from app.models import User, SubscriptionTier, SubscriptionPlan


# Initialize Stripe (will use env var in production)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")


# Subscription plans
SUBSCRIPTION_PLANS = [
    SubscriptionPlan(
        id="plan_free",
        name="Free",
        tier=SubscriptionTier.FREE,
        price_monthly=0,
        price_yearly=0,
        features=[
            "Track 1 company",
            "Basic competitor discovery",
            "Monthly email digest",
            "Limited feed access"
        ],
        competitor_limit=3,
        report_frequency="monthly",
        api_access=False
    ),
    SubscriptionPlan(
        id="plan_starter",
        name="Starter",
        tier=SubscriptionTier.STARTER,
        price_monthly=49,
        price_yearly=470,
        features=[
            "Track up to 3 companies",
            "5 competitors per company",
            "Weekly reports",
            "Full feed access",
            "Email alerts",
            "PDF report exports"
        ],
        competitor_limit=5,
        report_frequency="weekly",
        api_access=False
    ),
    SubscriptionPlan(
        id="plan_pro",
        name="Pro",
        tier=SubscriptionTier.PRO,
        price_monthly=149,
        price_yearly=1430,
        features=[
            "Track up to 10 companies",
            "15 competitors per company",
            "Daily reports",
            "Real-time feed",
            "Priority email alerts",
            "PDF & PowerPoint exports",
            "Custom report branding",
            "Slack integration"
        ],
        competitor_limit=15,
        report_frequency="daily",
        api_access=True
    ),
    SubscriptionPlan(
        id="plan_enterprise",
        name="Enterprise",
        tier=SubscriptionTier.ENTERPRISE,
        price_monthly=499,
        price_yearly=4790,
        features=[
            "Unlimited companies",
            "Unlimited competitors",
            "Real-time monitoring",
            "Custom integrations",
            "Dedicated support",
            "API access",
            "White-label reports",
            "Team collaboration",
            "Custom data sources"
        ],
        competitor_limit=999,
        report_frequency="realtime",
        api_access=True
    )
]


class BillingService:
    """Service for handling Stripe billing and subscriptions."""
    
    def __init__(self):
        self.plans = {plan.tier: plan for plan in SUBSCRIPTION_PLANS}
        # In-memory user storage for POC
        self.users: dict[str, User] = {}
    
    def get_plans(self) -> list[SubscriptionPlan]:
        """Get all available subscription plans."""
        return SUBSCRIPTION_PLANS
    
    def get_plan(self, tier: SubscriptionTier) -> Optional[SubscriptionPlan]:
        """Get a specific subscription plan."""
        return self.plans.get(tier)
    
    def create_user(self, email: str, company_url: Optional[str] = None) -> User:
        """Create a new user with free tier."""
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            company_url=company_url,
            subscription_tier=SubscriptionTier.FREE,
            created_at=datetime.now()
        )
        self.users[user.id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    async def create_checkout_session(
        self,
        user_id: str,
        tier: SubscriptionTier,
        billing_period: str = "monthly",
        success_url: str = "http://localhost:5173/billing/success",
        cancel_url: str = "http://localhost:5173/billing/cancel"
    ) -> dict:
        """Create a Stripe checkout session for subscription."""
        
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        plan = self.get_plan(tier)
        if not plan:
            raise ValueError("Invalid subscription tier")
        
        if plan.price_monthly == 0:
            raise ValueError("Cannot checkout for free tier")
        
        price = plan.price_yearly if billing_period == "yearly" else plan.price_monthly
        
        # For POC, return mock checkout session
        # In production, this would create a real Stripe checkout session
        checkout_session = {
            "id": f"cs_{uuid.uuid4().hex}",
            "url": f"https://checkout.stripe.com/pay/cs_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "tier": tier.value,
            "price": price,
            "billing_period": billing_period,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "status": "open"
        }
        
        return checkout_session
    
    async def handle_webhook(self, payload: dict, signature: str) -> dict:
        """Handle Stripe webhook events."""
        
        event_type = payload.get("type", "")
        
        if event_type == "checkout.session.completed":
            # Update user subscription
            session = payload.get("data", {}).get("object", {})
            customer_email = session.get("customer_email")
            
            user = self.get_user_by_email(customer_email)
            if user:
                # In production, parse the subscription tier from metadata
                user.subscription_tier = SubscriptionTier.STARTER
                user.stripe_customer_id = session.get("customer")
            
            return {"status": "success", "message": "Subscription activated"}
        
        elif event_type == "customer.subscription.updated":
            # Handle subscription updates
            return {"status": "success", "message": "Subscription updated"}
        
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription = payload.get("data", {}).get("object", {})
            customer_id = subscription.get("customer")
            
            for user in self.users.values():
                if user.stripe_customer_id == customer_id:
                    user.subscription_tier = SubscriptionTier.FREE
                    break
            
            return {"status": "success", "message": "Subscription cancelled"}
        
        return {"status": "ignored", "message": f"Unhandled event type: {event_type}"}
    
    async def cancel_subscription(self, user_id: str) -> dict:
        """Cancel a user's subscription."""
        
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.subscription_tier == SubscriptionTier.FREE:
            raise ValueError("User is on free tier")
        
        # In production, this would cancel the Stripe subscription
        user.subscription_tier = SubscriptionTier.FREE
        user.stripe_customer_id = None
        
        return {"status": "success", "message": "Subscription cancelled"}
    
    def get_user_limits(self, user_id: str) -> dict:
        """Get the limits for a user based on their subscription."""
        
        user = self.get_user(user_id)
        if not user:
            # Return free tier limits for unknown users
            plan = self.get_plan(SubscriptionTier.FREE)
        else:
            plan = self.get_plan(user.subscription_tier)
        
        if not plan:
            plan = self.get_plan(SubscriptionTier.FREE)
        
        return {
            "competitor_limit": plan.competitor_limit,
            "report_frequency": plan.report_frequency,
            "api_access": plan.api_access,
            "features": plan.features
        }
    
    async def upgrade_subscription(
        self,
        user_id: str,
        new_tier: SubscriptionTier
    ) -> dict:
        """Upgrade a user's subscription (for demo purposes)."""
        
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.subscription_tier = new_tier
        
        return {
            "status": "success",
            "message": f"Upgraded to {new_tier.value}",
            "new_tier": new_tier.value
        }


# Singleton instance
billing_service = BillingService()
