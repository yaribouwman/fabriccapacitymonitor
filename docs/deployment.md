# Deployment Options

Choose the deployment method that best fits your organization.

## Portal Deployment (Recommended for Most Users)

**For**: Smaller organizations, non-technical users, quick setup

Click the Deploy to Azure button and fill in a simple form. No command line tools or coding required. Everything happens automatically.

[Get Started with Portal Deployment →](deployment/portal.md)

## CLI Script Deployment

**For**: IT teams, developers, automation scenarios

Use a bash script to deploy via command line. Ideal for automation and when you're comfortable with Azure CLI.

[Get Started with CLI Deployment →](deployment/cli.md)

## Enterprise Deployment with CI/CD

**For**: Large organizations with existing DevOps processes

Deploy using Infrastructure-as-Code with Bicep templates. Includes GitHub Actions and Azure DevOps pipeline configurations.

[Get Started with Enterprise Deployment →](deployment/enterprise.md)

## Quick Comparison

| Feature | Portal | CLI | Enterprise |
|---------|--------|-----|------------|
| Setup Time | 15 min | 10 min | 30 min |
| Command Line Required | No | Yes | Yes |
| Automation Ready | No | Yes | Yes |
| CI/CD Integration | No | Partial | Full |
| Infrastructure as Code | No | No | Yes |
| Best For | Getting started | Dev teams | Large orgs |

## What Gets Deployed

All deployment methods create the same infrastructure:

- **Container App**: Hosts the backend API (Python/FastAPI)
- **PostgreSQL Database**: Stores capacity metrics and time-series data
- **Key Vault**: Manages database credentials and customer secrets
- **Container Registry**: Hosts application images
- **Virtual Network**: Isolates database from public internet
- **Managed Identity**: Enables passwordless authentication
- **Storage Account**: Supports distributed locking

Two deployment tiers available:
- **Starter**: Cost-optimized with scale-to-zero (~$20/month)
- **Enterprise**: Production-grade with HA and geo-redundancy (~$270/month)

## Need Help?

- First time deploying? Start with [Portal Deployment](deployment/portal.md)
- Need to automate? Use [CLI Deployment](deployment/cli.md)
- Enterprise setup? See [Enterprise Deployment](deployment/enterprise.md)
- After deployment: [Add your first customer](onboarding.md)
