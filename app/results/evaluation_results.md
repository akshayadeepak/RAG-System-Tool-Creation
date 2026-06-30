# Evaluation Results

## Summary Table

| # | Category | Query | Route | Tool | Correctness |
|---|---|---|---|---|---|
| 1 | Basic Retrieval | How many PTO days do full-time employees receive? | rag_fallback | check_pto_eligibility | _TBD_ |
| 2 | Basic Retrieval | What data sources does Northstar Insights support? | rag | — | _TBD_ |
| 3 | Basic Retrieval | How often do customer segments refresh? | rag | — | _TBD_ |
| 4 | Basic Retrieval | What encryption is used at rest? | rag | — | _TBD_ |
| 5 | Tool Use | Calculate the first-year cost for the Growth Plan on an a... | tool | calculate_pricing | _TBD_ |
| 6 | Tool Use | Show all open support tickets for GreenMart. | tool | lookup_tickets | _TBD_ |
| 7 | Tool Use | What is GreenMart's renewal risk? | tool | classify_renewal_risk | _TBD_ |
| 8 | Tool Use | Is a 5-day PTO request valid if submitted 7 business days... | tool | check_pto_eligibility | _TBD_ |
| 9 | Multi-Hop RAG | Why is UrbanBasket a good candidate for upgrading to Growth? | rag | — | _TBD_ |
| 10 | Multi-Hop RAG | Which internal projects are relevant to StyleHub? | tool | find_relevant_projects | _TBD_ |
| 11 | Multi-Hop RAG | What issues should the customer success team discuss with... | rag | — | _TBD_ |
| 12 | Multi-Hop RAG | Which customers are affected by integration issues? | rag | — | _TBD_ |
| 13 | Ambiguity / Robustness | Does the platform support Azure Synapse? | rag | — | _TBD_ |
| 14 | Ambiguity / Robustness | Can a customer with 4 months of sales history use forecas... | rag | — | _TBD_ |
| 15 | Ambiguity / Robustness | Can nonprofit annual discounts be combined? | rag | — | _TBD_ |
| 16 | Ambiguity / Robustness | Who owns the fix for false positive inventory alerts? | rag | — | _TBD_ |
| 17 | Structured Output | Return open tickets grouped by customer in JSON. | tool | lookup_tickets | _TBD_ |
| 18 | Structured Output | Create a customer risk table with customer, plan, renewal... | tool | lookup_tickets | _TBD_ |
| 19 | Structured Output | List all target releases by date. | rag | — | _TBD_ |
| 20 | Structured Output | Give me a sales prep brief for UrbanBasket with citations. | rag | — | _TBD_ |

---

## Full Results

### 1. [Basic Retrieval] How many PTO days do full-time employees receive?

**Route:** `rag_fallback`
**Tool:** `check_pto_eligibility`
**Args:** `{"pto_used_ytd": 0, "pto_carried_over": 0}`

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

**Correctness:** _TBD — fill in after manual review_

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
> Sources: product_docs.md | Data Sources

**Retrieved sources:**
- product_docs.md | Product Overview
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Security
- product_docs.md | Data Sources
- hr_policy.md | Northstar Analytics HR Policy Handbook
- sales_notes.md | GreenMart
- pricing_rules.md | Northstar Pricing and Packaging Rules
- pricing_rules.md | Plans

**Correctness:** _TBD — fill in after manual review_

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

**Correctness:** _TBD — fill in after manual review_

---

### 4. [Basic Retrieval] What encryption is used at rest?

**Route:** `rag`

**Answer:**

> At rest, Northstar Insights uses AES-256 encryption.
> 
> Sources:
> product_docs.md | Security
> product_docs.md | Data Sources

**Retrieved sources:**
- product_docs.md | Security
- support_tickets.csv | T-1005
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Data Sources
- product_docs.md | Product Overview
- pricing_rules.md | Plans
- hr_policy.md | Northstar Analytics HR Policy Handbook
- product_docs.md | Forecasting Module

**Correctness:** _TBD — fill in after manual review_

---

### 5. [Tool Use] Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer.

**Route:** `tool`
**Tool:** `calculate_pricing`
**Args:** `{"plan": "growth", "contract": "annual", "customer_type": "nonprofit"}`

**Answer:**

> The first-year cost for the Growth Plan on an annual contract for a nonprofit customer is $70,400.
> 
> This total includes the discounted monthly price of $5,200 per month, multiplied by 12 months in a year, plus an implementation fee of $8,000 and no additional discounts. 
> 
> Source: calculate_pricing

**Correctness:** _TBD — fill in after manual review_

---

### 6. [Tool Use] Show all open support tickets for GreenMart.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": "GreenMart", "status": "Open"}`

**Answer:**

