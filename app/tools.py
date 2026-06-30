"""
tools.py — Deterministic tools for the Northstar Insights RAG assistant.

Each tool is a plain Python function with a Pydantic input schema.
Tool definitions (for LLM function-calling) are exported as TOOL_DEFINITIONS.
"""

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, field_validator

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TICKETS_PATH = DATA_DIR / "support_tickets.csv"

PLAN_PRICES: dict[str, float] = {
    "starter": 2_000,
    "growth": 6_500,
    "enterprise": 15_000,
}

IMPLEMENTATION_FEES: dict[str, float] = {
    "starter": 3_000,
    "growth": 8_000,
    "enterprise": 20_000,
}

DISCOUNTS: dict[str, float] = {
    "annual": 0.12,
    "nonprofit": 0.20,
}

def _load_tickets() -> list[dict]:
    tickets = []
    with TICKETS_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tickets.append({k.strip(): v.strip() for k, v in row.items()})
    return tickets


# Tool 1: Pricing Calculator

class PricingInput(BaseModel):
    plan: str
    contract: str = "monthly"          # "monthly" | "annual"
    customer_type: str = "standard"    # "standard" | "nonprofit"

    @field_validator("plan")
    @classmethod
    def validate_plan(cls, v: str) -> str:
        normalized = v.lower()
        if normalized not in PLAN_PRICES:
            raise ValueError(
                f"Unknown plan '{v}'. Valid plans: {list(PLAN_PRICES.keys())}"
            )
        return normalized

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v: str) -> str:
        normalized = v.lower()
        if normalized not in ("monthly", "annual"):
            raise ValueError("contract must be 'monthly' or 'annual'")
        return normalized

    @field_validator("customer_type")
    @classmethod
    def validate_customer_type(cls, v: str) -> str:
        normalized = v.lower()
        if normalized not in ("standard", "nonprofit"):
            raise ValueError("customer_type must be 'standard' or 'nonprofit'")
        return normalized


def calculate_pricing(plan: str, contract: str = "monthly", customer_type: str = "standard") -> dict:
    """
    Calculate monthly price, annual subscription, implementation fee,
    and first-year total for a given plan, contract type, and customer type.

    Discounts cannot be stacked — the highest applicable discount is used.
    """
    inputs = PricingInput(plan=plan, contract=contract, customer_type=customer_type)

    base_monthly = PLAN_PRICES[inputs.plan]
    impl_fee = IMPLEMENTATION_FEES[inputs.plan]

    # Determine eligible discounts
    eligible: dict[str, float] = {}
    if inputs.contract == "annual":
        eligible["annual"] = DISCOUNTS["annual"]
    if inputs.customer_type == "nonprofit":
        eligible["nonprofit"] = DISCOUNTS["nonprofit"]

    # Apply highest single discount (no stacking)
    if eligible:
        best_label = max(eligible, key=lambda k: eligible[k])
        applied_discount_pct = eligible[best_label]
        applied_discount_label = best_label
    else:
        applied_discount_pct = 0.0
        applied_discount_label = "none"

    discounted_monthly = round(base_monthly * (1 - applied_discount_pct), 2)

    if inputs.contract == "annual":
        annual_subscription = round(discounted_monthly * 12, 2)
    else:
        annual_subscription = round(discounted_monthly * 12, 2)  # projected

    first_year_total = round(annual_subscription + impl_fee, 2)

    return {
        "plan": inputs.plan.title(),
        "contract": inputs.contract,
        "customer_type": inputs.customer_type,
        "base_monthly_price_usd": base_monthly,
        "eligible_discounts": {k: f"{int(v * 100)}%" for k, v in eligible.items()},
        "applied_discount": applied_discount_label,
        "applied_discount_pct": f"{int(applied_discount_pct * 100)}%",
        "discounted_monthly_price_usd": discounted_monthly,
        "annual_subscription_usd": annual_subscription,
        "implementation_fee_usd": impl_fee,
        "first_year_total_usd": first_year_total,
    }


# Tool 2: Support Ticket Lookup

class TicketLookupInput(BaseModel):
    customer: Optional[str] = None
    status: Optional[str] = None       # "Open" | "In Progress" | "Resolved"
    priority: Optional[str] = None     # "Low" | "Medium" | "High" | "Critical"
    category: Optional[str] = None


