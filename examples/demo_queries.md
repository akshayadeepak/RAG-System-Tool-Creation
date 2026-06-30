# Demo Queries

This file shows example queries run against the Northstar Insights RAG assistant,
covering tool calls, RAG retrieval, multi-hop reasoning, and ambiguity handling.

Run with: `python app/main.py "<query>"` for a single query, or `python app/main.py` to run all demo queries.

---

## 1. Tool Use — Pricing Calculator

**Query:** Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer.

**Route:** `tool` → `calculate_pricing`
**Extracted args:** `{"plan": "growth", "contract": "annual", "customer_type": "nonprofit"}`

**Answer:**
> The first-year cost for the Growth Plan on an annual contract for a nonprofit customer is $70,400.
> This total includes the discounted monthly price of $5,200 per month, multiplied by 12 months in a year, plus an implementation fee of $8,000, which brings the total to $62400.00 + $8000 = $70400.00.
>
> Source: calculate_pricing

---

## 2. Tool Use — Support Ticket Lookup

**Query:** Show all open support tickets for GreenMart.

**Route:** `tool` → `lookup_tickets`
**Extracted args:** `{"customer": "GreenMart", "status": "Open"}`

**Answer:**
> There are currently 2 open support tickets for GreenMart.
>
> - Ticket ID: T-1001
>  Date: October 1, 2025
>  Priority: High
>  Category: Forecasting
>  Summary: Weekly forecast failed to refresh for 12 stores in the Northeast region.
> - Ticket ID: T-1004
>  Date: October 6, 2025
>  Priority: Critical
>  Category: Inventory Alerts
>  Summary: False positive stockout alerts triggered for seasonal SKUs.
>
> Source: lookup_tickets

---

## 3. Tool Use — Renewal Risk Classifier

**Query:** What is GreenMart's renewal risk?

**Route:** `tool` → `classify_renewal_risk`
**Extracted args:** `{"customer": "GreenMart"}`

**Answer:**
> GreenMart is at high renewal risk due to an upcoming renewal date of February 28, 2026, with only 122 days remaining until the deadline. This is further complicated by two open tickets (T-1004 and potentially others not listed), which are currently causing issues such as false positive stockout alerts triggered for seasonal SKUs.
>
> Source: classify_renewal_risk

---

## 4. Tool Use — PTO Eligibility Checker

**Query:** Is a 5-day PTO request valid if submitted 7 business days in advance?

**Route:** `tool` → `check_pto_eligibility`
**Extracted args:** `{"duration_days": 5, "advance_notice_business_days": 7}`

**Answer:**
> Based on the check_pto_eligibility tool result, a 5-day PTO request submitted 7 business days in advance is not valid.
>
> The reason for this is that the policy requires 10 business days notice for vacations longer than 3 consecutive days, but only 7 business days were provided. This falls short of the required notice period.
>
> Additionally, the tool result indicates that there are sufficient PTO days available (20) and no issues with the PTO balance. However, the insufficient advance notice is a critical factor in determining eligibility for this request.
>
> Source: check_pto_eligibility

---

## 5. Tool Use — Project Release Finder (Optional Tool)

**Query:** Which internal projects are relevant to StyleHub?

**Route:** `tool` → `find_relevant_projects`
**Extracted args:** `{"customer": "StyleHub", "category": "internal"}`

**Answer:**
> Based on your request, there is one internal project that is directly relevant to StyleHub.
>
> The project is titled "Dashboard Permissions Redesign" and it is owned by the Product Experience Team. The status of the project is currently "Planned", with a target release date of January 20th, 2026. This project aims to provide more granular export permissions for viewer and analyst roles.
>
> Source: find_relevant_projects

---

## 6. Basic Retrieval

**Query:** How many PTO days do full-time employees receive?

**Route:** `rag`

**Answer:**
> Full-time employees receive 20 days of paid time off per calendar year.
>
> Sources: hr_policy.md | Paid Time Off

---

## 7. Basic Retrieval

**Query:** What data sources does Northstar Insights support?

**Route:** `rag`

**Answer:**
> Northstar Insights supports ingestion from the following sources: 
>
> * Shopify
> * Salesforce Commerce Cloud
> * Snowflake
> * BigQuery
> * Amazon S3
> * CSV uploads
>
> Sources: product_docs.md | Data Sources

---

## 8. Multi-Hop Reasoning

**Query:** Why is UrbanBasket a good candidate for upgrading to Growth?

**Route:** `rag`

**Answer:**
> UrbanBasket is a good candidate for upgrading to Growth due to their current pain points, which include:
>
> * Shopify connector reliability issues (Ticket T-1002 from 2025-10-03)
> * Need for customer segmentation (Ticket T-1006 from 2025-10-08), which is not currently being met
> * Manual reporting burden
>
> These issues are impacting UrbanBasket's operations and decision-making processes, making them a good candidate for the additional features and support offered by the Growth plan.
>
> Sources: sales_notes.md | UrbanBasket, support_tickets.csv | T-1002, T-1006

---

## 9. Ambiguity / Robustness

**Query:** Does the platform support Azure Synapse?

**Route:** `rag`

**Answer:**
> No, Northstar Insights does not currently support Azure Synapse as a data source. The supported data sources listed in the product documentation include Shopify, Salesforce Commerce Cloud, Snowflake, BigQuery, Amazon S3, and CSV uploads.
>
> Sources: product_docs.md | Data Sources

---

## 10. Multi-Hop Reasoning

**Query:** What issues should the customer success team discuss with GreenMart before renewal?

**Route:** `rag`

**Answer:**
> Based on the provided context, the customer success team should discuss the following issues with GreenMart before renewal:
>
> 1. **Forecasting reliability**: The weekly forecast refresh job failed to refresh for 12 stores in the Northeast region, and there are concerns about false positive inventory alerts.
> 2. **Inventory Alert Calibration**: There were false positive stockout alerts triggered for seasonal SKUs, which is being addressed by recalibrating stockout risk thresholds.
> 3. **Pharmacy-specific dashboards**: GreenMart needs pharmacy-specific dashboards to better manage their operations.
>
> These issues should be discussed with the customer success team to ensure a smooth transition and successful renewal of Northstar Insights' services.
>
> Sources: sales_notes.md | GreenMart, support_tickets.csv | T-1001, T-1004, project_updates.md | Forecast Refresh Reliability, Inventory Alert Calibration

---

## Summary

| # | Query Type | Route | Tool Used | Result |
|---|---|---|---|---|
| 1 | Tool — Pricing | tool | calculate_pricing | ✅ Correct |
| 2 | Tool — Tickets | tool | lookup_tickets | ✅ Correct |
| 3 | Tool — Risk | tool | classify_renewal_risk | ⚠️ Partially correct - (reasoning is not complete)|
| 4 | Tool — PTO | tool | check_pto_eligibility | ✅ Correct |
| 5 | Tool — Projects | tool | find_relevant_projects | ✅ Correct |
| 6 | Basic Retrieval | rag | — | ✅ Correct |
| 7 | Basic Retrieval | rag | — | ✅ Correct |
| 8 | Multi-Hop | rag | — | ✅ Correct |
| 9 | Ambiguity | rag | — | ✅ Correct|
| 10 | Multi-Hop | rag | — | ✅ Correct |