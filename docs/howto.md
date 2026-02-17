# How-To Guide

## Part 1: Self-Hosting Deployment

Deploy the monitoring infrastructure to your Azure subscription.

### Deploy via Button (Azure Portal)

1. Click the "Deploy to Azure" button in the README
2. Sign in to your Azure account
3. Fill in the form:
   - **Subscription**: Choose your Azure subscription
   - **Resource Group**: Create new or select existing
   - **Region**: Choose an Azure region (e.g., East US)
   - **App Name**: Enter a name (3-20 characters, alphanumeric)
   - **Environment Type**: Choose Starter or Enterprise
4. Click "Review + Create"
5. Wait 10-15 minutes for deployment to complete
6. Copy the Container App URL from the deployment outputs

### Deploy via CLI (Local)

Prerequisites:
- Azure CLI installed and logged in
- Bash shell (Linux, macOS, WSL, or Git Bash on Windows)

```bash
git clone https://github.com/yaribouwman/fabriccapacitymonitor.git
cd fabriccapacitymonitor

./deploy.sh \
  -g rg-fabricmon-prod \
  -l eastus \
  -n fabricmon \
  -e Enterprise
```

The script will:
- Check that Azure CLI is installed and you're logged in
- Generate a secure database password
- Create the resource group if it doesn't exist
- Deploy all infrastructure using Bicep
- Print the Container App URL and Container Registry name

### Deploy via CI/CD Pipeline

#### GitHub Actions

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy Bicep
        uses: azure/arm-deploy@v1
        with:
          scope: resourcegroup
          resourceGroupName: rg-fabricmon-prod
          template: ./infra/main.bicep
          parameters: >
            appName=fabricmon
            environmentType=Enterprise
            databaseAdminPassword=${{ secrets.DB_PASSWORD }}
```

#### Azure DevOps

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: 'Azure-Service-Connection'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        az deployment group create \
          --resource-group rg-fabricmon-prod \
          --template-file infra/main.bicep \
          --parameters appName=fabricmon environmentType=Enterprise
```

## Part 2: Connecting Customer Fabric Data

Customer onboarding uses a three-tier data collection model. Tier 1 is required. Tier 2 and 3 are optional.

### Tier 1: Azure Reader (Automatic Pull)

The monitoring app automatically pulls capacity state, SKU, and region from Azure Resource Manager API. Requires only Azure `Reader` role on the capacity resource.

#### Option A: Quick Setup (Small Organizations)

For customers who want a simple, fast setup with portal clicks. 5-minute guide, no scripts.

**What the customer does:**

1. Sign in to Azure Portal and go to **Entra ID > App Registrations**
2. Click **New registration**
   - Name: `FabricCapacityMonitor-ReadOnly`
   - Supported account types: "Accounts in this organizational directory only"
   - Click **Register**
3. On the app's overview page, copy the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Certificates & secrets** > **New client secret**
   - Description: `Fabric Capacity Monitor Access`
   - Expires: 12 months (or your org's policy)
   - Click **Add** and copy the **Value** (you can't see it again)
5. Go to your Fabric capacity resource in the Azure Portal
   - Navigate to **Subscriptions** > **Resource groups** > find your Fabric capacity
   - Click on the capacity resource
   - Go to **Access control (IAM)** > **Add role assignment**
   - Select role: **Reader**
   - Assign access to: **User, group, or service principal**
   - Search for `FabricCapacityMonitor-ReadOnly` and select it
   - Click **Review + assign**
6. Send back to your consulting company:
   - Tenant ID
   - Client ID
   - Client Secret
   - Subscription ID
   - Capacity Resource ID (or leave blank to scan entire subscription)

**Important**: The service principal has read-only access to Azure resource metadata only. It cannot read Fabric artifacts or data. Access can be revoked instantly by removing the role assignment.

#### Option B: CLI Script (Medium Organizations)

For customers who want a repeatable, auditable script. Review the script first, then run it.

**What the customer does:**

1. Clone this repository or download `onboarding/setup-customer.sh`
2. Review the script (see `onboarding/README.md` for full details)
3. Sign in to Azure: `az login`
4. Run the script: `bash onboarding/setup-customer.sh`
5. The script outputs:
   - Tenant ID
   - Client ID
   - Client Secret
   - Subscription ID
   - Resource ID (if provided)
6. Send these credentials to your consulting company

The script creates the App Registration, Service Principal, and grants Reader role.

#### Option C: Auditable IaC (Enterprise Organizations)

For customers who require Infrastructure-as-Code for change management and audit trails.

**What the customer does:**

1. Clone this repository or download the `onboarding/` folder
2. Review `onboarding/setup-customer.bicep` and `onboarding/README.md`
3. Put the Bicep template through your change management process
4. Deploy the template:

```bash
az login
az deployment subscription create \
  --location eastus \
  --template-file onboarding/setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

5. The deployment outputs:
   - Tenant ID
   - Client ID
   - Service Principal ID
6. Create a client secret manually in the portal (Bicep cannot output secrets)
7. Send the credentials to your consulting company

### Tier 2: Fabric Admin API (Optional)

For workspace metadata and item inventory. Requires Fabric Admin API tenant setting enabled and Service Principal added to a security group.

This tier is documented but not required for MVP. If needed, see ADR-007 in `docs/decisions.md`.

### Tier 3: CU Metrics (Notebook Push)

For detailed CU utilization, overload, and throttling metrics. Customer deploys a Fabric notebook that queries the Capacity Metrics semantic model and pushes data to your monitoring API.

**What the customer does:**

1. Receive an **Ingest Key** from your consulting company (generated when they add you to the monitoring app)
2. Copy the notebook template from `onboarding/extract-metrics-notebook.py`
3. Create a new Fabric notebook in any workspace in their tenant
4. Paste the notebook code
5. Configure the notebook parameters:
   - `API_URL`: The monitoring API endpoint (provided by your consulting company)
   - `INGEST_KEY`: The ingest key (provided by your consulting company)
   - `CAPACITY_NAME`: The name of the capacity to monitor
6. Schedule the notebook to run every 15 minutes using Fabric notebook scheduling

**Requirements:**
- The user who creates/schedules the notebook must have `Capacity Admin` role in Fabric
- The notebook queries the `Capacity Metrics` semantic model (built-in, no setup needed)
- The notebook uses Semantic Link Labs (`sempy.fabric`)

**Data pushed:**
- CU Utilization %
- Overloaded Minutes
- Throttled Operations

This data is stored in your monitoring app's database for long-term retention and cross-customer dashboards.

## Part 3: Operations

For detailed deployment instructions, see [docs/deployment.md](deployment.md).

### Push Your Container Image

Backend deployment is automatic via GitHub Actions on push to `main`. For manual deployment, see [deployment.md](deployment.md#manual-deployment-for-testing).

### Connect to the Database (Debugging)

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

> **Security warning:** This opens the database to the entire internet. Only use for short debugging sessions and disable immediately after. Prefer Azure Bastion or a jump box for production environments.

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

### View Logs

Stream Container App logs:

```bash
az containerapp logs show \
  --name ca-fabricmon-<unique-id> \
  --resource-group rg-fabricmon-prod \
  --follow
```

Query logs with Log Analytics:

```bash
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h) | order by TimeGenerated desc"
```
