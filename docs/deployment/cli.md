# Deploy via CLI Script

**Recommended for**: IT teams, developers, automation scenarios

**Time**: 10 minutes  
**Requirements**: Azure CLI, bash shell, command line familiarity

Use the deployment script for automation, CI/CD pipelines, or when you prefer command-line tools.

## Prerequisites

- Azure CLI installed (`az --version` to check)
- Bash shell (Linux, macOS, WSL, or Git Bash on Windows)
- Git installed
- Azure subscription with Owner or Contributor access
- Logged in to Azure (`az login`)

## Step 1: Clone the Repository

```bash
git clone https://github.com/yaribouwman/fabriccapacitymonitor.git
cd fabriccapacitymonitor
```

## Step 2: Run the Deployment Script

```bash
./deploy.sh \
  -g rg-fabricmon-prod \
  -l eastus \
  -n fabricmon \
  -e Enterprise
```

**Parameters:**
- `-g` Resource Group name
- `-l` Azure region (eastus, westus2, westeurope, etc.)
- `-n` App name (3-20 characters, alphanumeric only)
- `-e` Environment type (Starter or Enterprise)

The script will:
1. Generate a secure database password
2. Create the resource group if it doesn't exist
3. Deploy all Bicep templates
4. Output the Container App URL and Container Registry name

**Expected output:**
```
Deployment completed successfully!
Container App URL: https://ca-fabricmon-prod.azurecontainerapps.io
Container Registry: acrfabricmonxyz.azurecr.io
```

## Step 3: Verify Deployment

### Health Check

Test the API is responding:

```bash
CONTAINER_APP_URL="https://ca-fabricmon-prod.azurecontainerapps.io"

curl $CONTAINER_APP_URL/health
```

**Expected response:**
```json
{"status": "ok", "version": "0.1.0"}
```

### API Documentation

Visit the API documentation:

```bash
open $CONTAINER_APP_URL/docs  # macOS
xdg-open $CONTAINER_APP_URL/docs  # Linux
start $CONTAINER_APP_URL/docs  # Windows
```

### View Logs

Check application startup:

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --follow
```

Look for:
- `Database migrations completed successfully`
- `Application startup complete`
- `Uvicorn running on http://0.0.0.0:8080`

## Updating the Deployment

To update with new parameters:

```bash
az deployment group create \
  --resource-group rg-fabricmon-prod \
  --template-file infra/main.bicep \
  --parameters appName=fabricmon environmentType=Enterprise
```

## Troubleshooting

### Container App Won't Start

Check logs:

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 100
```

Common causes: failed database connection (check Key Vault secret), failed migration (check database state), or failed image pull (check ACR identity role).

### Database Issues

Verify PostgreSQL server status:

```bash
az postgres flexible-server show \
  --resource-group rg-fabricmon-prod \
  --name psql-fabricmon-prod
```

### Cannot Pull Image from ACR

Verify managed identity has `AcrPull` role. If missing, re-run the deployment.

### Key Vault Access Denied

Verify managed identity has `Key Vault Secrets User` role:

```bash
az keyvault show \
  --name kv-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --query "properties.networkAcls"
```

## Manual Backend Deployment

If you need to deploy custom code changes:

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

## Post-Deployment Configuration

### Scale Replicas

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

## Next Steps

After successful deployment:

1. [Add your first customer](../onboarding.md) to start collecting capacity metrics
2. [Connect Power BI](../powerbi-setup.md) to visualize capacity data
3. [Review operations guide](../operations.md) for day-to-day maintenance

## Related Documentation

- [Portal Deployment](portal.md) - No-code deployment via Azure Portal
- [Enterprise Deployment](enterprise.md) - For large organizations with CI/CD
- [Operations Guide](../operations.md) - Day-to-day maintenance
- [Architecture](../architecture.md) - System design and components
