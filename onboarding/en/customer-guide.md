# Fabric Capacity Monitor - Customer Onboarding Guide

**From**: [Your Consulting Company Name]  
**For**: [Customer Organization Name]  
**Purpose**: Enable read-only monitoring of your Microsoft Fabric capacity

---

## Executive Summary

We'd like to monitor your Microsoft Fabric capacity to provide proactive health monitoring and capacity planning insights. This requires a one-time setup (5-10 minutes) where you grant us read-only access to your capacity metadata.

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

### Portal Setup (Recommended for Most)

**For**: Small organizations, fast setup

Quick Azure Portal walkthrough. No command line tools needed.  
→ [Portal Setup Guide](portal.md)

### CLI Script Setup

**For**: Organizations wanting repeatable, auditable setup

Bash script that automates the setup process.  
→ [CLI Script Guide](script.md)

### Infrastructure as Code (Bicep)

**For**: Enterprises with change management requirements

Deploy using Bicep template for full audit trail.  
→ [IaC Setup Guide](iac.md)

---

## Quick Comparison

| Feature | Portal | CLI Script | Bicep IaC |
|---------|--------|------------|-----------|
| Setup Time | 5 min | 5 min | 10 min |
| Command Line Required | No | Yes | Yes |
| Audit Trail | Manual | Script logs | Full IaC |
| Change Management | No | Optional | Yes |
| Best For | Quick setup | Repeatable | Enterprise |

---

## What Happens Next

After you complete the setup:

1. **Send credentials** to your consultant via secure email
2. **Wait 15 minutes** - Your consultant adds you to their monitoring system
3. **Receive confirmation** - Data collection begins automatically
4. **Optional**: You may receive an "Ingest Key" for detailed CU metrics

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

This is **optional** - the basic monitoring works without it.

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
A: We store: capacity state (Active/Paused), SKU tier (F2/F4/F64), Azure region, and timestamps. If you enable optional CU metrics, we also store utilization percentages and overload events.

**Q: Where is the data stored?**  
A: In your consultant's Azure subscription, in a PostgreSQL database with private networking and encryption at rest.

**Q: Can other customers see our data?**  
A: No. Data is isolated per customer with database-level segregation. Your consultant cannot and does not share customer data.

---

## Contact Your Consultant

If you have questions or need assistance:

- **Email**: [your.email@company.com]
- **Phone**: [your phone number]
- **Support Portal**: [your support URL]

We typically respond within 4 business hours.

---

**Thank you for trusting us with your Fabric capacity monitoring!**

Once you've completed the setup, please send us the credentials. We'll confirm everything is working within 1 business day.
