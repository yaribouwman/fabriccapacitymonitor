# Power BI Setup Guide

Complete guide for connecting Power BI to your Fabric Capacity Monitor database and building dashboards.

## Challenge: VNET-Integrated Database

The PostgreSQL database is VNET-integrated with no public endpoint for security. Power BI needs special configuration to access it.

## Two Approaches

| Approach | Best For | Complexity | Security | Setup Time |
|----------|----------|------------|----------|------------|
| **Firewall Rules** | Testing, POC, small teams | Low | Medium | 5 minutes |
| **Data Gateway** | Production, enterprise, compliance | Medium | High | 30 minutes |

Choose based on your requirements and environment.

## Approach 1: Firewall Rules (Quick Setup)

Enable public access with restricted IP ranges. Good for testing and small deployments.

### Step 1: Enable Public Access on PostgreSQL

```bash
# Get your public IP
MY_IP=$(curl -s https://ifconfig.me)
echo "Your IP: $MY_IP"

# Add firewall rule for your IP
az postgres flexible-server firewall-rule create \
  --resource-group rg-fabricmon-prod \
  --name pg-fabricmon-prod \
  --rule-name AllowMyWorkstation \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

### Step 2: Add Power BI Service IP Ranges (For Power BI Service)

If publishing to Power BI Service, add Microsoft's IP ranges:

```bash
# Power BI Service IPs vary by region
# For global coverage, add these common ranges:

az postgres flexible-server firewall-rule create \
  --resource-group rg-fabricmon-prod \
  --name pg-fabricmon-prod \
  --rule-name AllowPowerBIService \
  --start-ip-address 13.66.140.0 \
  --end-ip-address 13.66.140.255

# Add more ranges based on your region
# See: https://learn.microsoft.com/power-bi/enterprise/service-admin-power-bi-security
```

**Important:** Power BI Service IPs change regularly. For production, use Approach 2 (Data Gateway) instead.

### Step 3: Get Connection Details

```bash
# Get database connection string from Key Vault
az keyvault secret show \
  --vault-name kv-fabricmon-prod \
  --name db-connection-string \
  --query value -o tsv
```

Extract the server hostname, database name, username, and password from the connection string.

### Step 4: Connect Power BI Desktop

1. Open Power BI Desktop
2. **Get Data** → **PostgreSQL database**
3. Enter the server hostname and database name from the connection string
4. Authenticate with **Database** method using the username and password from Key Vault

### Step 5: Load Tables

Select the tables you need (`customers`, `capacities`, `capacity_snapshots`, `capacity_metrics`) and load them.

### Security Considerations

**Pros:**
- Quick setup
- Works with Power BI Desktop and Service
- No additional infrastructure

**Cons:**
- Database exposed to internet (even if restricted)
- IP addresses can change
- Power BI Service IPs change frequently
- Not suitable for compliance requirements

**Recommendation:** Use for testing only. Switch to Approach 2 for production.

## Approach 2: Azure Data Gateway (Secure)

Use an on-premises data gateway to connect securely without exposing the database.

### Architecture

```
Power BI Service → Data Gateway (in Azure VNET) → PostgreSQL (private)
```

The gateway acts as a bridge between Power BI Service and your private database.

### Step 1: Create Gateway Virtual Machine

Create a VM in the same VNET as your database:

```bash
# Create subnet for gateway
az network vnet subnet create \
  --resource-group rg-fabricmon-prod \
  --vnet-name vnet-fabricmon-prod \
  --name snet-gateway \
  --address-prefix 10.0.3.0/24

# Create VM
az vm create \
  --resource-group rg-fabricmon-prod \
  --name vm-gateway-fabricmon \
  --image Win2022Datacenter \
  --size Standard_D2s_v3 \
  --vnet-name vnet-fabricmon-prod \
  --subnet snet-gateway \
  --admin-username azureuser \
  --admin-password '<your-secure-password>'
