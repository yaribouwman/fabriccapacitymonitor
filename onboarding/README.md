# Customer Onboarding Resources

This folder contains customer-facing onboarding guides and setup automation tools.

## Customer Guides

Professional guides for customers explaining the setup process, security model, and setup options.

### English
- **[Customer Guide](en/customer-guide.md)** - Overview and introduction
- **[Portal Setup](en/portal.md)** - Azure Portal walkthrough (no CLI)
- **[CLI Script Setup](en/script.md)** - Bash script automation
- **[IaC Setup](en/iac.md)** - Bicep Infrastructure-as-Code

### Dutch (Nederlands)
- **[Klant Handleiding](nl/customer-guide.md)** - Overzicht en introductie
- **[Portal Setup](nl/portal.md)** - Azure Portal walkthrough (geen CLI)
- **[CLI Script Setup](nl/script.md)** - Bash script automatisering
- **[IaC Setup](nl/iac.md)** - Bicep Infrastructure-as-Code

## Setup Automation

**CLI Script**: `setup-customer.sh`  
Bash script for creating the Service Principal and granting Reader access. Customers can review and run this script.

**Bicep Template**: `setup-customer.bicep`  
Infrastructure-as-Code template for enterprise customers requiring change management and audit trails.

**Bicep Config**: `bicepconfig.json`  
Configuration file for Bicep linter rules.

## Fabric Notebook

**CU Metrics Notebook**: `extract-metrics-notebook.py`  
Python notebook template for customers to deploy in their Fabric workspace. Queries the Capacity Metrics semantic model and pushes CU utilization data to the monitoring API.

## Internal Documentation

For consultant-facing onboarding instructions, see `docs/onboarding.md` in the repository root.
