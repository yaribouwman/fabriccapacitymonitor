# Deploy via Azure Portal (No Code)

**Recommended for**: Smaller organizations, non-technical users, quick setup

**Time**: 15 minutes  
**Requirements**: Azure account with Owner or Contributor access

This is the easiest deployment method - no command line tools or coding required. Everything happens automatically.

## Step 1: Start the Deployment

1. Go to the [repository README](../../README.md)
2. Click the **"Deploy to Azure"** button (blue button at the top)
3. Sign in to your Azure account if prompted
4. You'll see the deployment form in Azure Portal

## Step 2: Fill in the Form

Fill in these fields (all others have safe defaults):

- **Subscription**: Choose your Azure subscription from the dropdown
- **Resource Group**: Click "Create new" and enter a name like `rg-fabricmon-prod`
- **Region**: Choose a location close to you (e.g., `East US`, `West Europe`)
- **App Name**: Enter a short name (3-20 characters, letters and numbers only, no spaces or hyphens)
  - Example: `fabricmon` or `capacitymon`
- **Environment Type**: 
  - Choose `Starter` for testing or small deployments (lower cost, scales to zero)
  - Choose `Enterprise` for production (high availability, always-on)
- **Alert Emails**: (Optional) Enter email addresses for monitoring alerts, separated by commas
  - Example: `ops@yourcompany.com,alerts@yourcompany.com`
  - Leave blank if you don't want email alerts

## Step 3: Deploy

1. Click **"Review + create"** at the bottom
2. Review your settings (Azure will validate them)
3. Click **"Create"**
4. Wait 10-15 minutes while Azure creates your resources

You'll see a progress screen showing which resources are being created. Don't close this window.

## Step 4: Get Your App URL

When deployment completes (green checkmark):

1. Stay on the deployment completion screen
2. Click the **Outputs** tab in the left menu (under "Deployment details")
3. Find **appUrl** - this is your monitoring system URL
4. Copy this URL - you'll need it to add customers

Example URL: `https://ca-fabricmon-xyz123.azurecontainerapps.io`

**Everything is now deployed and running!** The deployment automatically:
- Created all infrastructure (database, networking, security)
- Generated secure passwords and stored them safely
- Initialized the database with required tables
- Started the backend application
- Configured all security settings

No manual setup needed - you're ready to add customers.

## Verify Your Deployment

After deployment, verify everything is working using the Azure Portal.

### Check 1: View Your Resources

1. In Azure Portal, go to **Resource groups**
2. Click on your resource group (e.g., `rg-fabricmon-prod`)
3. You should see these resources:
   - **Container App** (starts with `ca-`)
   - **Container Apps Environment** (starts with `cae-`)
   - **PostgreSQL server** (starts with `psql-`)
   - **Key Vault** (starts with `kv-`)
   - **Container Registry** (starts with `acr`)
   - **Storage Account** (starts with `st`)
   - **Virtual Network** (starts with `vnet-`)
   - **Managed Identity** (starts with `id-`)

If all these are present, your infrastructure deployed successfully.

### Check 2: Test the API

1. Open a new browser tab
2. Go to your app URL and add `/health` at the end
   - Example: `https://ca-fabricmon-xyz123.azurecontainerapps.io/health`
3. You should see a response like:
   ```json
   {"status": "ok", "version": "0.1.0"}
   ```

If you see this, your application is running and the database connection works.

### Check 3: View the API Documentation

1. Go to your app URL and add `/docs` at the end
   - Example: `https://ca-fabricmon-xyz123.azurecontainerapps.io/docs`
2. You should see the interactive API documentation (Swagger UI)
3. This shows all available endpoints

### Check 4: View Application Logs (Optional)

If you want to see what the application is doing:

1. In Azure Portal, go to your **Container App** (starts with `ca-`)
2. Click **"Log stream"** in the left menu
3. You'll see live logs from your application
4. Look for messages like:
   - `Application startup complete`
   - `Database migrations completed successfully`
   - `Uvicorn running on http://0.0.0.0:8080`

## Troubleshooting

### Problem: Health check returns an error or timeout

**Solution**: 
1. Go to your Container App in Azure Portal
2. Click **"Revision management"** in the left menu
3. Check if the latest revision shows "Running" status
4. If not, click **"Logs"** to see error messages

### Problem: Can't find the appUrl in deployment outputs

**Solution**:
1. Go to your Resource Group
2. Click **"Deployments"** in the left menu
3. Click on the most recent deployment
4. Click **"Outputs"** tab
5. Copy the **appUrl** value

### Problem: Resources are missing

**Solution**: The deployment may have failed partway through. Check:
1. Resource Group → **"Deployments"** → Click on the deployment name
2. Look for any resources marked with a red X (failed)
3. Click on the failed resource to see the error message

### Problem: Container App not starting

**Solution**:
1. Go to your Container App in Azure Portal
2. Click **"Log stream"** in the left menu
3. Look for error messages in red
4. Common issues:
   - `Database connection failed` - Database is still starting up (wait 2-3 minutes)
   - `Failed to pull image` - Container Registry access issue (re-run deployment)
   - `Health check failed` - Application startup error (check logs for details)

### Problem: Database not available

**Solution**:
1. Go to your Resource Group in Azure Portal
2. Find your PostgreSQL server (starts with `psql-`)
3. Click on it to open
4. Check the **Status** at the top - should say "Available"
5. If status is "Updating" or "Creating", wait 5-10 minutes and check again
6. If status is "Failed", the deployment had an issue - try redeploying

## Next Steps

After successful deployment:

1. [Add your first customer](../onboarding.md) to start collecting capacity metrics
2. [Connect Power BI](../powerbi-setup.md) to visualize capacity data
3. [Review operations guide](../operations.md) for day-to-day maintenance

## Related Documentation

- [CLI Deployment](cli.md) - For automation and scripting
- [Enterprise Deployment](enterprise.md) - For large organizations with CI/CD
- [Operations Guide](../operations.md) - Day-to-day maintenance
- [Architecture](../architecture.md) - System design and components
