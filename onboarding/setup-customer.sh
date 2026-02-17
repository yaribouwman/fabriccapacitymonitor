#!/bin/bash
set -euo pipefail

die() { echo "Error: $1" >&2; exit 1; }

is_uuid() {
  [[ "$1" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]
}

command -v az &>/dev/null || die "Azure CLI not found. Install from https://aka.ms/azure-cli"
az account show &>/dev/null || die "Not logged in to Azure. Run 'az login' first."
command -v jq &>/dev/null || die "jq not found. Install from https://stedolan.github.io/jq/"

read -p "Azure Subscription ID: " SUBSCRIPTION_ID
is_uuid "$SUBSCRIPTION_ID" || die "Invalid Subscription ID format (expected UUID)"

echo ""
echo "IMPORTANT: You must provide the full resource ID of the Fabric Capacity to monitor."
echo "Example: /subscriptions/xxx/resourceGroups/rg-name/providers/Microsoft.Fabric/capacities/capacity-name"
echo ""
read -p "Fabric Capacity Resource ID: " CAPACITY_RESOURCE_ID
[ -z "$CAPACITY_RESOURCE_ID" ] && die "Fabric Capacity Resource ID is required"

read -p "App Registration name [FabricCapacityMonitor-ReadOnly]: " APP_NAME
APP_NAME=${APP_NAME:-FabricCapacityMonitor-ReadOnly}

echo "Creating App Registration..."
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)

echo "Creating Service Principal..."
SP_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)

echo "Creating client secret (expires in 1 year)..."
SECRET=$(az ad app credential reset --id "$APP_ID" --years 1 --query password -o tsv)

TENANT_ID=$(az account show --query tenantId -o tsv)

SCRIPT_DIR=$(dirname "$0")
ROLE_DEF_FILE="$SCRIPT_DIR/fabric-capacity-reader-role.json"

echo "Creating custom RBAC role if not exists..."
ROLE_NAME="Fabric Capacity Reader"

EXISTING_ROLE=$(az role definition list --name "$ROLE_NAME" --query "[0].name" -o tsv 2>/dev/null || true)

if [ -z "$EXISTING_ROLE" ]; then
  echo "Custom role not found. Creating it now..."
  TEMP_ROLE_DEF=$(mktemp)
  jq --arg sub "$SUBSCRIPTION_ID" '.AssignableScopes[0] = "/subscriptions/\($sub)"' "$ROLE_DEF_FILE" > "$TEMP_ROLE_DEF"
  az role definition create --role-definition "$TEMP_ROLE_DEF"
  rm "$TEMP_ROLE_DEF"
  echo "Custom role created successfully."
else
  echo "Custom role already exists."
fi

SCOPE="$CAPACITY_RESOURCE_ID"
echo "Granting '$ROLE_NAME' role on: $SCOPE"

az role assignment create \
  --assignee "$SP_ID" \
  --role "$ROLE_NAME" \
  --scope "$SCOPE"

echo ""
echo "Setup complete. Send these credentials to your consulting partner (via secure channel):"
echo ""
echo "Tenant ID:       $TENANT_ID"
echo "Client ID:       $APP_ID"
echo "Client Secret:   $SECRET"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource ID:     $CAPACITY_RESOURCE_ID"
echo ""
echo "To revoke access:"
echo "  az role assignment delete --assignee $SP_ID --scope \"$SCOPE\""
