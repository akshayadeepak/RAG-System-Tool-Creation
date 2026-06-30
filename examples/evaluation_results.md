# Evaluation Results

## Summary Table

| # | Category | Query | Route | Tool | Correctness |
|---|---|---|---|---|---|
| 1 | Basic Retrieval | How many PTO days do full-time employees receive? | rag | — | ✅ Correct |
| 2 | Basic Retrieval | What data sources does Northstar Insights support? | rag | — | ✅ Correct |
| 3 | Basic Retrieval | How often do customer segments refresh? | rag | — | ✅ Correct |
| 4 | Basic Retrieval | What encryption is used at rest? | rag | — | ✅ Correct |
| 5 | Tool Use | Calculate the first-year cost for the Growth Plan on an a... | tool | calculate_pricing | ✅ Correct |
| 6 | Tool Use | Show all open support tickets for GreenMart. | tool | lookup_tickets | ✅ Correct |
| 7 | Tool Use | What is GreenMart's renewal risk? | tool | classify_renewal_risk | ⚠️ Partially correct - (reasoning focused on date instead of critical ticket) |
| 8 | Tool Use | Is a 5-day PTO request valid if submitted 7 business days... | tool | check_pto_eligibility | ✅ Correct |
| 9 | Multi-Hop RAG | Why is UrbanBasket a good candidate for upgrading to Growth? | rag | — | ✅ Correct |
| 10 | Multi-Hop RAG | Which internal projects are relevant to StyleHub? | tool | find_relevant_projects | ✅ Correct |
| 11 | Multi-Hop RAG | What issues should the customer success team discuss with... | rag | — | ✅ Correct |
| 12 | Multi-Hop RAG | Which customers are affected by integration issues? | rag | — | ✅ Correct |
| 13 | Ambiguity / Robustness | Does the platform support Azure Synapse? | rag | — | ⚠️ Partially correct - (does not list the supported platforms) |
| 14 | Ambiguity / Robustness | Can a customer with 4 months of sales history use forecas... | rag | — | ✅ Correct |
| 15 | Ambiguity / Robustness | Can nonprofit annual discounts be combined? | rag | — | ✅ Correct |
| 16 | Ambiguity / Robustness | Who owns the fix for false positive inventory alerts? | rag | — | ✅ Correct |
| 17 | Structured Output | Return open tickets grouped by customer in JSON. | tool | lookup_tickets | ⚠️ Partially correct - (does not list all open tickets) |
| 18 | Structured Output | Create a customer risk table with customer, plan, renewal... | tool | lookup_tickets | ❌ Incorrect - (incorrectly redirected to a tool instead of generating a response) |
| 19 | Structured Output | List all target releases by date. | rag | — | ⚠️ Partially correct - (does not list all target releases) |
| 20 | Structured Output | Give me a sales prep brief for UrbanBasket with citations. | rag | — | ✅ Correct |


---

## Full Results

### 1. [Basic Retrieval] How many PTO days do full-time employees receive?

**Route:** `rag`

**Answer:**

> Full-time employees receive 20 days of paid time off per calendar year.
> 
> Sources: hr_policy.md | Paid Time Off

**Retrieved sources:**
- hr_policy.md | Paid Time Off
- hr_policy.md | Sick Leave
- hr_policy.md | Remote Work
- hr_policy.md | Parental Leave
- pricing_rules.md | Implementation Fees
- hr_policy.md | Learning Budget
- hr_policy.md | Northstar Analytics HR Policy Handbook
- pricing_rules.md | Plans

**Correctness:** ✅ Correct

---

### 2. [Basic Retrieval] What data sources does Northstar Insights support?

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
> Sources:
> product_docs.md | Data Sources (Section: "Data Sources")

**Retrieved sources:**
- product_docs.md | Product Overview
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Security
- product_docs.md | Data Sources
- hr_policy.md | Northstar Analytics HR Policy Handbook
- sales_notes.md | GreenMart
- pricing_rules.md | Northstar Pricing and Packaging Rules
- pricing_rules.md | Plans

**Correctness:** ✅ Correct

