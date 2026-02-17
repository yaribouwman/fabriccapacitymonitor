# Security Architecture

This document outlines the security controls and design decisions for the Fabric Capacity Monitor application.

## Network Isolation

### Database Security

**PostgreSQL Flexible Server** is deployed with private-only access:

- **Private Subnet**: Database deployed in dedicated subnet (`10.0.2.0/24`)
- **Private DNS Zone**: Uses Azure Private DNS (`privatelink.postgres.database.azure.com`)
- **No Public Endpoint**: No public IP address or public DNS record
- **Network Security Group**:
  ```
  Rule: AllowAppSubnet
  - Protocol: TCP
  - Source: 10.0.0.0/23 (app subnet only)
  - Destination Port: 5432
  - Action: Allow
  - Priority: 100
  ```

**Attack Surface**: Database is unreachable from the internet. Only Container Apps in the app subnet can connect.

### Key Vault Security

**Azure Key Vault** uses RBAC-based access control:

- **Public Network Access**: Enabled (required for Container Apps without Premium VNet)
- **RBAC Authorization**: Only the Container App's managed identity has `Key Vault Secrets User` role
- **No Access Policies**: Classic access policies disabled
- **Soft Delete**: 7-day retention for accidental deletions

**Attack Surface**: While publicly accessible, only authenticated requests with proper RBAC succeed.

## Identity and Access Management

### Managed Identity (Container App)

**User-Assigned Managed Identity** with least-privilege RBAC roles:

1. **Key Vault Secrets User** (`4633458b-17de-408a-b874-0445c86b69e6`)
   - Scope: Single Key Vault resource
   - Permissions: Read secret values only
   - No write, delete, or management permissions

2. **AcrPull** (`7f951dda-4ed3-4680-a7ca-43fe172d538d`)
   - Scope: Single Container Registry
   - Permissions: Pull container images only
   - No push or management permissions

### Customer Service Principal

**Custom RBAC Role**: `Fabric Capacity Reader` (recommended)

```json
{
  "Actions": [
    "Microsoft.Fabric/capacities/read",
    "Microsoft.Insights/metricDefinitions/read",
    "Microsoft.Insights/metrics/read"
  ]
}
```

- **Scope**: Single Fabric Capacity resource (enforced by onboarding script)
- **Permissions**: 3 read operations (vs 7,501 in built-in Reader role)
- **No Control Plane**: Cannot modify, delete, or manage resources

**Migration**: Existing deployments using the built-in `Reader` role should migrate to the custom role for least privilege.

## Authentication and Authorization

### API Endpoints

#### Admin Endpoints (Customer Management)

Protected by **X-Admin-Key** header authentication:

- `POST /api/customers` - Create customer
- `GET /api/customers` - List customers
- `GET /api/customers/{id}` - Get customer details
- `DELETE /api/customers/{id}` - Deactivate customer

**Admin API Key**:
- Generated during deployment (`newGuid()` in Bicep)
- Stored in Azure Key Vault (`admin-api-key` secret)
- Injected into Container App via secret reference
- Never logged or exposed in deployment outputs

#### Ingest Endpoint

Protected by **X-Ingest-Key** header authentication:

- `POST /api/ingest` - Ingest capacity metrics

**Ingest Key**:
- Unique 32-character random string per customer
- Stored in `customers.ingest_key` column (indexed)
- Validated against active customers only (`is_active = true`)

#### Customer Data Endpoints

No authentication required (public API), but **customer_id** scoped:

- `GET /api/customers/{customer_id}/capacities`
- `GET /api/customers/{customer_id}/capacities/{capacity_id}/metrics`
- `GET /api/customers/{customer_id}/capacities/{capacity_id}/snapshots`

**Note**: These endpoints should be protected in production. Consider adding authentication or making them admin-only.

## Data Isolation

### Application-Level Filtering

All queries filter by `customer_id`:

**Metrics Endpoint**:
```python
query = select(CapacityMetric).where(
    CapacityMetric.customer_id == customer_id,
    CapacityMetric.capacity_id == capacity_id,
)
```

**Snapshots Endpoint** (fixed in this release):
```python
# First, verify capacity belongs to customer
capacity = await db.execute(
    select(Capacity).where(
        Capacity.id == capacity_id,
        Capacity.customer_id == customer_id
    )
)
if not capacity.scalars().first():
    return []
# Then return snapshots
```

### Database Schema Constraints

**Foreign Keys with Cascade Delete**:

```sql
capacities.customer_id -> customers.id (ON DELETE CASCADE)
capacity_metrics.customer_id -> customers.id (ON DELETE CASCADE)
capacity_snapshots.capacity_id -> capacities.id (ON DELETE CASCADE)
```

When a customer is deleted, all their capacities, metrics, and snapshots are automatically removed.

### Row-Level Security (RLS)

**Status**: Not implemented

The application relies on application-level filtering. RLS policies would provide defense-in-depth but are not currently configured.

## Secrets Management

### Secret Storage

All secrets stored in **Azure Key Vault**:

| Secret | Purpose | Rotation |
|--------|---------|----------|
| `db-connection-string` | PostgreSQL connection | Manual |
| `admin-api-key` | Admin API authentication | Manual |
| `customer-{uuid}-secret` | Customer Azure SP credentials | Customer-managed |

### Secret Access

**Container App** retrieves secrets via:

1. Managed identity authenticates to Key Vault
2. Container Apps runtime fetches secrets at startup
3. Secrets injected as environment variables
4. Application code accesses via `os.environ`

**No Secrets in Code**:
- No hardcoded credentials
- No secrets in source control
- No secrets in Bicep outputs
- No secrets in logs (see next section)

### Secret Logging Protection

