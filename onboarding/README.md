# Customer Onboarding Guide

This guide helps you grant read-only access to your Microsoft Fabric capacity metadata so your consulting partner can monitor capacity health.

## What This Does

Your organization will create a Service Principal (an application identity) in your Azure Active Directory tenant. This Service Principal will have read-only access to your Fabric capacity resource metadata via the Azure Resource Manager (ARM) API.

## Permissions Granted

The Service Principal will have access to:

- **Capacity State**: Active, Paused, Suspended status
- **Capacity SKU**: F2, F4, F64 tier information
- **Capacity Region**: Azure region where the capacity is deployed
- **Resource Metadata**: Resource tags, resource group, subscription ID

The Service Principal will NOT have access to:

- Actual data in your lakehouses, warehouses, or semantic models
- Fabric artifacts (notebooks, reports, dashboards)
- Workspace metadata or item inventory
- Azure resource management (cannot create/delete/modify resources)
- Microsoft Graph data (users, groups, emails, calendar, etc.)
- Write permissions to any resources

## Two-Tier Data Collection

This monitoring solution uses a hybrid data collection model:

1. **Tier 1 - Automatic Pull (ARM API)**: The monitoring app automatically pulls capacity state, SKU, and region from Azure using the Service Principal. This requires only Azure `Reader` role on the capacity resource.

2. **Tier 3 - Customer Push (Fabric Notebook)**: For detailed CU utilization metrics, you deploy a Fabric notebook in your tenant that queries the Capacity Metrics semantic model and pushes data to the monitoring API. This requires `Capacity Admin` role in Fabric.

Tier 1 is required. Tier 3 is optional but highly recommended for utilization insights.

## Security Posture

This setup follows Microsoft's recommended least-privilege pattern:

- **Single-tenant app**: The Service Principal exists only in your tenant, not shared across organizations
- **Minimal Azure RBAC**: Only `Reader` role on the specific capacity resource
- **Read-only**: The Service Principal cannot modify any Azure resources
- **No broad permissions**: No tenant-wide access, no Graph permissions, no Fabric Admin API access
- **Auditable**: All API calls by the Service Principal are logged in Azure Activity Log
- **Revocable**: Remove the role assignment to revoke access immediately

## Onboarding Options

### Tier 1 Setup (Required)

Choose the option that fits your organization's security and compliance requirements:

#### Option A: Quick Portal Setup

**Best for**: Small organizations, fast setup, minimal tooling requirements

Follow the step-by-step portal guide in [docs/howto.md](../docs/howto.md#tier-1-azure-reader-automatic-pull). Takes about 5 minutes.

#### Option B: CLI Script

**Best for**: Medium organizations, repeatable setup, security review

Review and run `setup-customer.sh`. The script creates the App Registration and grants the Reader role.

```bash
az login
bash setup-customer.sh
```

#### Option C: Bicep IaC

**Best for**: Enterprise organizations, change management, audit trails

Review `setup-customer.bicep` and deploy via your standard IaC process.

All three options create identical resources with identical permissions.

### Tier 3 Setup (Optional but Recommended)

For CU utilization metrics, deploy the Fabric notebook template:

1. Copy `extract-metrics-notebook.py` into a Fabric notebook in your tenant
2. Configure the notebook with your monitoring API URL and ingest key (provided by your partner)
3. Schedule the notebook to run every 15 minutes

See [docs/howto.md](../docs/howto.md#tier-3-cu-metrics-notebook-push) for detailed instructions.

## What to Send Your Partner

After Tier 1 setup, send these values to your consulting partner (via a secure channel):

- **Tenant ID**: Your Azure AD tenant ID
- **Client ID**: The Application ID of the Service Principal
- **Client Secret**: The secret value (treat like a password)
- **Subscription ID**: The Azure subscription containing your Fabric capacity
- **Capacity Resource ID** (optional): The full ARM resource ID of your capacity, or leave blank to scan the entire subscription

Your partner will add your organization to the monitoring app and provide an **Ingest Key** for Tier 3 (if you choose to enable it).

## Monitoring and Audit

To audit API access by the Service Principal:

1. Go to **Azure Portal** > **Monitor** > **Activity Log**
2. Filter by **Service**: `Microsoft.Fabric/capacities`
3. Filter by **Caller**: `FabricCapacityMonitor-ReadOnly`
4. Review read operations on your capacity resources

To see what role assignments exist:

```bash
az role assignment list --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Fabric/capacities/<capacity-name>
```

## Revoking Access

To immediately revoke Tier 1 access:

```bash
az role assignment delete --assignee <service-principal-id> --scope <capacity-resource-id>
```

To revoke Tier 3 access, simply stop the scheduled Fabric notebook.

To permanently delete the Service Principal:

```bash
az ad app delete --id <application-id>
```

## Support

If you have questions about this setup:

1. Review the full documentation in [docs/architecture.md](../docs/architecture.md)
2. Check the decision records in [docs/decisions.md](../docs/decisions.md)
3. Contact your consulting partner for assistance

## Compliance Notes

- The Service Principal does not access personal data or GDPR-protected information
- All data access is read-only and logged
- The monitoring solution does not store raw Fabric artifacts, only aggregated metrics
- Access can be revoked at any time without affecting your Fabric resources