---

### 3. [Basic Retrieval] How often do customer segments refresh?

**Route:** `rag`

**Answer:**

> Customer segments refresh every 24 hours.
> 
> Sources: product_docs.md | Customer Segmentation

**Retrieved sources:**
- product_docs.md | Customer Segmentation
- support_tickets.csv | T-1006
- product_docs.md | Forecasting Module
- project_updates.md | Forecast Refresh Reliability
- sales_notes.md | GreenMart
- support_tickets.csv | T-1002
- project_updates.md | Shopify Connector Stabilization
- support_tickets.csv | T-1001

**Correctness:** ✅ Correct

---

### 4. [Basic Retrieval] What encryption is used at rest?

**Route:** `rag`

**Answer:**

> Data is encrypted in transit using TLS 1.3 and at rest using AES-256.
> 
> Sources: product_docs.md | Security

**Retrieved sources:**
- product_docs.md | Security
- support_tickets.csv | T-1005
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Data Sources
- product_docs.md | Product Overview
- pricing_rules.md | Plans
- hr_policy.md | Northstar Analytics HR Policy Handbook
- product_docs.md | Forecasting Module

**Correctness:** ✅ Correct

---

### 5. [Tool Use] Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer.

**Route:** `tool`
**Tool:** `calculate_pricing`
**Args:** `{"plan": "growth", "contract": "annual", "customer_type": "nonprofit"}`

**Answer:**

> The first-year cost for the Growth Plan on an annual contract for a nonprofit customer is $70,400.
> 
> This total includes the discounted monthly price of $5,200 per month, multiplied by 12 months in a year, which equals $62,400. Additionally, there is an implementation fee of $8,000 and no other costs mentioned in the result.
> 
> Source: calculate_pricing

**Correctness:** ✅ Correct

---

### 6. [Tool Use] Show all open support tickets for GreenMart.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": "GreenMart", "status": "Open"}`

**Answer:**

> There are currently two open support tickets for GreenMart.
> 
> The first ticket, T-1001, was created on October 1st, 2025, and is related to an issue with the weekly forecast failing to refresh for 12 stores in the Northeast region. The priority of this ticket is High, and it falls under the category of Forecasting.
> 
> The second ticket, T-1004, was created on October 6th, 2025, and is related to a False positive stockout alerts issue triggered for seasonal SKUs. This ticket has a higher priority level of Critical and also falls under the Inventory Alerts category.
> 
> Source: lookup_tickets

**Correctness:** ✅ Correct

---

### 7. [Tool Use] What is GreenMart's renewal risk?

**Route:** `tool`
**Tool:** `classify_renewal_risk`
**Args:** `{"customer": "GreenMart"}`

**Answer:**

> GreenMart is at high renewal risk due to an upcoming renewal date of February 28, 2026. With only 122 days remaining until the renewal period, there is limited time for adjustments or changes that could mitigate potential issues.
> 
> Currently, GreenMart has two open tickets (T-1004) that are causing concern, specifically false positive stockout alerts triggered for seasonal SKUs. This indicates a critical issue that needs to be addressed before the renewal date.
> 
> Source: classify_renewal_risk

**Correctness:** ⚠️ Partially correct

---

### 8. [Tool Use] Is a 5-day PTO request valid if submitted 7 business days in advance?

**Route:** `tool`
**Tool:** `check_pto_eligibility`
**Args:** `{"duration_days": 5, "advance_notice_business_days": 7}`

**Answer:**

> Based on the check_pto_eligibility tool result, a 5-day PTO request submitted 7 business days in advance is not valid.
> 
> The reason for this is that the policy requires 10 business days notice for vacations longer than 3 consecutive days, but only 7 business days were provided. This falls short of the required notice period.
> 
> Additionally, the tool result indicates that there are sufficient PTO balance available (20 days) and that the advance notice passed the check, but this is not enough to override the policy requirement.
> 
> Source: check_pto_eligibility

**Correctness:** ✅ Correct

---

### 9. [Multi-Hop RAG] Why is UrbanBasket a good candidate for upgrading to Growth?