**Deploy Script** (`deploy.sh`):
```bash
PASSWORD=$(openssl rand -base64 32)  # Never echoed
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --parameters databaseAdminPassword="$PASSWORD" \
  --query "properties.outputs" \     # Only outputs, not parameters
  --output json)
```

**Application Logging** (`structlog`):
- Structured logging with context
- Customer secrets retrieved per-request, never logged
- Connection strings accessed from environment, not logged

**Customer Onboarding** (`setup-customer.sh`):
```bash
echo "Client Secret:   $SECRET"  # Intentional - for secure transmission
```

This is the only place a secret is printed, and it's by design for customer onboarding.

## Access Revocation

### Azure RBAC Revocation

Customer can remove access anytime:

```bash
az role assignment delete \
  --assignee <service-principal-id> \
  --scope <capacity-resource-id>
```

**Effect**: Service Principal can no longer call Azure APIs (2-5 minute propagation)

### Application-Level Deactivation

Admin can deactivate customer:

```bash
curl -X DELETE https://{app-url}/api/customers/{customer-id} \
  -H "X-Admin-Key: {admin-key}"
```

**Effect**:
- `is_active` flag set to `false`
- Ingest endpoint rejects requests (403)
- Collector skips customer in next cycle (up to 15-minute delay)

### Recommended Flow

1. Admin deactivates customer via API (immediate ingest block)
2. Customer removes Azure role assignment (immediate Azure API block)
3. Collector detects authentication failure and logs warning

## Attack Scenarios

### Cross-Customer Data Access

**Scenario**: Customer A attempts to access Customer B's data

**Mitigation**:
- All endpoints validate `customer_id` against `capacity_id`
- Database foreign keys enforce referential integrity
- Comprehensive test coverage (see `tests/test_data_isolation.py`)

**Example Attack**:
```bash
GET /api/customers/{customer-a-id}/capacities/{customer-b-capacity-id}/snapshots
# Returns: [] (empty array, no data leaked)
```

### Credential Theft

**Scenario**: Attacker obtains customer ingest key

**Mitigation**:
- Ingest key scoped to single customer
- Can only write metrics for customer's own capacities
- Cannot read other customers' data
- Cannot access admin endpoints

**Remediation**: Admin rotates ingest key via database update

### Database Compromise

**Scenario**: Attacker gains database access

**Mitigation**:
- No public database endpoint
- NSG allows only app subnet
- Credentials stored in Key Vault
- Connection string uses TLS (`sslmode=require`)

**Impact**: If database is compromised, attacker can access all customer data (data-at-rest encryption recommended)

### Admin API Key Theft

**Scenario**: Attacker obtains admin API key

**Mitigation**:
- Key stored in Key Vault (no code/config files)
- Only accessible via Container App managed identity
- Logged API calls for audit trail

**Remediation**: Rotate key in Key Vault, restart Container App

## Compliance and Best Practices

### OWASP Top 10

| Risk | Status | Mitigation |
|------|--------|-----------|
| A01:2021 - Broken Access Control | ✅ Mitigated | Customer_id validation on all endpoints |
| A02:2021 - Cryptographic Failures | ✅ Mitigated | TLS for all connections, Key Vault for secrets |
| A03:2021 - Injection | ✅ Mitigated | SQLAlchemy ORM with parameterized queries |
| A04:2021 - Insecure Design | ⚠️ Partial | Public customer data endpoints (should add auth) |
| A05:2021 - Security Misconfiguration | ✅ Mitigated | Least privilege RBAC, no public database |
| A07:2021 - Auth Failures | ✅ Mitigated | API key authentication, managed identity |

### Recommendations

**High Priority**:
1. Add authentication to customer data endpoints (`/api/customers/{id}/...`)
2. Implement Row-Level Security (RLS) policies in PostgreSQL
3. Add rate limiting to prevent DoS attacks
4. Enable Azure SQL Database encryption at rest

**Medium Priority**:
5. Add audit logging for all admin operations
6. Implement secret rotation policies
7. Add API request logging for security monitoring
8. Consider Azure Private Link for Key Vault

**Low Priority**:
9. Add CAPTCHA to prevent automated attacks
10. Implement IP allowlisting for admin endpoints

## Security Testing

### Automated Tests

**Test Coverage** (see `backend/tests/`):
- `test_data_isolation.py` - Customer data segregation
- `test_api_isolation.py` - API endpoint access control
- `test_customer_service.py` - Customer authentication

**Run Tests**:
```bash
cd backend
pytest tests/test_data_isolation.py -v
pytest tests/test_api_isolation.py -v
```

### Manual Testing

**Cross-Customer Access**:
```bash
# Create two customers, get their IDs
CUSTOMER_A_ID=...
CUSTOMER_B_ID=...

# Attempt to access Customer B's data using Customer A's ID
curl "https://{app-url}/api/customers/${CUSTOMER_A_ID}/capacities/${CUSTOMER_B_CAPACITY_ID}/snapshots"
# Expected: [] (empty array)
```

**Admin Authentication**:
```bash
# Attempt to list customers without admin key
curl "https://{app-url}/api/customers"
# Expected: 401 Unauthorized

# List customers with admin key
curl "https://{app-url}/api/customers" \
  -H "X-Admin-Key: {admin-key}"
# Expected: 200 OK with customer list
```

## Incident Response

### Security Incident Workflow

1. **Detect**: Monitor logs, alerts, and customer reports
2. **Contain**: Deactivate affected customers, rotate keys
3. **Investigate**: Review logs, database access, API calls
4. **Remediate**: Patch vulnerabilities, update configurations
5. **Recover**: Restore service, notify customers
6. **Learn**: Post-mortem, update security controls

### Contact Information

For security issues, contact: [security contact to be defined]

**Disclosure Policy**: Responsible disclosure within 90 days