```

### Step 2: Install On-Premises Data Gateway

1. RDP into the gateway VM
2. Download and install the On-Premises Data Gateway:
   - Download: https://aka.ms/on-premises-data-gateway
3. During installation:
   - Sign in with your Power BI account
   - Register the gateway with a name (e.g., "FabricMonitor-Gateway")
   - Keep default port 8080

### Step 3: Configure Gateway for PostgreSQL

On the gateway VM:

1. Download and install PostgreSQL ODBC driver:
   - Download: https://www.postgresql.org/ftp/odbc/versions/
   - Install: `psqlodbc_x64.msi`

2. Configure ODBC Data Source:
   - Open **ODBC Data Sources (64-bit)**
   - Click **Add** → Select **PostgreSQL Unicode**
   - Configure:
     - **Data Source**: `FabricMonitor`
     - **Server**: `pg-fabricmon-prod.postgres.database.azure.com`
     - **Port**: `5432`
     - **Database**: `fabricmon`
     - **User Name**: `dbadmin`
     - **Password**: (from Key Vault)
     - **SSL Mode**: `require`
   - Click **Test** to verify connection

### Step 4: Configure Gateway in Power BI Service

1. Go to Power BI Service (app.powerbi.com)
2. Click **Settings** → **Manage gateways**
3. Your gateway should appear in the list
4. Click the gateway → **Settings**
5. Click **Add data source**:
   - **Data Source Name**: `FabricMonitor-PostgreSQL`
   - **Data Source Type**: `PostgreSQL`
   - **Server**: `pg-fabricmon-prod.postgres.database.azure.com`
   - **Database**: `fabricmon`
   - **Authentication Method**: `Basic`
   - **Username**: `dbadmin`
   - **Password**: (from Key Vault)
6. Click **Add**

### Step 5: Connect and Publish

1. In Power BI Desktop, connect via **Get Data** → **PostgreSQL database** using the same connection details as Approach 1
2. Build your report and click **Publish**
3. In Power BI Service, open the dataset settings and map the **Gateway connection** to your PostgreSQL data source

### Security Considerations

**Pros:**
- Database remains private (no public endpoint)
- Centralized credential management
- Suitable for compliance (SOC 2, HIPAA, etc.)
- Supports scheduled refresh

**Cons:**
- Requires VM for gateway
- Additional cost (~$70/month for D2s_v3 VM)
- More setup complexity

**Recommendation:** Use for production environments and enterprise deployments.

## Power BI Data Model

### Tables and Relationships

```
customers (1) ─────< (∞) capacities
                         │
                         ├─────< (∞) capacity_snapshots
                         │
                         └─────< (∞) capacity_metrics
```

### Recommended Data Transformations

#### 1. Create Date Table

```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), TODAY()),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM YYYY"),
    "Quarter", "Q" & QUARTER([Date]) & " " & YEAR([Date]),
    "DayOfWeek", FORMAT([Date], "ddd")
)
```

#### 2. Create Measures

```dax
// Current CU Utilization
Current CU Utilization = 
CALCULATE(
    AVERAGE(capacity_metrics[metric_value]),
    capacity_metrics[metric_name] = "CU_Utilization_Pct",
    capacity_metrics[collected_at] = MAX(capacity_metrics[collected_at])
)

// Average Utilization (Last 24h)
Avg Utilization 24h = 
CALCULATE(
    AVERAGE(capacity_metrics[metric_value]),
    capacity_metrics[metric_name] = "CU_Utilization_Pct",
    capacity_metrics[collected_at] >= NOW() - 1
)

// Peak Utilization (Last 24h)
Peak Utilization 24h = 
CALCULATE(
    MAX(capacity_metrics[metric_value]),
    capacity_metrics[metric_name] = "CU_Utilization_Pct",
    capacity_metrics[collected_at] >= NOW() - 1
)

// Total Throttled Operations
Total Throttled = 
CALCULATE(
    SUM(capacity_metrics[metric_value]),
    capacity_metrics[metric_name] = "Throttled_Operations"
)

// Capacity Health Status
Health Status = 
VAR CurrentUtil = [Current CU Utilization]
RETURN
    SWITCH(
        TRUE(),
        CurrentUtil < 50, "Healthy",
        CurrentUtil < 80, "Warning",
        "Critical"
    )
