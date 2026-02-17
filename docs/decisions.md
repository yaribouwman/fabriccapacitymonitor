# Architecture Decision Records

## ADR-001: Bicep over Terraform

**Status**: Accepted

**Context**: Need to choose an infrastructure-as-code tool for Azure deployments.

**Decision**: Use Azure Bicep for all infrastructure definitions.

**Rationale**: 
- Native Azure tooling with first-class support for new Azure features
- Simpler syntax than ARM JSON, less verbose than Terraform
- No state management complexity (Azure Resource Manager is the state)
- Better type checking and IntelliSense in VS Code
- Target audience is Azure-focused organizations that already use Azure tooling

**Tradeoffs**: 
- Azure-only (not multi-cloud)
- Smaller ecosystem compared to Terraform
- Some advanced features require preview API versions

## ADR-002: User Assigned Managed Identity

**Status**: Accepted

**Context**: Container Apps need to authenticate to Key Vault and Container Registry.

**Decision**: Use User Assigned Managed Identity, not System Assigned.

**Rationale**:
- Can pre-create the identity and assign RBAC roles before the app exists
- Single identity can be shared across multiple resources if needed
- Easier to audit in Azure AD (persistent principal ID)
- Can be created in a separate lifecycle from the app
- Cleaner deletion (identity persists even if app is deleted and recreated)

**Tradeoffs**:
- Slightly more complex deployment (requires explicit identity resource)
- Must manually assign the identity to resources

## ADR-003: Container Apps over AKS

**Status**: Accepted

**Context**: Need a container orchestration platform for the backend API.

**Decision**: Use Azure Container Apps, not Azure Kubernetes Service.

**Rationale**:
- Fully managed (no node management, patching, or control plane maintenance)
- Built-in scaling including scale-to-zero for Starter tier
- Simpler networking model (automatic ingress, no LoadBalancer services)
- Native Key Vault secret integration
- Lower operational overhead for small-to-medium workloads
- Better cost model for variable traffic (pay per vCPU-second)

**Tradeoffs**:
- Less control over underlying infrastructure
- Cannot run privileged containers or custom node configurations
- Smaller ecosystem of tooling compared to Kubernetes
- Not suitable if customer requires Kubernetes for compliance reasons

## ADR-004: PostgreSQL Flexible Server

**Status**: Accepted

**Context**: Need a relational database for capacity metrics and time-series data.

**Decision**: Use Azure Database for PostgreSQL Flexible Server with VNET integration.

**Rationale**:
- Strong relational model fits capacity metrics (entities: workspaces, capacities, events)
- Time-series extensions (timescaledb) available if needed
- VNET integration ensures database is not publicly accessible
- Burstable tier available for Starter environments (cost-effective)
- Automated backups, point-in-time restore, high availability options

**Tradeoffs**:
- More expensive than Cosmos DB for simple document storage
- Requires VNET setup (adds networking complexity)
- Scaling compute requires downtime (brief restart)

## ADR-005: Auto-Generated Passwords

**Status**: Accepted

**Context**: Database administrator password must be set during deployment.

**Decision**: Use Bicep's `newGuid()` function to auto-generate passwords in the Deploy to Azure flow.

**Rationale**:
- Users never see or type the password (reduces social engineering risk)
- Password is immediately stored in Key Vault
- No password appears in deployment outputs or logs
- Simplifies the Deploy to Azure experience (fewer form fields)
- Application retrieves the password from Key Vault at runtime via Managed Identity

**Tradeoffs**:
- Password rotation requires manual steps (cannot use `newGuid()` again without recreating the database)
- Less explicit than asking users to provide their own password
- Need to document how to retrieve the password for emergency access

## ADR-006: Two-Tier Pricing Model

**Status**: Accepted

**Context**: Need to balance cost for small deployments vs. production requirements for enterprises.

**Decision**: Offer Starter and Enterprise tiers controlled by a single `environmentType` parameter.

**Rationale**:
- Starter tier enables free trials, demos, and small production deployments (scale-to-zero saves money)
- Enterprise tier provides production-grade guarantees (HA, geo-redundancy, always-warm)
- Single parameter makes tier selection obvious in the Deploy to Azure form
- Avoids exposing 20+ individual SKU parameters to users

**Tradeoffs**:
- Only two tiers (not a full range of options)
- Users cannot mix-and-match (e.g., Enterprise database + Starter app)
- Future requirement for custom tiers requires refactoring

## ADR-007: Cross-Tenant Service Principal Model

**Status**: Accepted

**Context**: Need to read Fabric capacity metadata from customer tenants. Customers range from small businesses to regulated enterprises. They need control over access and auditability.

**Decision**: Each customer creates their own Service Principal in their own Entra ID tenant. The customer grants Azure `Reader` role on their Fabric capacity resource, then shares the credentials (Tenant ID, Client ID, Client Secret, Subscription ID) with the consulting company.

**Rationale**:
- Customer retains full control over the Service Principal (can revoke access instantly)
- No multi-tenant consent required (avoids customer concerns about third-party app access)
- Single-tenant Service Principal is easier to audit in customer's Azure Activity Log
- Customer can review and approve the exact permissions granted (Azure Reader only)
- Credentials are stored in the consulting company's Key Vault, not in customer code
- Each customer is isolated (compromise of one customer's credentials doesn't affect others)
- **Lower privilege than Fabric Admin API**: Only requires Azure RBAC, no Fabric tenant settings

