# CLI Script Setup

**Recommended for**: Organizations wanting repeatable, auditable setup

**Time**: 5 minutes  
**Requirements**: Azure CLI installed, bash shell

Auditable bash script for repeatable setup with security review.

## Prerequisites

- Azure CLI installed (`az --version` to check)
- Bash shell (Linux, macOS, WSL, or Git Bash on Windows)
- Azure Administrator or Owner role on your Fabric capacity

## Step 1: Download the Script

Download the `setup-customer.sh` script from your consultant or from the GitHub repository.

## Step 2: Review the Script

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

## Step 3: Sign In to Azure

```bash
az login
```

## Step 4: Run the Script

```bash
bash setup-customer.sh
```

The script will prompt you for:
- **Subscription ID**: Your Azure subscription ID
- **Capacity Resource ID**: Full resource ID of your Fabric capacity (or leave empty to scan entire subscription)

## Step 5: Save the Output

The script outputs:
- Tenant ID
- Client ID
- Client Secret
- Subscription ID
- Resource ID (if provided)

**Copy these values and send them to your consultant via secure channel.**

Example output:

```
Setup completed successfully!

Please send these credentials to your consultant:

Organization: YourCompany
Tenant ID: 12345678-1234-1234-1234-123456789012
Client ID: 87654321-4321-4321-4321-210987654321
Client Secret: abc123~defGHI456...
Subscription ID: aaaabbbb-cccc-dddd-eeee-ffffffffffff
Resource Group: rg-fabric-prod
Capacity Name: fabriccap01

The Service Principal 'FabricCapacityMonitor-ReadOnly' has been granted
'Reader' role on your Fabric capacity.
```

## Step 6: Send Credentials to Your Consultant

Send the output to your consultant via secure email or your organization's secure file sharing method.

## Verifying the Setup

Check the App Registration was created:

```bash
az ad app list --display-name "FabricCapacityMonitor-ReadOnly"
```

Check the role assignment:

```bash
az role assignment list \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RG/providers/Microsoft.Fabric/capacities/YOUR_CAPACITY \
  --role "Reader"
```

## Troubleshooting

**Problem: Azure CLI not found**  
**Solution**: Install Azure CLI from https://docs.microsoft.com/cli/azure/install-azure-cli

**Problem: Not logged in**  
**Solution**: Run `az login` and follow the prompts

**Problem: Permission denied when creating App Registration**  
**Solution**: You need Azure AD permissions. Contact your Global Administrator.

**Problem: Cannot grant Reader role**  
**Solution**: You need "Owner" or "User Access Administrator" role on the Fabric capacity resource.

**Problem: Capacity resource not found**  
**Solution**: Verify the subscription ID and capacity name are correct. You can list capacities with:

```bash
az resource list --resource-type "Microsoft.Fabric/capacities"
```

## How to Revoke Access

Remove the role assignment:

```bash
az role assignment delete \
  --assignee <service-principal-id> \
  --scope <capacity-resource-id>
```

Or delete the App Registration entirely:

```bash
az ad app delete --id <application-id>
```

## Script Source Code

For transparency, the script is open source and available at:
https://github.com/yaribouwman/fabriccapacitymonitor/blob/main/onboarding/setup-customer.sh

You can review the full source code before running it.

## Next Steps

After sending the credentials:
- Your consultant will add you to their monitoring system
- Within 15 minutes, data collection will begin
- You'll receive confirmation when everything is working
- You may receive an optional "Ingest Key" for detailed CU metrics
