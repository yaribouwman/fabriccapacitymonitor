# Deployment Guide

Complete guide for deploying the Fabric Capacity Monitor to Azure.

## Prerequisites

Before you begin, ensure you have:

- Azure CLI installed and logged in (`az login`)
- Docker installed (for local image testing, optional)
- Git installed
- GitHub account with repository created
- Azure subscription with Owner or Contributor access

## One-Time Setup

### 1. Clone and Configure Repository

```bash
git clone https://github.com/yaribouwman/fabriccapacitymonitor.git
cd fabriccapacitymonitor
```

### 2. Create Azure Service Principal for GitHub Actions

Create a Service Principal that GitHub Actions will use to deploy resources:

```bash
az ad sp create-for-rbac \
  --name "GitHub-FabricMonitor-Deploy" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

Copy the entire JSON output. You'll need it in the next step.

### 3. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AZURE_CREDENTIALS` | JSON from previous step | Service Principal credentials |
| `ACR_NAME` | `acrfabricmon<unique>` | Container Registry name (will be created) |
| `CONTAINER_APP_NAME` | `ca-fabricmon-<env>` | Container App name (will be created) |
| `RESOURCE_GROUP` | `rg-fabricmon-<env>` | Resource Group name |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Azure subscription ID |

## Infrastructure Deployment

### Option A: Deploy via CLI Script

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
- `-n` App name (3-20 characters, alphanumeric)
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

### Option B: Deploy via Azure Portal Button

Click the "Deploy to Azure" button in README.md and fill in the form.

## Backend Deployment

### Automatic Deployment (Recommended)

Push to `main` and GitHub Actions will build the Docker image, push to GHCR and ACR, and update the Container App. Monitor progress in the repository's Actions tab (typical build: 3-5 minutes).

### Manual Deployment (For Testing)

If you need to deploy manually:

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

## Database Initialization

The database schema is automatically initialized on first container startup via Alembic migrations. Verify by checking container logs for `"Database migrations completed successfully"`:

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --follow
```

## Verification

### 1. Health Check

Test the API is responding:

```bash
CONTAINER_APP_URL="https://ca-fabricmon-prod.azurecontainerapps.io"

curl $CONTAINER_APP_URL/health
```

**Expected response:**
```json
{"status": "ok", "version": "0.1.0"}
```

### 2. API Documentation

Visit `https://ca-fabricmon-prod.azurecontainerapps.io/docs` for interactive Swagger documentation.

### 3. Database Connectivity

If the health check passes, database connectivity is working. Check container logs for errors if it doesn't.

### 4. Run API Test Script

```bash
cd backend
./scripts/test-api.sh https://ca-fabricmon-prod.azurecontainerapps.io
```

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

### Background Collector Not Running

```bash
az containerapp logs show \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --tail 200 | grep "collection"
```

Look for `collection_cycle_start` and `collection_complete` events. If absent, verify active customers exist.

### Key Vault Access Denied

Verify the managed identity has `Key Vault Secrets User` role and that Key Vault network rules allow access:

```bash
az keyvault show \
  --name kv-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --query "properties.networkAcls"
```

## Post-Deployment Configuration

Common `az containerapp update` operations:

```bash
# Update image
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --image acrfabricmonxyz.azurecr.io/fabricmon:v1.0.1

# Scale replicas
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --min-replicas 1 \
  --max-replicas 5

# Update environment variables
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --set-env-vars "COLLECTOR_INTERVAL_MINUTES=10" "LOG_LEVEL=DEBUG"
```

## Security Considerations

### Managed Identity

The Container App uses a User Assigned Managed Identity for:
- Pulling images from ACR (`AcrPull` role)
- Reading secrets from Key Vault (`Key Vault Secrets User` role)

**Never** use connection strings or passwords in environment variables. Always use Key Vault references.

### Database Access

The PostgreSQL database is VNET-integrated with no public endpoint. Only the Container App subnet can access it.

For administrative access, use:
```bash
az postgres flexible-server connect \
  --name pg-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --admin-user dbadmin
```

### Secrets Management

All secrets are stored in Azure Key Vault:
- Database password
- Customer Service Principal credentials

To view secrets:
```bash
az keyvault secret show \
  --vault-name kv-fabricmon-prod \
  --name db-connection-string
```

## Next Steps

After successful deployment:

1. **Add your first customer:** See [onboarding.md](onboarding.md)
2. **Connect Power BI:** See [powerbi-setup.md](powerbi-setup.md)
3. **Monitor operations:** See [operations.md](operations.md)

## Support

For issues:
1. Check container logs: `az containerapp logs show`
2. Review [architecture.md](architecture.md) for system design
3. Check [decisions.md](decisions.md) for architectural decisions
4. Open an issue in the GitHub repository