def lookup_tickets(
    customer: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """
    Filter support tickets by customer, status, priority, and/or category.
    All filters are case-insensitive. Returns matching tickets as structured JSON.
    """
    TicketLookupInput(customer=customer, status=status, priority=priority, category=category)

    tickets = _load_tickets()
    results = []

    for t in tickets:
        if customer and t["customer"].lower() != customer.lower():
            continue
        if status and t["status"].lower() != status.lower():
            continue
        if priority and t["priority"].lower() != priority.lower():
            continue
        if category and t["category"].lower() != category.lower():
            continue
        results.append(t)

    return {
        "filters": {
            "customer": customer,
            "status": status,
            "priority": priority,
            "category": category,
        },
        "count": len(results),
        "tickets": results,
    }


# Tool 3: Renewal Risk Classifier

# Renewal dates from sales_notes.md
RENEWAL_DATES: dict[str, str] = {
    "greenmart": "2026-02-28",
    "urbanbasket": "2026-01-15",
    "stylehub": "2026-04-30",
}

class RenewalRiskInput(BaseModel):
    customer: str

    @field_validator("customer")
    @classmethod
    def validate_customer(cls, v: str) -> str:
        if v.lower() not in RENEWAL_DATES:
            raise ValueError(
                f"Unknown customer '{v}'. Known customers: {list(RENEWAL_DATES.keys())}"
            )
        return v


def classify_renewal_risk(customer: str) -> dict:
    """
    Classify renewal risk as Low, Medium, or High.

    Rules:
      High   — at least one Critical open ticket
      Medium — two or more open tickets OR renewal within 90 days
      Low    — otherwise
    """
    RenewalRiskInput(customer=customer)

    tickets = _load_tickets()
    customer_tickets = [
        t for t in tickets if t["customer"].lower() == customer.lower()
    ]
    open_tickets = [t for t in customer_tickets if t["status"].lower() == "open"]
    critical_open = [t for t in open_tickets if t["priority"].lower() == "critical"]

    renewal_str = RENEWAL_DATES[customer.lower()]
    renewal_date = datetime.strptime(renewal_str, "%Y-%m-%d").date()
    today = date.today()
    days_to_renewal = (renewal_date - today).days

    reasons = []
    risk = "Low"

    # High risk: any Critical open ticket
    if critical_open:
        risk = "High"
        for t in critical_open:
            reasons.append(
                f"Critical open ticket {t['ticket_id']}: {t['summary']}"
            )

    # Medium risk: 2+ open tickets or renewal within 90 days
    if risk != "High":
        if len(open_tickets) >= 2:
            risk = "Medium"
            reasons.append(
                f"{len(open_tickets)} open tickets: "
                + ", ".join(t["ticket_id"] for t in open_tickets)
            )
        if days_to_renewal <= 90:
            risk = max(risk, "Medium")  # doesn't downgrade High
            reasons.append(
                f"Renewal date {renewal_str} is {days_to_renewal} days away (within 90-day window)"
            )

    if not reasons:
        reasons.append("No critical tickets, fewer than 2 open tickets, renewal not imminent")

    return {
        "customer": customer.title(),
        "risk": risk,
        "renewal_date": renewal_str,
        "days_to_renewal": days_to_renewal,
        "open_ticket_count": len(open_tickets),
        "reasons": reasons,
    }


# Tool 4: Project Release Finder

# Structured project data from project_updates.md
PROJECTS = [
    {
        "name": "Shopify Connector Stabilization",
        "owner": "Integrations Team",
        "status": "In Progress",
        "target_release": "2025-11-15",
        "relevant_customers": ["urbanbasket"],
        "relevant_categories": ["integrations", "shopify"],
        "description": "Addressing timeout issues during high-volume nightly syncs.",
    },
    {
        "name": "Forecast Refresh Reliability",
        "owner": "ML Platform Team",
        "status": "In Progress",
        "target_release": "2025-12-01",
        "relevant_customers": ["greenmart"],
        "relevant_categories": ["forecasting"],
        "description": "Improving retry logic for weekly forecast refresh jobs.",
    },
    {
        "name": "Dashboard Permissions Redesign",
        "owner": "Product Experience Team",
        "status": "Planned",
        "target_release": "2026-01-20",
        "relevant_customers": ["stylehub"],
        "relevant_categories": ["dashboards", "permissions"],
        "description": "More granular export permissions for viewer and analyst roles.",
    },
    {
        "name": "Inventory Alert Calibration",
        "owner": "Applied AI Team",
        "status": "In Progress",
        "target_release": "2025-12-10",
        "relevant_customers": ["greenmart"],
        "relevant_categories": ["inventory alerts"],
        "description": "Recalibrating stockout risk thresholds to reduce false positive alerts for seasonal SKUs.",
    },
]


def find_relevant_projects(customer: Optional[str] = None, category: Optional[str] = None) -> dict:
    """
    Find internal projects relevant to a customer's pain points or support tickets.
    Filters by customer name and/or category keyword.
    """
    results = []

    for project in PROJECTS:
        match = False
        why = []

        if customer and customer.lower() in project["relevant_customers"]:
            match = True
            why.append(f"Directly relevant to {customer.title()}")

        if category:
            for cat in project["relevant_categories"]:
                if category.lower() in cat.lower():
                    match = True
                    why.append(f"Matches category '{category}'")
                    break

        if not customer and not category:
            match = True
            why.append("No filter applied — returning all projects")

        if match:
            results.append({
                "project": project["name"],
                "owner": project["owner"],
                "status": project["status"],
                "target_release": project["target_release"],
                "description": project["description"],
                "relevance": why,
            })

    # Sort by target release date ascending
    results.sort(key=lambda x: x["target_release"])

    return {
        "filters": {"customer": customer, "category": category},
        "count": len(results),
        "projects": results,
    }


# Tool 5: PTO Eligibility Checker

# Policy constants from hr_policy.md
PTO_DAYS_PER_YEAR = 20
PTO_CARRYOVER_MAX = 5
SICK_DAYS_PER_YEAR = 8
ADVANCE_NOTICE_DAYS = 10        # business days required for vacations > 3 consecutive days
ADVANCE_NOTICE_THRESHOLD = 3    # consecutive days that trigger the notice requirement


class PTOInput(BaseModel):
    duration_days: int
    advance_notice_business_days: int
    pto_used_ytd: int = 0
    pto_carried_over: int = 0

    @field_validator("duration_days")
    @classmethod
    def positive_duration(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_days must be a positive integer")
        return v

    @field_validator("pto_carried_over")
    @classmethod
    def max_carryover(cls, v: int) -> int:
        if v > PTO_CARRYOVER_MAX:
            raise ValueError(
                f"Carried-over PTO cannot exceed {PTO_CARRYOVER_MAX} days per policy"
            )
        return v


def check_pto_eligibility(
    duration_days: int,
    advance_notice_business_days: int,
    pto_used_ytd: int = 0,
    pto_carried_over: int = 0,
) -> dict:
    """
    Check whether a PTO request satisfies company policy.

    Policy rules:
    - Full-time employees receive 20 PTO days per year.
    - Unused PTO carries over up to 5 days maximum.
    - Vacations longer than 3 consecutive business days require
      at least 10 business days advance notice.
    """
    PTOInput(
        duration_days=duration_days,
        advance_notice_business_days=advance_notice_business_days,
        pto_used_ytd=pto_used_ytd,
        pto_carried_over=pto_carried_over,
    )

    total_available = PTO_DAYS_PER_YEAR + pto_carried_over
    remaining = total_available - pto_used_ytd
    issues = []
    checks = []

    # Check 1: sufficient balance
    if duration_days > remaining:
        issues.append(
            f"Insufficient PTO balance: requesting {duration_days} days but only {remaining} available"
        )
        checks.append({"check": "PTO balance", "passed": False})
    else:
        checks.append({
            "check": "PTO balance",
            "passed": True,
            "detail": f"{remaining} days available, {duration_days} requested",
        })

    # Check 2: advance notice for longer vacations
    if duration_days > ADVANCE_NOTICE_THRESHOLD:
        if advance_notice_business_days < ADVANCE_NOTICE_DAYS:
            issues.append(
                f"Insufficient advance notice: {duration_days}-day vacation requires "
                f"{ADVANCE_NOTICE_DAYS} business days notice, but only "
                f"{advance_notice_business_days} provided"
            )
            checks.append({"check": "Advance notice", "passed": False})
        else:
            checks.append({
                "check": "Advance notice",
                "passed": True,
                "detail": f"{advance_notice_business_days} business days notice provided (minimum {ADVANCE_NOTICE_DAYS})",
            })
    else:
        checks.append({
            "check": "Advance notice",
            "passed": True,
            "detail": f"Vacation is {duration_days} days (≤{ADVANCE_NOTICE_THRESHOLD}), no advance notice requirement applies",
        })

    eligible = len(issues) == 0

    return {
        "eligible": eligible,
        "duration_days": duration_days,
        "advance_notice_business_days": advance_notice_business_days,
        "pto_available": remaining,
        "checks": checks,
        "issues": issues if issues else ["None — request meets all policy requirements"],
        "policy_note": (
            f"Full-time employees receive {PTO_DAYS_PER_YEAR} PTO days/year "
            f"with up to {PTO_CARRYOVER_MAX} days carryover. "
            f"Vacations longer than {ADVANCE_NOTICE_THRESHOLD} consecutive days "
            f"require {ADVANCE_NOTICE_DAYS} business days advance notice."
        ),
    }


# Tool definitions for LLM function-calling
TOOL_DEFINITIONS = [
    {
        "name": "calculate_pricing",
        "description": (
            "Calculate the monthly price, annual subscription cost, implementation fee, "
            "and first-year total for a Northstar Insights plan. "
            "Use this when the user asks about pricing, costs, or upgrade economics. "
            "Discounts cannot be stacked — the highest applicable discount is applied."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "plan": {
                    "type": "string",
                    "description": "Plan name: 'starter', 'growth', or 'enterprise'",
                },
                "contract": {
                    "type": "string",
                    "description": "'monthly' or 'annual'",
                    "default": "monthly",
                },
                "customer_type": {
                    "type": "string",
                    "description": "'standard' or 'nonprofit'",
                    "default": "standard",
                },
            },
            "required": ["plan"],
        },
    },
    {
        "name": "lookup_tickets",
        "description": (
            "Look up support tickets filtered by customer, status, priority, and/or category. "
            "Use this when the user asks about open issues, support history, or ticket status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "string",
                    "description": "Customer name, e.g. 'GreenMart'",
                },
                "status": {
                    "type": "string",
                    "description": "'Open', 'In Progress', or 'Resolved'",
                },
                "priority": {
                    "type": "string",
                    "description": "'Low', 'Medium', 'High', or 'Critical'",
                },
                "category": {
                    "type": "string",
                    "description": "Ticket category, e.g. 'Forecasting', 'Integrations'",
                },
            },
            "required": [],
        },
    },
    {
        "name": "classify_renewal_risk",
        "description": (
            "Classify the renewal risk for a customer as Low, Medium, or High "
            "based on open support tickets and renewal date proximity. "
            "Use this when asked about renewal risk, churn risk, or account health."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "string",
                    "description": "Customer name, e.g. 'GreenMart'",
                },
            },
            "required": ["customer"],
        },
    },
    {
        "name": "find_relevant_projects",
        "description": (
            "Find internal engineering or product projects relevant to a customer or issue category. "
            "Use this when asked which projects affect a customer or when a fix is expected."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "string",
                    "description": "Customer name, e.g. 'StyleHub'",
                },
                "category": {
                    "type": "string",
                    "description": "Issue category, e.g. 'forecasting', 'inventory alerts'",
                },
            },
            "required": [],
        },
    },
    {
        "name": "check_pto_eligibility",
        "description": (
            "Check whether a PTO request satisfies Northstar HR policy. "
            "Use this when asked about PTO requests, leave eligibility, or advance notice requirements."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "duration_days": {
                    "type": "integer",
                    "description": "Number of PTO days being requested",
                },
                "advance_notice_business_days": {
                    "type": "integer",
                    "description": "How many business days in advance the request is being submitted",
                },
                "pto_used_ytd": {
                    "type": "integer",
                    "description": "PTO days already used this year (default 0)",
                    "default": 0,
                },
                "pto_carried_over": {
                    "type": "integer",
                    "description": "PTO days carried over from last year (max 5, default 0)",
                    "default": 0,
                },
            },
            "required": ["duration_days", "advance_notice_business_days"],
        },
    },
]

# Tool dispatcher — called by main.py orchestrator
TOOL_REGISTRY = {
    "calculate_pricing": calculate_pricing,
    "lookup_tickets": lookup_tickets,
    "classify_renewal_risk": classify_renewal_risk,
    "find_relevant_projects": find_relevant_projects,
    "check_pto_eligibility": check_pto_eligibility,
}


def dispatch_tool(name: str, arguments: dict) -> dict:
    """Call a tool by name with the given arguments. Raises KeyError if unknown."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool '{name}'. Available: {list(TOOL_REGISTRY.keys())}")
    return TOOL_REGISTRY[name](**arguments)