> Here are the open support tickets for GreenMart:
> 
> There are currently two open support tickets for GreenMart.
> 
> 1. Ticket ID: T-1001
>    Date: October 1, 2025
>    Priority: High
>    Category: Forecasting
>    Summary: Weekly forecast failed to refresh for 12 stores in the Northeast region.
>    Status: Open
> 
> 2. Ticket ID: T-1004
>    Date: October 6, 2025
>    Priority: Critical
>    Category: Inventory Alerts
>    Summary: False positive stockout alerts triggered for seasonal SKUs.
>    Status: Open
> 
> Source: lookup_tickets

**Correctness:** _TBD — fill in after manual review_

---

### 7. [Tool Use] What is GreenMart's renewal risk?

**Route:** `tool`
**Tool:** `classify_renewal_risk`
**Args:** `{"customer": "GreenMart"}`

**Answer:**

> GreenMart is at high renewal risk due to an open ticket count of 2 and a critical issue with false positive stockout alerts triggered for seasonal SKUs (Ticket ID: T-1004). The customer's renewal date is set for February 28, 2026, which is just over 122 days away. This indicates that GreenMart needs to address the underlying cause of these issues before its next scheduled renewal period.
> 
> Source: classify_renewal_risk

**Correctness:** _TBD — fill in after manual review_

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
> Additionally, the tool result indicates that there are sufficient PTO days available (20) and no issues with the PTO balance. However, the insufficient advance notice is a critical factor in determining eligibility for this request.
> 
> Source: check_pto_eligibility

**Correctness:** _TBD — fill in after manual review_

---

### 9. [Multi-Hop RAG] Why is UrbanBasket a good candidate for upgrading to Growth?

**Route:** `rag`

**Answer:**

> UrbanBasket is a good candidate for upgrading to Growth due to their current pain points, which include:
> 
> * Shopify connector reliability issues, as evident from Ticket T-1002 (status: In Progress) and the ongoing stabilization efforts of the Shopify Connector.
> * The need for customer segmentation, highlighted in Ticket T-1006 (status: Open), which is a key feature of the Growth Plan.
> 
> These pain points suggest that UrbanBasket requires more advanced features and support to manage their data effectively, making them a good candidate for upgrading to the Growth Plan.
> 
> Sources:
> sales_notes.md | UrbanBasket
> support_tickets.csv | T-1002
> T-1006

**Retrieved sources:**
- sales_notes.md | UrbanBasket
- project_updates.md | Shopify Connector Stabilization
- sales_notes.md | GreenMart
- support_tickets.csv | T-1006
- support_tickets.csv | T-1002
- product_docs.md | Data Sources
- sales_notes.md | StyleHub
- support_tickets.csv | T-1008

**Correctness:** _TBD — fill in after manual review_

---

### 10. [Multi-Hop RAG] Which internal projects are relevant to StyleHub?

**Route:** `tool`
**Tool:** `find_relevant_projects`
**Args:** `{"customer": "StyleHub", "category": "internal"}`

**Answer:**

> Based on your search for internal projects relevant to StyleHub, we found one project that matches your criteria.
> 
> The project is titled "Dashboard Permissions Redesign" and is owned by the Product Experience Team. The current status of the project is Planned, with a target release date of January 20th, 2026.
> 
> This project is directly relevant to StyleHub, as indicated by its relevance score. The description of the project includes more granular export permissions for viewer and analyst roles, which may be of interest to StyleHub stakeholders.
> 
> Source: find_relevant_projects

**Correctness:** _TBD — fill in after manual review_

---

### 11. [Multi-Hop RAG] What issues should the customer success team discuss with GreenMart before renewal?

**Route:** `rag`

**Answer:**

> Based on the context excerpts, the customer success team should discuss the following issues with GreenMart before renewal:
> 
> 1. **Forecasting reliability**: The weekly forecast refresh job failed to refresh for 12 stores in the Northeast region, and there are concerns about false positive inventory alerts.
> 2. **False positive inventory alerts**: There were critical false positive stockout alerts triggered for seasonal SKUs, which may be causing operational issues.
> 3. **Need pharmacy-specific dashboards**: GreenMart is evaluating whether to expand Northstar Insights to their pharmacy division, indicating a need for tailored solutions.
> 
> Sources:
> - sales_notes.md | GreenMart
> - project_updates.md | Forecast Refresh Reliability
> - support_tickets.csv | T-1001 and T-1004

**Retrieved sources:**
- sales_notes.md | GreenMart
- project_updates.md | Forecast Refresh Reliability
- support_tickets.csv | T-1001
- support_tickets.csv | T-1004
- sales_notes.md | UrbanBasket
- project_updates.md | Shopify Connector Stabilization
- project_updates.md | Inventory Alert Calibration
- support_tickets.csv | T-1006

**Correctness:** _TBD — fill in after manual review_

---

### 12. [Multi-Hop RAG] Which customers are affected by integration issues?

**Route:** `rag`

**Answer:**