**Route:** `rag`

**Answer:**

> UrbanBasket is a good candidate for upgrading to Growth due to their current pain points, which include:
> 
> * Shopify connector reliability issues, as evident from Ticket T-1002 (status: In Progress) and the ongoing stabilization efforts of the Shopify Connector (target release: 2025-11-15).
> * The need for customer segmentation, highlighted in Ticket T-1006 (status: Open), which is a key feature of the Growth Plan.
> * Manual reporting burden, mentioned in sales_notes.md as one of their current pain points.
> 
> These issues suggest that UrbanBasket requires more advanced features and support to manage their growth, making them a good candidate for upgrading to the Growth Plan.
> 
> Sources:
> sales_notes.md | UrbanBasket
> support_tickets.csv | T-1002
> project_updates.md | Shopify Connector Stabilization

**Retrieved sources:**
- sales_notes.md | UrbanBasket
- project_updates.md | Shopify Connector Stabilization
- sales_notes.md | GreenMart
- support_tickets.csv | T-1006
- support_tickets.csv | T-1002
- product_docs.md | Data Sources
- sales_notes.md | StyleHub
- support_tickets.csv | T-1008

**Correctness:** ✅ Correct

---

### 10. [Multi-Hop RAG] Which internal projects are relevant to StyleHub?

**Route:** `tool`
**Tool:** `find_relevant_projects`
**Args:** `{"customer": "StyleHub", "category": "internal"}`

**Answer:**

> Based on your request, we found one internal project that is directly relevant to StyleHub.
> 
> The project is titled "Dashboard Permissions Redesign" and is owned by the Product Experience Team. It has a planned status with a target release date of January 20th, 2026. The project aims to provide more granular export permissions for viewer and analyst roles.
> 
> This project is considered directly relevant to StyleHub due to its focus on enhancing user permissions.
> 
> Source: find_relevant_projects

**Correctness:** ✅ Correct

---

### 11. [Multi-Hop RAG] What issues should the customer success team discuss with GreenMart before renewal?

**Route:** `rag`

**Answer:**

> Based on the context excerpts, the customer success team should discuss the following issues with GreenMart before renewal:
> 
> 1. **Forecasting reliability**: The weekly forecast refresh job failed to refresh for 12 stores in the Northeast region, and there are concerns about false positive inventory alerts.
> 2. **False positive inventory alerts**: There were critical false positive stockout alerts triggered for seasonal SKUs, which may be causing operational issues.
> 3. **Pharmacy-specific dashboards**: GreenMart needs pharmacy-specific dashboards to better manage their operations.
> 
> These issues should be discussed with the key stakeholders: Maya Chen (VP Analytics), Robert Ellis (CIO), and Tanya Brooks (Director of Merchandising).
> 
> Sources:
> - sales_notes.md | GreenMart
> - project_updates.md | Forecast Refresh Reliability
> - support_tickets.csv | T-1001, T-1004

**Retrieved sources:**
- sales_notes.md | GreenMart
- project_updates.md | Forecast Refresh Reliability
- support_tickets.csv | T-1001
- support_tickets.csv | T-1004
- sales_notes.md | UrbanBasket
- project_updates.md | Shopify Connector Stabilization
- project_updates.md | Inventory Alert Calibration
- support_tickets.csv | T-1006

**Correctness:** ✅ Correct

---

### 12. [Multi-Hop RAG] Which customers are affected by integration issues?

**Route:** `rag`

**Answer:**

> According to the context excerpts, two customers are mentioned as being affected by integration issues:
> 
> 1. UrbanBasket (T-1002) - experiencing intermittent timeouts during nightly syncs with their Shopify connector.
> 2. StyleHub (T-1008) - facing BigQuery ingestion lag exceeding 9 hours.
> 
> Sources: support_tickets.csv | T-1002, sales_notes.md | StyleHub

**Retrieved sources:**
- support_tickets.csv | T-1002
- project_updates.md | Shopify Connector Stabilization
- support_tickets.csv | T-1006
- product_docs.md | Customer Segmentation
- sales_notes.md | GreenMart
- sales_notes.md | UrbanBasket
- support_tickets.csv | T-1008
- sales_notes.md | StyleHub

