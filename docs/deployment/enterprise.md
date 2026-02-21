# Enterprise Deployment with CI/CD

**Recommended for**: Large organizations, enterprises with existing DevOps processes

**Time**: 30 minutes  
**Requirements**: Azure CLI, Git, GitHub/Azure DevOps, Bicep knowledge

Use this method for Infrastructure-as-Code deployments with automated CI/CD pipelines.

## Prerequisites

- Azure CLI installed and configured
- Git and GitHub/Azure DevOps account
- Bicep CLI (`az bicep version` to check)
- Azure subscription with Owner or Contributor access
- Understanding of CI/CD concepts

## Option A: GitHub Actions

### Step 1: Fork the Repository

Fork the repository to your GitHub organization for full control.

### Step 2: Create Azure Service Principal

Create a Service Principal that GitHub Actions will use:

```bash
az ad sp create-for-rbac \
  --name "GitHub-FabricMonitor-Deploy" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

Copy the entire JSON output.

### Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AZURE_CREDENTIALS` | JSON from previous step | Service Principal credentials |
| `ACR_NAME` | `acrfabricmon<unique>` | Container Registry name |
| `CONTAINER_APP_NAME` | `ca-fabricmon-<env>` | Container App name |
| `RESOURCE_GROUP` | `rg-fabricmon-<env>` | Resource Group name |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Azure subscription ID |

### Step 4: Deploy Infrastructure

The repository includes a GitHub Actions workflow that automatically:
1. Deploys infrastructure on push to `main`
2. Builds and pushes Docker images
3. Updates the Container App

Trigger the workflow:

```bash
git push origin main
```

Monitor progress in the Actions tab.

### GitHub Actions Workflow

The workflow file `.github/workflows/deploy.yml` handles:
- Infrastructure deployment (Bicep templates)
- Container image build and push
- Container App updates
- Automated testing

## Option B: Azure DevOps

### Step 1: Create Azure DevOps Project

Create a new project in Azure DevOps for your deployment.

### Step 2: Import Repository

Import the GitHub repository or clone it to Azure Repos.

### Step 3: Create Service Connection

1. Go to Project Settings → Service connections
2. Create new Azure Resource Manager connection
3. Use Service Principal authentication
4. Grant access to your subscription

### Step 4: Create Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  resourceGroup: 'rg-fabricmon-prod'
  location: 'eastus'
  appName: 'fabricmon'
  environmentType: 'Enterprise'

stages:
  - stage: Deploy
    jobs:
      - job: DeployInfrastructure
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'Azure-Service-Connection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az deployment group create \
                  --resource-group $(resourceGroup) \
                  --template-file infra/main.bicep \
                  --parameters appName=$(appName) environmentType=$(environmentType)
          
          - task: Docker@2
            inputs:
              containerRegistry: 'ACR-Service-Connection'
              repository: 'fabricmon'
              command: 'buildAndPush'
              Dockerfile: 'backend/Dockerfile'
```

### Step 5: Run Pipeline

Commit and push to trigger the pipeline.

## Direct Bicep Deployment

For manual Infrastructure-as-Code deployment without CI/CD:

### Step 1: Review Bicep Templates

Review the templates in `infra/`:
- `main.bicep` - Main orchestrator
- `modules/` - Individual resource modules

### Step 2: Customize Parameters

Create a parameter file `infra/main.parameters.json`:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appName": {
      "value": "fabricmon"
    },
    "environmentType": {
      "value": "Enterprise"
    },
    "alertEmails": {
      "value": "ops@company.com,alerts@company.com"
    }
  }
}
```

### Step 3: Deploy

```bash
# Create resource group
az group create \
  --name rg-fabricmon-prod \
  --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group rg-fabricmon-prod \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

### Step 4: Deploy Application

```bash
# Build and push image
az acr build \
  --registry acrfabricmonxyz \
  --image fabricmon:latest \
  --file backend/Dockerfile \
  backend/

