# Customer Onboarding Guide

Complete guide for onboarding new customers to the Fabric Capacity Monitor.

## Prerequisites

Before onboarding a customer:
- Infrastructure deployed to Azure (see [deployment.md](deployment.md))
- Backend application running successfully
- Container App URL available (e.g., `https://ca-fabricmon-prod.azurecontainerapps.io`)
- Admin API key retrieved from Key Vault

Allow 30-45 minutes for the full onboarding process (most of it is waiting for the background collector).

## Overview

Customer onboarding uses a three-tier data collection model:

**Tier 1 - Azure ARM API (Required)**
- Automatic pull of capacity metadata (state, SKU, region)
- Requires Azure `Reader` role on customer's capacity resource
- Customer creates Service Principal in their tenant

**Tier 2 - Fabric Admin API (Optional)**
- Workspace metadata and item inventory
- Not implemented in MVP

**Tier 3 - CU Metrics Push (Optional)**
- Detailed CU utilization from Capacity Metrics semantic model
- Customer deploys Fabric notebook in their tenant
- Notebook pushes data to your ingest API

## Step 1: Send Setup Guide to Customer

Send the customer the appropriate setup guide from the `onboarding/` folder:

**English**: 
- Overview: `onboarding/en/customer-guide.md`
- Portal Setup: `onboarding/en/portal.md`
- CLI Script: `onboarding/en/script.md`
- IaC Setup: `onboarding/en/iac.md`

**Dutch**: 
- Overview: `onboarding/nl/customer-guide.md`
- Portal Setup: `onboarding/nl/portal.md`
- CLI Script: `onboarding/nl/script.md`
- IaC Setup: `onboarding/nl/iac.md`

The customer guide provides an overview and three setup options:

**Portal Setup**
- Best for small organizations
- 5-minute Azure Portal walkthrough
- No command line tools required

**CLI Script Setup**
- Best for organizations wanting repeatable setup
- Auditable bash script (`onboarding/setup-customer.sh`)
- Reviewable and repeatable

**Infrastructure as Code (Bicep)**
- Best for enterprises with change management
- Bicep template (`onboarding/setup-customer.bicep`)
- Full audit trail

All three options create identical Service Principals with identical permissions.

## Step 2: Receive Customer Credentials

The customer will send you:
- **Customer Organization Name**
- **Tenant ID** (Azure AD tenant)
- **Client ID** (Application/Service Principal ID)
- **Client Secret** (treat as password)
- **Subscription ID** (Azure subscription containing Fabric capacity)
- **Resource Group** (optional, leave empty to scan entire subscription)

Store these securely until added to your Key Vault in the next step.

## Step 3: Add Customer to Monitoring App

Use the `add-customer.sh` script to register the customer:

```bash
cd backend/scripts
./add-customer.sh https://ca-fabricmon-prod.azurecontainerapps.io
```

The script will prompt you for:
- Customer Name (e.g., "Contoso Corporation")
- Tenant ID (from customer)
- Client ID (from customer)
- Client Secret (from customer)
- Subscription ID (from customer)
- Resource Group (optional, leave empty to scan entire subscription)

On success, the script outputs:
- **Customer ID** (UUID)
- **Ingest Key** (for Tier 3 CU metrics push)

Save the ingest key - the customer will need it if they deploy the Fabric notebook for Tier 3.

### Verify Customer Was Added

```bash
curl https://ca-fabricmon-prod.azurecontainerapps.io/api/customers
```

You should see the new customer in the list with `is_active: true`.

## Step 4: Wait for Automatic Collection

The background collector runs every 15 minutes. It will:
1. Retrieve customer credentials from Key Vault
2. Authenticate to customer's Azure tenant
3. Call ARM API to list Fabric capacities
4. Store capacity metadata (state, SKU, region)
5. Create capacity snapshots

**Wait 15-20 minutes after adding the customer.**

### Monitor Collector Logs

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --follow | grep "collection"
```

Look for these events:
- `collection_cycle_start`
- `capacities_discovered`
- `collection_complete`

### Verify Capacity Data Appeared

```bash
curl https://ca-fabricmon-prod.azurecontainerapps.io/api/customers/<customer-id>/capacities
```

You should see capacity objects with `display_name`, `sku_name`, `state`, and `last_synced_at` fields populated.

### Check Database Directly (Optional)

If you have database access:

```sql
SELECT id, customer_id, display_name, sku_name, state, last_synced_at 
FROM capacities 
WHERE customer_id = '<customer-id>';