**Correctness:** ✅ Correct

---

### 13. [Ambiguity / Robustness] Does the platform support Azure Synapse?

**Route:** `rag`

**Answer:**

> No, Northstar Insights does not currently support Azure Synapse as a data source.
> 
> Sources:
> product_docs.md | Data Sources
> product_docs.md | Product Overview

**Retrieved sources:**
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Data Sources
- product_docs.md | Security
- project_updates.md | Shopify Connector Stabilization
- product_docs.md | Product Overview
- support_tickets.csv | T-1002
- pricing_rules.md | Plans
- project_updates.md | Forecast Refresh Reliability

**Correctness:** ⚠️ Partially correct

---

### 14. [Ambiguity / Robustness] Can a customer with 4 months of sales history use forecasting?

**Route:** `rag`

**Answer:**

> No, a customer with less than 6 months of historical data cannot use the forecasting module. According to the context excerpt from product_docs.md | Forecasting Module, "Customers with less than 6 months of historical data cannot use the forecasting module."
> 
> Sources: product_docs.md | Forecasting Module

**Retrieved sources:**
- product_docs.md | Forecasting Module
- support_tickets.csv | T-1001
- pricing_rules.md | Plans
- project_updates.md | Forecast Refresh Reliability
- sales_notes.md | GreenMart
- sales_notes.md | Sales Enablement Notes
- project_updates.md | Inventory Alert Calibration
- product_docs.md | Inventory Alerts

**Correctness:** ✅ Correct

---

### 15. [Ambiguity / Robustness] Can nonprofit annual discounts be combined?

**Route:** `rag`

**Answer:**

> No, nonprofit annual discounts cannot be combined. According to the pricing rules, "Discounts cannot be stacked. If multiple discounts apply, use the highest single discount." This policy applies to all types of discounts, including nonprofit annual discounts.
> 
> Sources: pricing_rules.md | Discounts

**Retrieved sources:**
- pricing_rules.md | Discounts
- hr_policy.md | Paid Time Off
- hr_policy.md | Learning Budget
- pricing_rules.md | Implementation Fees
- pricing_rules.md | Northstar Pricing and Packaging Rules
- hr_policy.md | Sick Leave
- sales_notes.md | Sales Enablement Notes
- sales_notes.md | GreenMart

**Correctness:** ✅ Correct

---

### 16. [Ambiguity / Robustness] Who owns the fix for false positive inventory alerts?

**Route:** `rag`

**Answer:**

> The Applied AI team is responsible for recalibrating stockout risk thresholds to reduce false positive alerts for seasonal SKUs, which includes addressing the issue of false positive inventory alerts.
> 
> Sources:
> - project_updates.md | Inventory Alert Calibration
> - product_docs.md | Inventory Alerts

**Retrieved sources:**
- project_updates.md | Inventory Alert Calibration
- product_docs.md | Inventory Alerts
- support_tickets.csv | T-1004
- sales_notes.md | GreenMart
- project_updates.md | Forecast Refresh Reliability
- project_updates.md | Shopify Connector Stabilization
- support_tickets.csv | T-1005
- support_tickets.csv | T-1002

**Correctness:** ✅ Correct

---

### 17. [Structured Output] Return open tickets grouped by customer in JSON.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": "", "status": "Open", "priority": null, "category": null}`

**Answer:**

