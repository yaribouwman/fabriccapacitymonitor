# Changelog

All notable changes to Fabric Capacity Monitor will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-21

### Fixed
- Fixed `Deployment Progress Deadline Exceeded. 0/1 replicas ready` error: Added generous explicit Health Probes (Startup, Liveness, Readiness) to the Container App configuration to give the PostgreSQL database enough time to finish provisioning before Azure marks the initial deployment as failed.
- Key Vault `enablePurgeProtection` error during Starter tier deployment: The property is now omitted instead of explicitly being set to `false`, avoiding terminal provisioning failures when a soft-deleted vault exists.
- Key Vault deployment failure: Application secrets (`db-connection-string`, `admin-api-key`) are now injected directly into the Container App instead of being created in the Key Vault via ARM. This avoids permission errors when deploying via the Azure Portal since the deploying user no longer needs Key Vault Data Plane roles.
- `alertEmails` parameter now accepts a comma-separated string instead of an array, fixing the Azure portal deployment error
- Storage account, registry, key vault, and container app names now strip hyphens and truncate to meet Azure naming constraints
- Corrected repository name references in Deploy to Azure button and GitHub Actions workflows
- GitHub Actions workflows now skip Azure deployment when credentials are not configured

## [0.1.0] - 2026-02-17

### Added

**Infrastructure**
- Azure Bicep templates for complete infrastructure deployment
- Deploy to Azure button for one-click setup
- Two-tier deployment model (Starter ~$20/month, Enterprise ~$270/month)
- Container Apps for serverless Python/FastAPI backend
- PostgreSQL Flexible Server with VNET integration
- Azure Key Vault for secrets management
- User Assigned Managed Identity for credential-free access
- Private networking with NSGs and subnet delegation
- Storage Account for distributed locking
- Azure Monitor alerts for security and performance events

**Backend Application**
- FastAPI backend with async SQLAlchemy ORM
- Multi-tenant data model with customer isolation
- Cross-tenant authentication via Service Principal credentials
- Automatic capacity metadata collection every 15 minutes
- Parallel customer processing (10 concurrent by default)
- Customer health tracking (healthy/degraded/critical status)
- Authentication error detection and alerting
- Admin API for customer management
- Ingest API for customer-pushed CU metrics
- Structured logging with request context

**Customer Onboarding**
- Azure Portal step-by-step guide for non-technical users
- Complete customer package documentation
- Bash automation script for technical setup
- Bicep IaC template for enterprise deployments
- Custom "Fabric Capacity Reader" RBAC role with minimal permissions

**Documentation**
- Complete architecture documentation with component diagrams
- Security model and threat analysis
- Architecture Decision Records (ADRs)
- PowerShell deployment verification guide
- Multiple onboarding paths for different user types

**Security**
- Managed Identity authentication (no stored credentials)
- Customer secrets stored in Key Vault with RBAC
- Database in private subnet with NSG restrictions
- Customer data isolation via foreign keys
- Least-privilege Service Principal model
- Instant access revocation capability
- Audit trail in Azure Activity Log
- Soft delete and purge protection (Enterprise tier)