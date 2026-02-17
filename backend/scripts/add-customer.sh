#!/bin/bash
set -euo pipefail

die() { echo "Error: $1" >&2; exit 1; }

is_uuid() {
  [[ "$1" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]
}

if [ -z "${1:-}" ]; then
  echo "Usage: ./add-customer.sh <api-base-url>"
  echo "Example: ./add-customer.sh https://ca-fabricmon-prod.azurecontainerapps.io"
  exit 1
fi

API_URL="$1"
[[ "$API_URL" =~ ^https?:// ]] || die "Invalid URL: $API_URL (must start with http:// or https://)"

command -v jq &>/dev/null || die "jq is required but not installed"
command -v curl &>/dev/null || die "curl is required but not installed"

read -p "Customer Name: " CUSTOMER_NAME
[ -n "$CUSTOMER_NAME" ] || die "Customer name cannot be empty"

read -p "Azure Tenant ID: " TENANT_ID
is_uuid "$TENANT_ID" || die "Invalid Tenant ID format (expected UUID)"

read -p "Service Principal Client ID: " CLIENT_ID
is_uuid "$CLIENT_ID" || die "Invalid Client ID format (expected UUID)"

read -sp "Service Principal Client Secret: " CLIENT_SECRET
echo
[ -n "$CLIENT_SECRET" ] || die "Client secret cannot be empty"

read -p "Azure Subscription ID: " SUBSCRIPTION_ID
is_uuid "$SUBSCRIPTION_ID" || die "Invalid Subscription ID format (expected UUID)"

read -p "Resource Group (leave empty to scan entire subscription): " RESOURCE_GROUP

echo ""
echo "Name:            $CUSTOMER_NAME"
echo "Tenant ID:       $TENANT_ID"
echo "Client ID:       $CLIENT_ID"
echo "Client Secret:   ********"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource Group:  ${RESOURCE_GROUP:-(scan entire subscription)}"
echo ""

read -p "Is this correct? (y/n) " CONFIRM
[ "$CONFIRM" = "y" ] || { echo "Aborted."; exit 0; }

# Build JSON payload via jq to prevent injection from user input
JSON_PAYLOAD=$(jq -n \
  --arg name "$CUSTOMER_NAME" \
  --arg tenant_id "$TENANT_ID" \
  --arg client_id "$CLIENT_ID" \
  --arg client_secret "$CLIENT_SECRET" \
  --arg subscription_id "$SUBSCRIPTION_ID" \
  '{name: $name, tenant_id: $tenant_id, client_id: $client_id, client_secret: $client_secret, subscription_id: $subscription_id}')

if [ -n "$RESOURCE_GROUP" ]; then
  JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | jq --arg rg "$RESOURCE_GROUP" '. + {resource_group: $rg}')
fi

TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

echo "POST $API_URL/api/customers"

HTTP_CODE=$(curl -s -o "$TMPFILE" -w "%{http_code}" \
  -X POST "$API_URL/api/customers" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

BODY=$(cat "$TMPFILE")

if [ "$HTTP_CODE" != "201" ]; then
  echo "Failed (HTTP $HTTP_CODE):"
  echo "$BODY"
  exit 1
fi

CUSTOMER_ID=$(echo "$BODY" | jq -r '.id')
INGEST_KEY=$(echo "$BODY" | jq -r '.ingest_key // empty')

echo "Customer added. ID: $CUSTOMER_ID"

if [ -n "$INGEST_KEY" ]; then
  FILENAME="customer-${CUSTOMER_NAME// /-}-ingest-key.txt"
  echo "$INGEST_KEY" > "$FILENAME"
  echo "Ingest key saved to: $FILENAME"
  echo "Send this key to the customer for Tier 3 notebook configuration."
fi