```

## Sample Dashboard Layout

### Page 1: Executive Overview

**Header:**
- Card: Total Customers
- Card: Total Capacities
- Card: Average Utilization (All)

**Main:**
- Line chart: CU Utilization over time (last 7 days)
- Bar chart: Top 10 capacities by utilization
- Table: All capacities with current status

### Page 2: Customer Detail

Slicers for customer and capacity name. Visuals: CU utilization gauge, utilization trend line chart, peak/average/overloaded/throttled cards, and a capacity details table.

### Page 3: Capacity Health

Matrix of customers vs. capacities colored by health status (green/yellow/red), plus a table of capacities exceeding 80% utilization.

## Power Query (M) Samples

### Load Capacity Metrics with Time Filter

```m
let
    Source = PostgreSQL.Database("pg-fabricmon-prod.postgres.database.azure.com", "fabricmon"),
    capacity_metrics = Source{[Schema="public",Item="capacity_metrics"]}[Data],
    #"Filtered Rows" = Table.SelectRows(capacity_metrics, each [collected_at] >= DateTime.AddDays(DateTime.LocalNow(), -30)),
    #"Changed Type" = Table.TransformColumnTypes(#"Filtered Rows",{{"metric_value", type number}, {"collected_at", type datetime}})
in
    #"Changed Type"
```

### Join Capacities with Customer Names

```m
let
    Source_Capacities = PostgreSQL.Database("pg-fabricmon-prod.postgres.database.azure.com", "fabricmon"){[Schema="public",Item="capacities"]}[Data],
    Source_Customers = PostgreSQL.Database("pg-fabricmon-prod.postgres.database.azure.com", "fabricmon"){[Schema="public",Item="customers"]}[Data],
    MergedQueries = Table.NestedJoin(Source_Capacities, {"customer_id"}, Source_Customers, {"id"}, "customers", JoinKind.Inner),
    #"Expanded customers" = Table.ExpandTableColumn(MergedQueries, "customers", {"name"}, {"customer_name"})
in
    #"Expanded customers"
```

## Refresh Schedule

### Scheduled Refresh (Power BI Service)

1. Go to dataset settings
2. Click **Scheduled refresh**
3. Set frequency:
   - **Recommended:** Every 15 minutes (aligns with data collector)
   - **Minimum:** Hourly
4. Set time zone
5. Click **Apply**

**Note:** Scheduled refresh requires gateway (Approach 2) or public database access (Approach 1).

## Performance Optimization

Use **Import** mode (recommended for datasets under 1 GB) for fast dashboards with scheduled refresh. Switch to **DirectQuery** only for very large datasets where real-time data is critical.

For large datasets, filter to recent data in Power Query and consider aggregating at the database level:

```sql
CREATE VIEW daily_utilization AS
SELECT 
    capacity_id,
    DATE(collected_at) as date,
    AVG(metric_value) as avg_utilization,
    MAX(metric_value) as peak_utilization
FROM capacity_metrics
WHERE metric_name = 'CU_Utilization_Pct'
GROUP BY capacity_id, DATE(collected_at);
```

## Troubleshooting

### Cannot Connect to Database

Check firewall rules (Approach 1) or gateway status (Approach 2), verify credentials, and confirm the database server is running.

### Refresh Fails in Power BI Service

Check gateway status, data source credentials, and Power BI Service IP firewall rules. View refresh history in dataset settings for error details.

### Slow Dashboard Performance

Switch to Import mode, filter data in Power Query to recent periods, and add database indexes:

```sql
CREATE INDEX idx_metrics_time ON capacity_metrics(collected_at);
CREATE INDEX idx_metrics_capacity_name ON capacity_metrics(capacity_id, metric_name);
```

## Next Steps

- [Add more customers](onboarding.md)
- [Monitor operations](operations.md)
- [Scale infrastructure](operations.md#scale-from-starter-to-enterprise)
- Build alerting (send Teams/email when utilization > 80%)

## Resources

- [Power BI PostgreSQL Connector Documentation](https://learn.microsoft.com/power-bi/connect-data/desktop-connect-postgres)
- [On-Premises Data Gateway Documentation](https://learn.microsoft.com/data-integration/gateway/service-gateway-onprem)
- [Power BI Security Best Practices](https://learn.microsoft.com/power-bi/enterprise/service-admin-power-bi-security)
