# Northstar Insights Product Documentation
 
Version: 3.4
Last updated: 2025-10-02
 
## Product Overview
Northstar Insights is a SaaS analytics platform for mid-market retail companies. It provides sales forecasting, customer segmentation, inventory alerts, and executive dashboards.
 
## Data Sources
Northstar Insights supports ingestion from the following sources:
- Shopify
- Salesforce Commerce Cloud
- Snowflake
- BigQuery
- Amazon S3
- CSV uploads
 
## Forecasting Module
The forecasting module generates weekly sales forecasts at the SKU, store, region, and category levels.
 
Forecasts are refreshed every Monday at 06:00 UTC.
 
The model requires at least 18 months of historical sales data for optimal accuracy. Customers with less than 6 months of historical data cannot use the forecasting module.
 
## Customer Segmentation
The segmentation module groups customers based on purchase frequency, average order value, category preference, and recency of purchase.
 
Segments refresh every 24 hours.
 
## Inventory Alerts
Inventory alerts are generated when projected stockout risk exceeds 70% within the next 14 days.
 
Alerts can be sent by email, Slack, or webhook.
 
## Security
Northstar Insights is SOC 2 Type II certified. Data is encrypted in transit using TLS 1.3 and at rest using AES-256.