> According to the context excerpts, two customers are mentioned as being affected by integration issues:
> 
> 1. UrbanBasket (T-1002) - experiencing intermittent timeouts during nightly syncs with their Shopify connector.
> 2. StyleHub (T-1008) - facing BigQuery ingestion lag exceeding 9 hours.
> 
> Sources: support_tickets.csv | T-1002, project_updates.md, and support_tickets.csv | T-1008

**Retrieved sources:**
- support_tickets.csv | T-1002
- project_updates.md | Shopify Connector Stabilization
- support_tickets.csv | T-1006
- product_docs.md | Customer Segmentation
- sales_notes.md | GreenMart
- sales_notes.md | UrbanBasket
- support_tickets.csv | T-1008
- sales_notes.md | StyleHub

**Correctness:** _TBD — fill in after manual review_

---

### 13. [Ambiguity / Robustness] Does the platform support Azure Synapse?

**Route:** `rag`

**Answer:**

> No, the platform does not directly support Azure Synapse as a data source. However, it supports BigQuery, which can be used to connect to Azure Synapse.
> 
> Sources:
> product_docs.md | Data Sources
> Data Sources
> - Shopify
> - Salesforce Commerce Cloud
> - Snowflake
> - BigQuery
> - Amazon S3
> - CSV uploads

**Retrieved sources:**
- product_docs.md | Northstar Insights Product Documentation
- product_docs.md | Data Sources
- product_docs.md | Security
- project_updates.md | Shopify Connector Stabilization
- product_docs.md | Product Overview
- support_tickets.csv | T-1002
- pricing_rules.md | Plans
- project_updates.md | Forecast Refresh Reliability

**Correctness:** _TBD — fill in after manual review_

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

**Correctness:** _TBD — fill in after manual review_

---

### 15. [Ambiguity / Robustness] Can nonprofit annual discounts be combined?

**Route:** `rag`

**Answer:**

> No, nonprofit annual discounts cannot be combined. According to the pricing rules, "Discounts cannot be stacked. If multiple discounts apply, use the highest single discount."
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

**Correctness:** _TBD — fill in after manual review_

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

**Correctness:** _TBD — fill in after manual review_

---

### 17. [Structured Output] Return open tickets grouped by customer in JSON.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": null, "status": "Open", "priority": null, "category": null}`

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

**Correctness:** _TBD — fill in after manual review_

---

### 18. [Structured Output] Create a customer risk table with customer, plan, renewal date, open tickets, and risk level.

**Route:** `tool`
**Tool:** `lookup_tickets`
**Args:** `{"customer": "string", "status": "string", "priority": "string", "category": "string"}`

**Answer:**

> Unfortunately, we do not have any customer risk data available in our system at this time.
> 
> The lookup_tickets tool was used with no filters applied, but it did not return any results. This means that there are currently no open tickets for customers that meet the specified criteria.
> 
> Source: lookup_tickets

**Correctness:** _TBD — fill in after manual review_

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
> Sources:
> project_updates.md | Target release: Forecast Refresh Reliability
> project_updates.md | Target release: Shopify Connector Stabilization
> project_updates.md | Target release: Inventory Alert Calibration

**Retrieved sources:**
- project_updates.md | Forecast Refresh Reliability
- project_updates.md | Shopify Connector Stabilization
- pricing_rules.md | Northstar Pricing and Packaging Rules
- sales_notes.md | Sales Enablement Notes
- project_updates.md | Inventory Alert Calibration
- project_updates.md | Internal Project Updates
- product_docs.md | Forecasting Module
- pricing_rules.md | Plans

**Correctness:** _TBD — fill in after manual review_

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
> 1. **Shopify Connector Reliability**: The current Shopify connector is unreliable, causing issues during high-volume nightly syncs (Source: project_updates.md | Shopify Connector Stabilization).
> 2. **Customer Segmentation**: UrbanBasket requires customer segmentation to refresh loyalty segments, but this feature is not currently working as expected (Source: support_tickets.csv | T-1006).
> 3. **Manual Reporting Burden**: The current setup creates a manual reporting burden for stakeholders, which may hinder data-driven decision-making.
> 
> **Opportunities:**
> 
> 1. **Upgrade to Growth Plan**: UrbanBasket is considering upgrading to the Growth Plan to address their growing needs (Source: sales_notes.md | UrbanBasket).
> 2. **Integrate Additional Data Sources**: Northstar Insights supports ingestion from various sources, including Shopify, Salesforce Commerce Cloud, and Snowflake, which could provide additional insights for UrbanBasket's operations.
> 
> **Recommendations:**
> 
> 1. Prioritize the stabilization of the Shopify connector to ensure reliable data syncs.
> 2. Address the customer segmentation issue to enable loyalty program management.
> 3. Explore Northstar Insights' pricing options to optimize reporting and analytics capabilities.
> 
> Sources:
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

**Correctness:** _TBD — fill in after manual review_

---
