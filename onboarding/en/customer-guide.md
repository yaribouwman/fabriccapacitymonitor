# Fabric Capacity Monitor - Customer Onboarding Guide

**From**: [Your Consulting Company Name]  
**For**: [Customer Organization Name]  
**Purpose**: Enable read-only monitoring of your Microsoft Fabric capacity

---

## Executive Summary

We'd like to monitor your Microsoft Fabric capacity to provide proactive health monitoring and capacity planning insights. This requires a one-time setup (10 minutes) where you grant us read-only access to your capacity metadata.

**What we'll see:**
- Capacity state (Active, Paused, Suspended)
- Capacity SKU tier and region
- Basic resource information

**What we will NOT see:**
- Your data (lakehouses, warehouses, semantic models)
- Fabric artifacts (reports, dashboards, notebooks)
- User information or workspace contents
- Ability to modify any resources

**Security model:**
- Read-only Azure "Reader" role (no write permissions)
- Scoped to your specific Fabric capacity resource only
- Auditable in your Azure Activity Log
- You can revoke access anytime instantly

---

## Why This Is Safe

This setup follows Microsoft's recommended security practices:

1. **Least Privilege**: Only "Reader" role on your capacity resource (not subscription-wide)
2. **Single Tenant**: The Service Principal exists only in your tenant (not shared across customers)
3. **Read-Only**: Cannot create, modify, or delete any Azure resources
4. **No Data Access**: Cannot query your actual data or Fabric artifacts
5. **Transparent**: All API calls are logged in your Azure Activity Log
6. **Revocable**: Remove the role assignment to instantly revoke access

This is the same pattern used by Azure Managed Service Providers (MSPs) and is approved by Azure security best practices.

---

## Setup Options

Choose the option that best fits your organization's processes and security requirements. All three options create identical Service Principals with identical permissions.

### Option A: Quick Portal Setup

