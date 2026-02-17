# First Customer Onboarding Walkthrough

Complete end-to-end guide for onboarding your first customer and verifying data collection.

## Prerequisites

Before starting:
- Infrastructure deployed to Azure (see [deployment.md](deployment.md))
- Backend application running successfully
- Container App URL available (e.g., `https://ca-fabricmon-prod.azurecontainerapps.io`)

Allow 30-45 minutes for the full process (most of it is waiting for the background collector).

## Step 1: Customer Setup (Tier 1)

The customer needs to create a Service Principal and grant it Reader access to their Fabric capacity.

### Option A: Customer Uses CLI Script

Send the customer `onboarding/setup-customer.sh` and these instructions:

```bash
# 1. Sign in to Azure
az login

# 2. Run the setup script
bash setup-customer.sh

# 3. Follow the prompts:
#    - Enter subscription ID
#    - Enter capacity resource ID (or leave empty to scan entire subscription)
#    - Script creates App Registration and grants Reader role

# 4. Send you these outputs:
#    - Tenant ID
#    - Client ID
#    - Client Secret
#    - Subscription ID
```

### Option B: Customer Uses Azure Portal

Send the customer `onboarding/README.md` and point them to the "Quick Portal Setup" section.

The customer will:
1. Create an App Registration in Azure Portal
2. Create a client secret
3. Grant the Service Principal "Reader" role on their Fabric capacity resource
4. Send you: Tenant ID, Client ID, Client Secret, Subscription ID

The client secret is only used once during onboarding, then stored in Azure Key Vault.

## Step 2: Add Customer to Monitoring App

Use the `add-customer.sh` script to add the customer:

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
- Resource Group (optional - leave empty to scan entire subscription)

On success, the script outputs a **Customer ID** and an **Ingest Key** (used for Tier 3 CU metrics push). Save the ingest key -- the customer will need it for their Fabric notebook configuration.

### Verify Customer Was Added

```bash
curl https://ca-fabricmon-prod.azurecontainerapps.io/api/customers
```

## Step 3: Wait for Automatic Collection

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

Look for `collection_cycle_start`, `capacities_discovered`, and `collection_complete` events.

### Verify Capacity Data Appeared

```bash
curl https://ca-fabricmon-prod.azurecontainerapps.io/api/customers/<customer-id>/capacities
```

You should see capacity objects with `display_name`, `sku_name`, `state`, and `last_synced_at` fields populated.

### Check Database Directly (Optional)

If you have database access (see [howto.md](howto.md#connect-to-the-database-debugging)):

```sql
SELECT id, customer_id, display_name, sku_name, state, last_synced_at FROM capacities;
SELECT capacity_id, collected_at, state, sku_name FROM capacity_snapshots ORDER BY collected_at DESC LIMIT 10;
```

## Step 4: Optional Tier 3 Setup (CU Metrics Push)

If the customer wants detailed CU utilization metrics (recommended):

### A. Send Ingest Key to Customer

Share the ingest key (from Step 2) and your API URL with the customer.

### B. Customer Deploys Fabric Notebook

Send the customer `onboarding/extract-metrics-notebook.py`. They need to:

1. Create a new Fabric notebook and paste the code
2. Set `API_URL`, `INGEST_KEY`, and `CAPACITY_NAME` in the configuration section
3. Run once to test, then schedule every 15 minutes

The notebook user must have Fabric **Capacity Admin** role. It queries the built-in Capacity Metrics semantic model via Semantic Link Labs (`sempy.fabric`).

### C. Verify Metrics Are Flowing

After the customer schedules the notebook, query the metrics endpoint:

```bash
curl "https://ca-fabricmon-prod.azurecontainerapps.io/api/customers/<customer-id>/capacities/<capacity-id>/metrics?metric_name=CU_Utilization_Pct"
```

You should see metric entries with `metric_name`, `metric_value`, and `collected_at` fields.

## Step 5: Build Power BI Dashboard

Now that data is flowing, connect Power BI to visualize it. Follow [powerbi-setup.md](powerbi-setup.md) for connection options and dashboard examples.

## Troubleshooting

### No Capacities Discovered After 15 Minutes

**Check:**
1. Customer credentials are correct
2. Service Principal has Reader role on capacity resource
3. Capacity resource exists in the subscription/resource group specified
4. Collector logs show errors

**Solution:**
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
  -H "X-Ingest-Key: VeryLongSecureRandomString123ABC..." \
  -d '{
    "capacity_name": "fabriccap01",
    "metrics": [
      {"name": "CU_Utilization_Pct", "value": 75.0, "aggregation": "Average"}
    ]
  }'
```

### Container App Not Responding

**Check:**
```bash
# Health check
curl https://ca-fabricmon-prod.azurecontainerapps.io/health

# If timeout, check app logs
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 50
```

## Next Customers

Repeat Steps 1-2 for each new customer. The background collector handles all customers automatically.

## What's Next

- [Monitor operations and logs](howto.md#part-3-operations)
- [Scale to Enterprise tier](howto.md#scale-from-starter-to-enterprise)
- [Build advanced Power BI dashboards](powerbi-setup.md)
- [Add alerting and notifications](architecture.md) (future feature)
