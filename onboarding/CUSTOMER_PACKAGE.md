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

## Setup Instructions

### Prerequisites

- Access to [portal.azure.com](https://portal.azure.com)
- Azure Administrator or Owner role on your Fabric capacity resource
- 10 minutes of time

### Step 1: Sign In to Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your work account
3. Verify you're in the correct directory/tenant

---

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

---

### Step 3: Create Client Secret

1. In the left menu, click **"Certificates & secrets"**
2. Click **"+ New client secret"**
3. Description: `Fabric Monitor Access`
4. Expiration: **24 months** (or your org policy)
5. Click **"Add"**
6. **IMMEDIATELY copy the Value** - you'll never see it again!
   - Looks like: `abc123~defGHI456...`

---

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

---

### Step 5: Get Resource Information

On your Fabric capacity overview page, note:
- **Subscription ID**: (visible in the overview)
- **Resource Group**: (visible in the overview)
- **Capacity Name**: (the name you clicked on)

---

### Step 6: Send Credentials to Us

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

## What Happens Next

1. We'll add your organization to our monitoring system
2. Within 15 minutes, we'll confirm data collection is working
3. We may provide an optional "Ingest Key" for detailed CU metrics (requires deploying a Fabric notebook)
4. We'll set up monitoring dashboards and alerts for your capacity

---

## Optional: Detailed CU Metrics (Tier 3)

For deeper insights into Capacity Unit (CU) utilization, you can optionally deploy a Fabric notebook that pushes CU metrics to our monitoring system.

**Benefits:**
- See CU utilization percentages over time
- Track overloaded minutes and throttling events
- Store metrics beyond the built-in 14-day retention
- Compare utilization across multiple capacities

**Setup:**
1. We'll provide a Python notebook template
2. You deploy it in your Fabric workspace
3. Schedule it to run every 15 minutes
4. Uses an "Ingest Key" (we'll provide) for authentication

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

You can also ask us to confirm - we'll see your capacity state and SKU in our dashboard.

---

## How to Revoke Access

If you need to remove our access at any time:

1. Go to Azure Portal → Your Fabric Capacity
2. Click **"Access control (IAM)"**
3. Find **"FabricCapacityMonitor-ReadOnly"**
4. Click **"..."** → **"Remove"**
5. Confirm removal

**Access is revoked immediately** - we'll stop receiving data within 15 minutes.

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
A: In our Azure subscription, in a PostgreSQL database with private networking and encryption at rest.

**Q: Can other customers see our data?**  
A: No. Data is isolated per customer with database-level segregation. We cannot and do not share customer data.

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

## Contact Us

If you have questions or need assistance:

- **Email**: [your.email@company.com]
- **Phone**: [your phone number]
- **Support Portal**: [your support URL]

We typically respond within 4 business hours.

---

## Detailed Technical Documentation

For technical staff who want deeper details:

- **Full Architecture**: [Link to architecture.md in your repo]
- **Security Model**: [Link to security docs]
- **API Permissions Reference**: [Link to Microsoft docs on Fabric RBAC]

---

## Document Information

**Version**: 1.0  
**Last Updated**: February 2026  
**Prepared by**: [Your Consulting Company Name]  
**Valid for**: Microsoft Fabric Standard/Premium Capacities

---

**Thank you for trusting us with your Fabric capacity monitoring!**

Once you've completed the setup, please send us the credentials using the template in Step 6. We'll confirm everything is working within 1 business day.
