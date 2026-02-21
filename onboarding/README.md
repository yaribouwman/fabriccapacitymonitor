# Customer Onboarding Resources

This folder contains customer-facing onboarding guides and setup automation tools.

## Customer Guides

**English**: `en/customer-guide.md`  
**Dutch**: `nl/customer-guide.md`

Professional guides for customers explaining the setup process, security model, and three onboarding options (Portal, CLI Script, Bicep IaC).

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