SELECT capacity_id, collected_at, state, sku_name 
FROM capacity_snapshots 
WHERE capacity_id IN (SELECT id FROM capacities WHERE customer_id = '<customer-id>')
ORDER BY collected_at DESC 
LIMIT 10;
```

## Step 5: Optional Tier 3 Setup (CU Metrics)

If the customer wants detailed CU utilization metrics (recommended):

### Share Ingest Key with Customer

Send the customer:
- **Ingest Key** (from Step 3)
- **API URL** (your Container App URL)
- **Notebook Template** (`onboarding/extract-metrics-notebook.py`)

### Customer Deploys Fabric Notebook

The customer needs to:
1. Create a new Fabric notebook and paste the code from `extract-metrics-notebook.py`
2. Set `API_URL`, `INGEST_KEY`, and `CAPACITY_NAME` in the configuration section
3. Run once to test, then schedule every 15 minutes

**Requirements:**
- The user who creates/schedules the notebook must have `Capacity Admin` role in Fabric
- The notebook queries the built-in Capacity Metrics semantic model via Semantic Link Labs (`sempy.fabric`)

### Verify Metrics Are Flowing

After the customer schedules the notebook, query the metrics endpoint:

```bash
curl "https://ca-fabricmon-prod.azurecontainerapps.io/api/customers/<customer-id>/capacities/<capacity-id>/metrics?metric_name=CU_Utilization_Pct"
```

You should see metric entries with `metric_name`, `metric_value`, and `collected_at` fields.

## Troubleshooting

### No Capacities Discovered After 15 Minutes

**Check:**
1. Customer credentials are correct
2. Service Principal has Reader role on capacity resource
3. Capacity resource exists in the subscription/resource group specified
4. Collector logs show errors

**Diagnose:**
```bash
# Check collector logs for errors
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 100 | grep -A 5 "collection_failed"

# Common errors:
# - "Authentication failed": Check tenant_id and client_id
# - "Insufficient privileges": Verify Reader role assignment
# - "Resource not found": Check subscription_id and resource_group
```

### Tier 3 Metrics Not Appearing

**Check:**
1. Customer deployed and scheduled the notebook
2. Ingest key is correct in notebook configuration
3. Capacity name matches exactly
4. Notebook runs successfully without errors

**Test ingest endpoint:**
```bash
curl -X POST https://ca-fabricmon-prod.azurecontainerapps.io/api/ingest \
  -H "Content-Type: application/json" \
  -H "X-Ingest-Key: <ingest-key>" \
  -d '{
    "capacity_name": "fabriccap01",
    "metrics": [
      {"name": "CU_Utilization_Pct", "value": 75.0, "aggregation": "Average"}
    ]
  }'
```

Expected response: `202 Accepted`

### Authentication Failures

If the collector logs show authentication failures:

1. Verify the client secret hasn't expired
2. Check the Service Principal exists in the customer's tenant
3. Confirm the Service Principal has the Reader role assigned

Ask the customer to verify in Azure Portal:
- **Entra ID > App registrations** - Service Principal exists
- **Fabric Capacity > Access control (IAM)** - Service Principal has Reader role

### Container App Not Responding

```bash
# Health check
curl https://ca-fabricmon-prod.azurecontainerapps.io/health

# If timeout, check app logs
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 50
```

## Deactivating a Customer

To stop collecting data from a customer:

### Deactivate via API

```bash
curl -X DELETE https://ca-fabricmon-prod.azurecontainerapps.io/api/customers/<customer-id> \
  -H "X-Admin-Key: <admin-api-key>"
```

This sets `is_active = false` in the database:
- Ingest endpoint rejects requests (403)
- Collector skips customer in next cycle (up to 15-minute delay)

### Customer Revokes Access

The customer can remove access anytime:

```bash
az role assignment delete \
  --assignee <service-principal-id> \
  --scope <capacity-resource-id>
```

Effect: Service Principal can no longer call Azure APIs (2-5 minute propagation)

## Onboarding Multiple Customers

Repeat Steps 1-3 for each new customer. The background collector handles all customers automatically.

Each customer gets:
- Isolated credentials in Key Vault (`customer-{uuid}-secret`)
- Isolated data in database (enforced by `customer_id` foreign keys)
- Unique ingest key for Tier 3 metrics

## Next Steps

After successful onboarding:
- [Connect Power BI](powerbi-setup.md) to visualize capacity data
- [Monitor operations](operations.md) for logs and health checks
- [Review security model](security.md) for access control and data isolation

## Related Documentation

- [Deployment Guide](deployment.md) - Initial infrastructure setup
- [Operations Guide](operations.md) - Day-to-day maintenance
- [Power BI Setup](powerbi-setup.md) - Building dashboards
- [Architecture](architecture.md) - System design
- [Security](security.md) - Security model
