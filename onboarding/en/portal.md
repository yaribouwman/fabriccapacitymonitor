# Portal Setup (Azure Portal)

**Recommended for**: Small organizations, fast setup

**Time**: 5 minutes  
**Requirements**: Access to Azure Portal

Quick Azure Portal walkthrough - no command line tools needed.

## Step 1: Sign In to Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your work account
3. Verify you're in the correct directory/tenant

## Step 2: Create Service Principal

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

## Step 3: Create Client Secret

1. In the left menu, click **"Certificates & secrets"**
2. Click **"+ New client secret"**
3. Description: `Fabric Monitor Access`
4. Expiration: **24 months** (or your org policy)
5. Click **"Add"**
6. **IMMEDIATELY copy the Value** - you'll never see it again!
   - Looks like: `abc123~defGHI456...`

## Step 4: Grant Access to Fabric Capacity

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

## Step 5: Get Resource Information

On your Fabric capacity overview page, note:
- **Subscription ID**: (visible in the overview)
- **Resource Group**: (visible in the overview)
- **Capacity Name**: (the name you clicked on)

## Step 6: Send Credentials to Your Consultant

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

## Troubleshooting

**Problem: Can't find "App registrations"**  
**Solution**: You may need Azure AD permissions. Contact your Global Administrator or Azure AD administrator.

**Problem: "Access control (IAM)" button is greyed out**  
**Solution**: You need "Owner" or "User Access Administrator" role on the Fabric capacity resource.

**Problem: Can't see the Client Secret value**  
**Solution**: It's only shown once. Create a new secret if you missed it.

**Problem: Don't know which Fabric capacity to select**  
**Solution**: Ask your Fabric Administrator or check the Fabric Admin Portal for capacity names.

## Next Steps

After sending the credentials:
- Your consultant will add you to their monitoring system
- Within 15 minutes, data collection will begin
- You'll receive confirmation when everything is working
- You may receive an optional "Ingest Key" for detailed CU metrics

## How to Verify It's Working

After 15 minutes:

1. Go to Azure Portal → Your Fabric Capacity → **"Activity log"**
2. Filter by "Operation name" → "List Fabric Capacities"
3. You should see API calls from "FabricCapacityMonitor-ReadOnly"

## How to Revoke Access

If you need to remove access at any time:

1. Go to Azure Portal → Your Fabric Capacity
2. Click **"Access control (IAM)"**
3. Find **"FabricCapacityMonitor-ReadOnly"**
4. Click **"..."** → **"Remove"**
5. Confirm removal

**Access is revoked immediately** - data collection will stop within 15 minutes.
