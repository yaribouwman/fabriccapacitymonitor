# Operations Guide

Day-to-day operations and maintenance tasks for the Fabric Capacity Monitor.

## Deploying Container Updates

Backend deployment is automatic via GitHub Actions on push to `main`. For manual deployment:

### Manual Container Deployment

```bash
# Get ACR name from infrastructure output
ACR_NAME="acrfabricmonxyz"

# Login to ACR
az acr login --name $ACR_NAME

# Build the image
cd backend
docker build -t fabricmon:latest .

# Tag for ACR
docker tag fabricmon:latest $ACR_NAME.azurecr.io/fabricmon:latest

# Push to ACR
docker push $ACR_NAME.azurecr.io/fabricmon:latest

# Update Container App
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --image $ACR_NAME.azurecr.io/fabricmon:latest
```

### Update Image Version

```bash
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --image acrfabricmonxyz.azurecr.io/fabricmon:v1.0.1
```

## Database Operations

### Connect to the Database

The database is not publicly accessible. To connect for debugging:

1. Retrieve the connection string from Key Vault:

```bash
KV_NAME="kv-fabricmon-<unique-id>"

az keyvault secret show \
  --vault-name $KV_NAME \
  --name db-connection-string \
  --query value -o tsv
```

2. Use Azure Bastion or a jump box in the VNET, or enable temporary public access:

**Security warning:** This opens the database to the entire internet. Only use for short debugging sessions and disable immediately after. Prefer Azure Bastion or a jump box for production environments.

```bash
az postgres flexible-server update \
  --name psql-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --public-access 0.0.0.0-255.255.255.255

psql "<connection-string>"

# Disable public access immediately after debugging
az postgres flexible-server update \
  --name psql-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --public-access None
```

### Rotate Database Password

1. Generate a new password:

```bash
NEW_PASSWORD=$(openssl rand -base64 32)
```

2. Update the PostgreSQL server:

```bash
az postgres flexible-server update \
  --name psql-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --admin-password "$NEW_PASSWORD"
```

3. Update Key Vault secret:

```bash
NEW_CONNECTION_STRING="postgresql://dbadmin:$NEW_PASSWORD@psql-fabricmon-<unique-id>.postgres.database.azure.com:5432/fabricmon?sslmode=require"

az keyvault secret set \
  --vault-name kv-fabricmon-<unique-id> \
  --name db-connection-string \
  --value "$NEW_CONNECTION_STRING"
```

4. Restart the Container App to pick up the new secret:

```bash
az containerapp revision restart \
  --name ca-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod
```

## Scaling Operations

### Scale Container App Replicas

```bash
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --min-replicas 1 \
  --max-replicas 5
```

### Update Environment Variables

```bash
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --set-env-vars "COLLECTOR_INTERVAL_MINUTES=10" "LOG_LEVEL=DEBUG"
```

### Scale from Starter to Enterprise

Re-deploy with the Enterprise tier parameter:

```bash
az deployment group create \
  --resource-group rg-fabricmon-prod \
  --template-file infra/main.bicep \
  --parameters appName=fabricmon environmentType=Enterprise
```

This will:
- Scale up the PostgreSQL server to a higher SKU
- Enable geo-redundant backup
- Enable zone-redundant high availability
- Increase Container App CPU and memory
- Set minimum replicas to 1 (disable scale-to-zero)

Note: Scaling the database causes a brief restart (1-2 minutes of downtime).

## Monitoring and Logs

### View Container App Logs

Stream logs in real-time:

```bash
az containerapp logs show \
  --name ca-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --follow
```

View recent logs:

```bash
az containerapp logs show \
  --name ca-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --tail 100
```

### Query Logs with Log Analytics

```bash
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h) | order by TimeGenerated desc"
```

### Monitor Background Collector

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 200 | grep "collection"
```

Look for `collection_cycle_start`, `capacities_discovered`, and `collection_complete` events.

## Security Operations

### Rotate Admin API Key

```bash
az keyvault secret set \
  --vault-name kv-fabricmon-<unique-id> \
  --name admin-api-key \
  --value $(openssl rand -base64 32)

az containerapp revision restart \
  --name ca-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod
```

### Rotate Customer Ingest Key

```sql
UPDATE customers 
SET ingest_key = gen_random_uuid() 
WHERE id = '<customer_id>';
```

Then notify the customer to update their Fabric notebook configuration.

## Troubleshooting

### Container App Won't Start

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 100
```

Common causes: failed database connection (check Key Vault secret), failed migration (check database state), or failed image pull (check ACR identity role).

### Database Migration Fails

Verify the PostgreSQL server state is "Ready" and the managed identity has access:

```bash
az postgres flexible-server show \
  --resource-group rg-fabricmon-prod \
  --name pg-fabricmon-prod
```

### Cannot Pull Image from ACR

Verify the managed identity has `AcrPull` role on the registry. If missing, re-run the infrastructure deployment.

### Key Vault Access Denied

Verify the managed identity has `Key Vault Secrets User` role and that Key Vault network rules allow access:

```bash
az keyvault show \
  --name kv-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --query "properties.networkAcls"
```

## Related Documentation

- [Deployment Guide](deployment.md) - Initial infrastructure setup
- [Customer Onboarding](onboarding.md) - Adding customers to the system
- [Architecture](architecture.md) - System design and components
- [Security](security.md) - Security model and best practices