# Update Container App
az containerapp update \
  --name ca-fabricmon-prod \
  --resource-group rg-fabricmon-prod \
  --image acrfabricmonxyz.azurecr.io/fabricmon:latest
```

## Infrastructure as Code Best Practices

### Version Control

- Store Bicep templates in version control
- Use parameter files for environment-specific values
- Never commit secrets (use Azure Key Vault references)
- Tag releases for production deployments

### Change Management

- Use pull requests for infrastructure changes
- Require code reviews for Bicep modifications
- Test changes in dev/staging before production
- Document breaking changes in commit messages

### Environment Strategy

Maintain separate environments:

```bash
# Development
az deployment group create \
  --resource-group rg-fabricmon-dev \
  --template-file infra/main.bicep \
  --parameters appName=fabricmondev environmentType=Starter

# Staging
az deployment group create \
  --resource-group rg-fabricmon-staging \
  --template-file infra/main.bicep \
  --parameters appName=fabricmonstg environmentType=Enterprise

# Production
az deployment group create \
  --resource-group rg-fabricmon-prod \
  --template-file infra/main.bicep \
  --parameters appName=fabricmon environmentType=Enterprise
```

### Monitoring Deployments

Enable deployment logging:

```bash
az deployment group show \
  --resource-group rg-fabricmon-prod \
  --name main \
  --query properties.outputs
```

## Advanced Configuration

### Multi-Region Deployment

Deploy to multiple regions for disaster recovery:

```bash
# Primary region
az deployment group create \
  --resource-group rg-fabricmon-eastus \
  --template-file infra/main.bicep \
  --parameters appName=fabricmoneast environmentType=Enterprise location=eastus

# Secondary region
az deployment group create \
  --resource-group rg-fabricmon-westus \
  --template-file infra/main.bicep \
  --parameters appName=fabricmonwest environmentType=Enterprise location=westus
```

### Custom Networking

Modify `infra/modules/network.bicep` for custom VNET configurations:
- Custom address spaces
- Additional subnets
- Network security group rules
- Private Link configurations

### High Availability

Enterprise tier includes:
- Zone-redundant PostgreSQL high availability
- Geo-redundant backups (35 days retention)
- Multiple Container App replicas
- Azure Monitor alerts

## Security Considerations

### Managed Identity

The deployment uses User Assigned Managed Identity for:
- Pulling images from ACR (`AcrPull` role)
- Reading secrets from Key Vault (`Key Vault Secrets User` role)

No connection strings or passwords in environment variables.

### Network Isolation

- PostgreSQL database is VNET-integrated with no public endpoint
- Network Security Groups restrict traffic to app subnet only
- Private DNS for internal name resolution
- TLS 1.2+ required for all connections

### Secrets Management

All secrets stored in Azure Key Vault:
- Database password
- Customer Service Principal credentials
- Admin API key

Access via Managed Identity only.

## Troubleshooting

### Bicep Validation Errors

Validate templates before deployment:

```bash
az bicep build --file infra/main.bicep
```

### Deployment Failures

View detailed error messages:

```bash
az deployment group show \
  --resource-group rg-fabricmon-prod \
  --name main \
  --query properties.error
```

### Pipeline Failures

Check service principal permissions:
- Contributor role on subscription
- Ability to create resource groups
- Access to Azure Container Registry

## Next Steps

After successful deployment:

1. [Add your first customer](../onboarding.md) to start collecting capacity metrics
2. [Connect Power BI](../powerbi-setup.md) to visualize capacity data
3. [Review operations guide](../operations.md) for day-to-day maintenance
4. Set up automated backups and disaster recovery procedures
5. Configure monitoring dashboards in Azure Monitor

## Related Documentation

- [Portal Deployment](portal.md) - No-code deployment via Azure Portal
- [CLI Deployment](cli.md) - Quick script-based deployment
- [Operations Guide](../operations.md) - Day-to-day maintenance
- [Architecture](../architecture.md) - System design and components
- [Security](../security.md) - Security architecture and best practices