> Here is the summary of open tickets grouped by customer in JSON format:
> 
> {
>   "GreenMart": [
>     {
>       "ticket_id": "T-1001",
>       "date": "2025-10-01",
>       "priority": "High",
>       "category": "Forecasting",
>       "summary": "Weekly forecast failed to refresh for 12 stores in the Northeast region.",
>       "status": "Open"
>     },
>     {
>       "ticket_id": "T-1004",
>       "date": "2025-10-06",
>       "priority": "Critical",
>       "category": "Inventory Alerts",
>       "summary": "False positive stockout alerts triggered for seasonal SKUs.",
>       "status": "Open"
>     }
>   ],
>   "UrbanBasket": [
>     {
>       "ticket_id": "T-1006",
>       "date": "2025-10-08",
>       "priority": "Medium",
>       "category": "Customer Segmentation",
>       "summary": "Segments not refreshing for loyalty customers.",
>       "status": "Open"
>     }
>   ],
>   "StyleHub": [
>     {
>       "ticket_id": "T-1008",
>       "date": "2025-10-10",
>       "priority": "High",
>       "category": "Integrations",
>       "summary": "BigQuery ingestion lag exceeding 9 hours.",
>       "status": "Open"
>     }
>   ]
> }
> 
> Source: lookup_tickets

**Correctness:** ⚠️ Partially correct

---

### 18. [Structured Output] Create a customer risk table with customer, plan, renewal date, open tickets, and risk level.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": "string", "status": "string", "priority": "string", "category": "string"}`

**Answer:**

> Unfortunately, the lookup_tickets tool did not return any results for the specified filters.
> 
> Source: lookup_tickets

**Correctness:** ❌ Incorrect

---

### 19. [Structured Output] List all target releases by date.

**Route:** `rag`

**Answer:**

> Here are the target release dates:
> 
> * 2025-11-15 (Shopify Connector Stabilization)
> * 2025-12-01 (Forecast Refresh Reliability)
> * 2025-12-10 (Inventory Alert Calibration)
> 
> Sources: project_updates.md | Forecast Refresh Reliability, project_updates.md | Shopify Connector Stabilization, project_updates.md | Inventory Alert Calibration

**Retrieved sources:**
- project_updates.md | Forecast Refresh Reliability
- project_updates.md | Shopify Connector Stabilization
- pricing_rules.md | Northstar Pricing and Packaging Rules
- sales_notes.md | Sales Enablement Notes
- project_updates.md | Inventory Alert Calibration
- project_updates.md | Internal Project Updates
- product_docs.md | Forecasting Module
- pricing_rules.md | Plans

**Correctness:** ⚠️ Partially correct

---

### 20. [Structured Output] Give me a sales prep brief for UrbanBasket with citations.

**Route:** `rag`

**Answer:**

> **Sales Prep Brief for UrbanBasket**
> 
> UrbanBasket is a fast-growing online grocery platform experiencing pain points in Shopify connector reliability, customer segmentation, and manual reporting burden.
> 
> **Key Challenges:**
> 
> 1. **Shopify Connector Reliability**: UrbanBasket is currently on the Starter Plan but is considering upgrading to Growth due to issues with the Shopify connector's reliability during high-volume nightly syncs (Source: project_updates.md | Shopify Connector Stabilization).
> 2. **Customer Segmentation**: UrbanBasket requires customer segmentation, but segments are not refreshing for loyalty customers, as reported in T-1006 support ticket (Source: support_tickets.csv | T-1006).
> 3. **Manual Reporting Burden**: The current setup creates a manual reporting burden, which may be alleviated with Northstar Insights' automated reporting capabilities.
> 
> **Recommendation:**
> 
> UrbanBasket should consider upgrading to the Growth Plan and leveraging Northstar Insights' features to address these pain points. Specifically:
> 
> * Utilize Shopify connector stabilization efforts to improve reliability.
> * Implement customer segmentation to better understand loyalty customers.
> * Leverage Northstar Insights' automated reporting capabilities to reduce manual reporting burden.
> 
> **Sources:**
> 
> - sales_notes.md | UrbanBasket
> - project_updates.md | Shopify Connector Stabilization
> - support_tickets.csv | T-1006
> - product_docs.md | Data Sources

**Retrieved sources:**
- sales_notes.md | UrbanBasket
- project_updates.md | Shopify Connector Stabilization
- support_tickets.csv | T-1006
- product_docs.md | Data Sources
- sales_notes.md | Sales Enablement Notes
- sales_notes.md | GreenMart
- pricing_rules.md | Northstar Pricing and Packaging Rules
- sales_notes.md | StyleHub

**Correctness:** ✅ Correct

---