**Tradeoffs**:
- More setup per customer vs. a multi-tenant consent link
- Consulting company must manage multiple sets of credentials (mitigated by Key Vault)
- Client secrets expire and must be rotated (typically annual)

**Alternative Considered**: Multi-tenant Azure AD app with consent link. Rejected because many enterprise customers are hesitant to consent to third-party apps, and a multi-tenant app provides less isolation and auditability.

## ADR-008: Three-Tier Customer Onboarding

**Status**: Accepted

**Context**: Customers have varying levels of security maturity and tooling. Small organizations (5-10 people) want fast, simple onboarding. Enterprise customers require Infrastructure-as-Code for change management and audit trails.

**Decision**: Offer three onboarding paths for Tier 1 (ARM Reader) that all create identical resources:
1. **Option A (Portal)**: Step-by-step Azure Portal guide
2. **Option B (Script)**: Auditable bash script (`setup-customer.sh`)
3. **Option C (Bicep)**: Infrastructure-as-Code template

**Rationale**:
- Small organizations optimize for speed (Option A takes 5 minutes, no tooling required)
- Medium organizations want repeatability and version control (Option B provides a reviewable script)
- Enterprise customers need declarative IaC for change management (Option C can be stored in their repo, diffed, and approved)
- All three options produce identical Service Principals with identical permissions (same security outcome)
- Customers can choose based on their processes, not security requirements
- **Simpler than before**: No security groups, no Fabric tenant settings, just Azure role assignment

**Tradeoffs**:
- Three paths to maintain and test (mitigated by the fact they create the same resources)
- Documentation is longer (but clearer for the three audiences)

**Alternative Considered**: Only offer the script (Option B). Rejected because small orgs would find it intimidating, and enterprise would demand IaC.

## ADR-009: ARM API over Fabric Admin API for Tier 1

**Status**: Accepted

**Context**: We need capacity metadata (state, SKU, region) from customer tenants. Fabric Admin API offers this data but requires a tenant-level setting that many enterprises reject due to security policy.

**Decision**: Use Azure Resource Manager (ARM) API for Tier 1 capacity metadata collection. This requires only Azure `Reader` role, not Fabric Admin API access.

**Rationale**:
- **Lower privilege barrier**: Azure Reader is a standard, well-understood Azure RBAC role. No Fabric-specific settings required.
- **Higher adoption rate**: Enterprise security teams are more comfortable granting Azure Reader than enabling Fabric Admin API tenant settings.
- **Auditable in Azure Activity Log**: All API calls are logged in Azure Monitor, which is standard for compliance audits.
- **No dependency on Fabric tenant configuration**: Works even if customer has strict Fabric tenant settings.
- **Sufficient for MVP**: ARM API provides capacity state, SKU, region, tags - enough for health monitoring.

**Tradeoffs**:
- ARM API does not provide workspace metadata or item inventory (Tier 2 Fabric Admin API needed for that, optional).
- ARM API does not provide CU utilization metrics (Tier 3 notebook push needed for that).
- Must query Azure ARM API per subscription/resource group rather than a single Fabric-wide endpoint.

**Alternative Considered**: Fabric Admin API as Tier 1. Rejected because it requires a tenant setting that many customers refuse to enable, reducing adoption.

## ADR-010: CU Metrics via Customer-Deployed Notebook (Tier 3 Push)

**Status**: Accepted

**Context**: The most valuable metric for capacity monitoring is CU utilization percentage. This data exists in the Fabric Capacity Metrics semantic model, but there is no public API to retrieve it. Azure Monitor Metrics API does not expose CU utilization for Fabric capacities.

**Decision**: Customers who want CU utilization metrics deploy a Fabric notebook in their tenant. The notebook queries the Capacity Metrics semantic model using Semantic Link Labs and pushes data to our monitoring API via `POST /api/ingest`. Customers authenticate to the ingest endpoint with an API key.

**Rationale**:
- **Only viable path to CU data**: Capacity Metrics semantic model is the authoritative source, but it's only accessible within the customer's Fabric tenant.
- **Customer control**: Customer deploys and schedules the notebook. They can inspect the code, modify the schedule, or disable it at any time.
- **Capacity Admin role is acceptable**: While it's a high privilege, customers grant it to their own user accounts (not a Service Principal from an external company), making it more palatable.
- **Long-term retention**: We store pushed metrics in PostgreSQL for multi-month dashboards and trend analysis, which the 14-day Capacity Metrics app cannot provide.
- **Cross-customer dashboards**: Centralized data enables comparing CU utilization across all customer capacities in one view.

**Tradeoffs**:
- Requires Capacity Admin role in customer's Fabric tenant (higher privilege than Tier 1).
- Customer must deploy and schedule the notebook manually (cannot be automated from external tenant).
- Notebook queries consume CU on the customer's capacity (minimal, <1 CU per run).
- If the notebook fails or is disabled, CU metrics stop flowing (Tier 1 metadata continues).

**Alternative Considered**: 
- **Azure Monitor Metrics API**: Tested, but Fabric capacities do not expose CU utilization metrics via this API (only basic Azure metrics like availability).
- **Fabric Admin API**: Does not provide CU utilization metrics, only capacity state and workspace metadata.
- **Service Principal access to Capacity Metrics**: Not supported by Microsoft (Capacity Metrics semantic model is protected, only user accounts can query it).

**Open Questions**: 
- Will Microsoft eventually provide a Fabric Admin API endpoint for CU metrics? If so, we can replace Tier 3 with an automatic pull.
