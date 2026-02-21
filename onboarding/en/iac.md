# Infrastructure as Code Setup (Bicep)

**Recommended for**: Enterprises with change management requirements

**Time**: 10 minutes  
**Requirements**: Azure CLI, Bicep knowledge, change management process

Infrastructure-as-Code template for enterprise change management and audit trails.

## Prerequisites

- Azure CLI with Bicep installed
- Familiarity with Azure Bicep/ARM templates
- Your organization's change management process
- Azure Administrator or Owner role on your Fabric capacity

## Step 1: Download the Bicep Template

Download these files from your consultant or GitHub repository:
- `setup-customer.bicep`
- `bicepconfig.json` (optional)

## Step 2: Review the Template

Review the Bicep template to understand the resources being created:

```bash
cat setup-customer.bicep
```

The template creates:
1. Azure AD App Registration
2. Service Principal
3. Role assignment (Reader) on the Fabric capacity

## Step 3: Submit for Change Management

If your organization requires change management for infrastructure changes, submit the Bicep template through your standard approval process.

Include in your change request:
- Description: "Create read-only Service Principal for Fabric capacity monitoring"
- Risk level: Low (read-only access, scoped to single resource)
- Rollback plan: Delete App Registration via `az ad app delete`

## Step 4: Deploy the Template

```bash
az login

az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

Replace the `capacityResourceId` with your actual Fabric capacity resource ID.

To find your capacity resource ID:

```bash
az resource list \
  --resource-type "Microsoft.Fabric/capacities" \
  --query "[].id" -o tsv
```

## Step 5: Get Deployment Outputs

The deployment outputs:
- Tenant ID
- Client ID
- Service Principal ID

Example:

```bash
az deployment subscription show \
  --name setup-customer \
  --query properties.outputs
```

## Step 6: Create Client Secret Manually

Bicep cannot output secrets for security reasons. Create the client secret manually:

### Via Portal:
1. Go to Azure Portal → **Entra ID** → **App registrations**
2. Find `FabricCapacityMonitor-ReadOnly`
3. Go to **Certificates & secrets** → **New client secret**
4. Copy the secret value

### Via CLI:
```bash
az ad app credential reset \
  --id <application-id> \
  --append \
  --display-name "Fabric Monitor Access" \
  --years 2
```

Copy the `password` value from the output.

## Step 7: Send Credentials to Your Consultant

Send these values to your consultant via secure channel:
- Tenant ID (from deployment output)
- Client ID (from deployment output)
- Client Secret (from step 6)
- Subscription ID
- Resource Group
- Capacity Name

## Deployment Parameters

The Bicep template accepts these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `appName` | Yes | Name for the App Registration |
| `capacityResourceId` | Yes | Full resource ID of your Fabric capacity |
| `location` | No | Azure region (defaults to deployment location) |

Example parameter file (`setup-customer.parameters.json`):

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appName": {
      "value": "FabricCapacityMonitor-ReadOnly"
    },
    "capacityResourceId": {
      "value": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-fabric-prod/providers/Microsoft.Fabric/capacities/fabriccap01"
    }
  }
}
```

Deploy with parameter file:

```bash
az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters setup-customer.parameters.json
```

## Validating the Deployment

Validate the template before deploying:

```bash
az deployment subscription validate \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

## Verifying the Setup

Check the App Registration:

```bash
az ad app list --display-name "FabricCapacityMonitor-ReadOnly"
```

Check the role assignment:

```bash
az role assignment list \
  --scope /subscriptions/.../Microsoft.Fabric/capacities/... \
  --role "Reader"
```

## Deployment Logs

View deployment logs:

```bash
az deployment subscription show \
  --name setup-customer \
  --query properties.error
```

## Troubleshooting

**Problem: Deployment validation fails**  
**Solution**: Check the capacity resource ID is correct and you have permissions

**Problem: Cannot create App Registration**  
**Solution**: Requires Azure AD Application Administrator role or higher

**Problem: Role assignment fails**  
**Solution**: Requires Owner or User Access Administrator on the capacity resource

**Problem: Deployment already exists**  
**Solution**: Use a different deployment name:

```bash
az deployment subscription create \
  --name setup-customer-v2 \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters ...
```

## How to Revoke Access

### Delete the entire deployment:

```bash
# Get the Service Principal ID
SP_ID=$(az ad sp list --display-name "FabricCapacityMonitor-ReadOnly" --query "[0].id" -o tsv)

# Delete role assignment
az role assignment delete \
  --assignee $SP_ID \
  --scope /subscriptions/.../Microsoft.Fabric/capacities/...

# Delete App Registration
az ad app delete --id <application-id>
```

### Or re-deploy with updated parameters:

Update the Bicep template or parameters and redeploy to modify the configuration.

## Change History

Maintain a change log for your deployments:

```bash
# List all subscription deployments
az deployment subscription list \
  --query "[?contains(name, 'setup-customer')].{Name:name, State:properties.provisioningState, Timestamp:properties.timestamp}" \
  -o table
```

## Template Source Code

For transparency, the Bicep template is open source and available at:
https://github.com/yaribouwman/fabriccapacitymonitor/blob/main/onboarding/setup-customer.bicep

You can review the full source code before deploying.

## Next Steps

After sending the credentials:
- Your consultant will add you to their monitoring system
- Within 15 minutes, data collection will begin
- You'll receive confirmation when everything is working
- You may receive an optional "Ingest Key" for detailed CU metrics

## Related Documentation

- [Portal Setup](portal.md) - Azure Portal walkthrough
- [CLI Script Setup](script.md) - Bash script automation
- [Customer Guide](customer-guide.md) - Overview of all options