**Best for**: Small organizations, fast setup, minimal tooling requirements  
**Time required**: 5 minutes  
**Requirements**: Access to [portal.azure.com](https://portal.azure.com)

[Jump to Portal Setup Instructions](#option-a-portal-setup-instructions)

### Option B: CLI Script

**Best for**: Medium organizations, repeatable setup, security review  
**Time required**: 5 minutes  
**Requirements**: Azure CLI installed, bash shell

[Jump to CLI Script Instructions](#option-b-cli-script-instructions)

### Option C: Infrastructure as Code (Bicep)

**Best for**: Enterprise organizations, change management, audit trails  
**Time required**: 10 minutes  
**Requirements**: Azure CLI, familiarity with Bicep/ARM deployments

[Jump to Bicep IaC Instructions](#option-c-bicep-iac-instructions)

---

## Option A: Portal Setup Instructions

### Step 1: Sign In to Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your work account
3. Verify you're in the correct directory/tenant

### Step 2: Create Service Principal

1. Search for **"App registrations"** in the top search bar
2. Click **"+ New registration"**
3. Fill in:
   - **Name**: `FabricCapacityMonitor-ReadOnly`
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Leave empty
4. Click **"Register"**

**What you'll see**: An overview page with two important IDs

5. **Copy these values** (you'll need them later):
   - **Application (client) ID**: (looks like: 12345678-1234-1234-1234-123456789abc)
   - **Directory (tenant) ID**: (looks like: 87654321-4321-4321-4321-210987654321)

### Step 3: Create Client Secret

1. In the left menu, click **"Certificates & secrets"**
2. Click **"+ New client secret"**
3. Description: `Fabric Monitor Access`
4. Expiration: **24 months** (or your org policy)
5. Click **"Add"**
6. **IMMEDIATELY copy the Value** - you'll never see it again!
   - Looks like: `abc123~defGHI456...`

### Step 4: Grant Access to Fabric Capacity

1. Search for **"Fabric capacities"** in Azure Portal
2. Click on your capacity (e.g., "MyFabricCapacity")
3. Click **"Access control (IAM)"** in left menu
4. Click **"+ Add"** → **"Add role assignment"**
5. Select **"Reader"** role → Click **"Next"**
6. Click **"+ Select members"**
7. Search for: `FabricCapacityMonitor-ReadOnly`
8. Select it → Click **"Select"**
9. Click **"Review + assign"** (twice)

**Verification**: You should see "FabricCapacityMonitor-ReadOnly" with "Reader" role in the list.

### Step 5: Get Resource Information

On your Fabric capacity overview page, note:
- **Subscription ID**: (visible in the overview)
- **Resource Group**: (visible in the overview)
- **Capacity Name**: (the name you clicked on)

### Step 6: Send Credentials to Your Consultant

Please send the following information via secure email:

```
Subject: Fabric Capacity Monitor Setup - [Your Company Name]

Hello [Consultant Name],

I've completed the Fabric Capacity Monitor setup. Here are the credentials:

Organization Name: [Your Company Name]
Tenant ID: [From Step 2]
Client ID: [From Step 2]
Client Secret: [From Step 3]
Subscription ID: [From Step 5]
Resource Group: [From Step 5]
Capacity Name: [From Step 5]

The Service Principal has been granted "Reader" role on our Fabric capacity.

Best regards,
[Your Name]
[Your Title]
[Contact Information]
```

**Security tip**: Send via encrypted email or your organization's secure file sharing method.

---

## Option B: CLI Script Instructions

### Prerequisites

- Azure CLI installed (`az --version`)
- Bash shell (Linux, macOS, WSL, or Git Bash on Windows)
- Azure Administrator or Owner role on your Fabric capacity

### Step 1: Download the Script

Download the `setup-customer.sh` script from your consultant or from the GitHub repository.

### Step 2: Review the Script

Before running any script, review its contents:

```bash
cat setup-customer.sh
```

The script performs these actions:
1. Checks Azure CLI is installed and you're logged in
2. Creates an App Registration in your tenant
3. Creates a client secret
4. Grants Reader role on your Fabric capacity
5. Outputs the credentials to share with your consultant

### Step 3: Sign In to Azure

```bash
az login
```

### Step 4: Run the Script

```bash
bash setup-customer.sh
```

The script will prompt you for:
- **Subscription ID**: Your Azure subscription ID
- **Capacity Resource ID**: Full resource ID of your Fabric capacity (or leave empty to scan entire subscription)

### Step 5: Save the Output

The script outputs:
- Tenant ID
- Client ID
- Client Secret
- Subscription ID
- Resource ID (if provided)

**Copy these values and send them to your consultant via secure channel.**

---

## Option C: Bicep IaC Instructions

### Prerequisites

- Azure CLI installed
- Familiarity with Azure Bicep/ARM templates
- Your organization's change management process

### Step 1: Download the Bicep Template

Download these files from your consultant or GitHub repository:
- `setup-customer.bicep`
- `bicepconfig.json` (optional)

### Step 2: Review the Template

Review the Bicep template to understand the resources being created:

```bash
cat setup-customer.bicep
```

The template creates:
1. Azure AD App Registration
2. Service Principal
3. Role assignment (Reader) on the Fabric capacity

### Step 3: Submit for Change Management

If your organization requires change management for infrastructure changes, submit the Bicep template through your standard approval process.

### Step 4: Deploy the Template

```bash
az login

az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

### Step 5: Get Deployment Outputs

The deployment outputs:
- Tenant ID
- Client ID
- Service Principal ID

### Step 6: Create Client Secret Manually

Bicep cannot output secrets for security reasons. Create the client secret manually:

1. Go to Azure Portal → **Entra ID** → **App registrations**
2. Find `FabricCapacityMonitor-ReadOnly`
3. Go to **Certificates & secrets** → **New client secret**
4. Copy the secret value

### Step 7: Send Credentials to Your Consultant

Send the Tenant ID, Client ID, Client Secret, and Subscription ID to your consultant via secure channel.

---

## What Happens Next

1. Your consultant will add your organization to their monitoring system
2. Within 15 minutes, they'll confirm data collection is working
3. They may provide an optional "Ingest Key" for detailed CU metrics (requires deploying a Fabric notebook)
4. They'll set up monitoring dashboards and alerts for your capacity

---

## Optional: Detailed CU Metrics

For deeper insights into Capacity Unit (CU) utilization, you can optionally deploy a Fabric notebook that pushes CU metrics to the monitoring system.

**Benefits:**
- See CU utilization percentages over time
- Track overloaded minutes and throttling events
- Store metrics beyond the built-in 14-day retention
- Compare utilization across multiple capacities

**Setup:**
1. Your consultant will provide a Python notebook template
2. You deploy it in your Fabric workspace
3. Schedule it to run every 15 minutes
4. Uses an "Ingest Key" (provided by consultant) for authentication

**Requirements:**
- Capacity Admin role in your Fabric tenant
- 5 minutes to deploy the notebook

This is **optional** - the basic monitoring (Tier 1) works without it.

---

## How to Verify It's Working

After 15 minutes:

1. Go to Azure Portal → Your Fabric Capacity → **"Activity log"**
2. Filter by "Operation name" → "List Fabric Capacities"
3. You should see API calls from "FabricCapacityMonitor-ReadOnly"

You can also ask your consultant to confirm - they'll see your capacity state and SKU in their dashboard.

---

## How to Revoke Access

If you need to remove access at any time:

1. Go to Azure Portal → Your Fabric Capacity
2. Click **"Access control (IAM)"**
3. Find **"FabricCapacityMonitor-ReadOnly"**
4. Click **"..."** → **"Remove"**
5. Confirm removal

**Access is revoked immediately** - data collection will stop within 15 minutes.

---

## Frequently Asked Questions

**Q: Will this affect our Fabric performance?**  
A: No. Monitoring uses lightweight Azure API calls (once every 15 minutes). No impact on CU consumption or query performance.

**Q: Can you see our data?**  
A: No. We only see capacity metadata (state, SKU, region). We cannot access your lakehouses, warehouses, reports, or any actual data.

**Q: How do we know what you're accessing?**  
A: Check your Azure Activity Log - all API calls are logged with timestamps and the Service Principal name.

**Q: What if the Client Secret expires?**  
A: We'll notify you if we detect collection failures. You'll need to generate a new secret and send it to us.

**Q: Is this compliant with our security policies?**  
A: This uses standard Azure RBAC with least-privilege access. It's the same pattern used by Microsoft partners and MSPs. Check with your security team if you have specific compliance requirements.

**Q: What data do you store?**  
A: We store: capacity state (Active/Paused), SKU tier (F2/F4/F64), Azure region, and timestamps. If you enable Tier 3, we also store CU utilization percentages and overload events.

**Q: Where is the data stored?**  
A: In your consultant's Azure subscription, in a PostgreSQL database with private networking and encryption at rest.

**Q: Can other customers see our data?**  
A: No. Data is isolated per customer with database-level segregation. Your consultant cannot and does not share customer data.

---

## Troubleshooting

**Problem: Can't find "App registrations"**  
**Solution**: You may need Azure AD permissions. Contact your Global Administrator or Azure AD administrator.

**Problem: "Access control (IAM)" button is greyed out**  
**Solution**: You need "Owner" or "User Access Administrator" role on the Fabric capacity resource.

**Problem: Can't see the Client Secret value**  
**Solution**: It's only shown once. Create a new secret if you missed it.

**Problem: Don't know which Fabric capacity to select**  
**Solution**: Ask your Fabric Administrator or check the Fabric Admin Portal for capacity names.

---

## Contact Your Consultant

If you have questions or need assistance:

- **Email**: [your.email@company.com]
- **Phone**: [your phone number]
- **Support Portal**: [your support URL]

We typically respond within 4 business hours.

---

## Document Information

**Version**: 1.0  
**Last Updated**: February 2026  
**Prepared by**: [Your Consulting Company Name]  
**Valid for**: Microsoft Fabric Standard/Premium Capacities

---

**Thank you for trusting us with your Fabric capacity monitoring!**

Once you've completed the setup, please send us the credentials using the template above. We'll confirm everything is working within 1 business day.
