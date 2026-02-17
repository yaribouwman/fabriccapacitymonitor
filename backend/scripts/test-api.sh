#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: ./test-api.sh <api-base-url>"
  echo "Example: ./test-api.sh https://ca-fabricmon-prod.azurecontainerapps.io"
  exit 1
fi

API_URL="$1"
PASS=0
FAIL=0
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

request() {
  local method="$1" url="$2"
  shift 2
  HTTP_CODE=$(curl -s -o "$TMPFILE" -w "%{http_code}" -X "$method" "$url" "$@")
  BODY=$(cat "$TMPFILE")
}

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "Testing API at $API_URL"
echo ""

# 1. Health check
echo "1. Health check"
request GET "$API_URL/health"
if [ "$HTTP_CODE" = "200" ]; then
  pass "returned $HTTP_CODE"
else
  fail "returned $HTTP_CODE: $BODY"
  echo "Health check failed, aborting."
  exit 1
fi

# 2. List customers
echo "2. List customers"
request GET "$API_URL/api/customers"
if [ "$HTTP_CODE" = "200" ]; then
  pass "returned $HTTP_CODE"
else
  fail "returned $HTTP_CODE: $BODY"
fi

# 3. Create test customer
echo "3. Create test customer"
request POST "$API_URL/api/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "tenant_id": "00000000-0000-0000-0000-000000000000",
    "client_id": "11111111-1111-1111-1111-111111111111",
    "client_secret": "test-secret-do-not-use-in-production",
    "subscription_id": "22222222-2222-2222-2222-222222222222"
  }'

if [ "$HTTP_CODE" = "201" ]; then
  pass "returned $HTTP_CODE"
  CUSTOMER_ID=$(echo "$BODY" | jq -r '.id // empty')
  INGEST_KEY=$(echo "$BODY" | jq -r '.ingest_key // empty')
else
  fail "returned $HTTP_CODE: $BODY"
fi

# 4. Get customer details
if [ -n "${CUSTOMER_ID:-}" ]; then
  echo "4. Get customer details"
  request GET "$API_URL/api/customers/$CUSTOMER_ID"
  if [ "$HTTP_CODE" = "200" ]; then
    pass "returned $HTTP_CODE"
  else
    fail "returned $HTTP_CODE: $BODY"
  fi
fi

# 5. List customer capacities
if [ -n "${CUSTOMER_ID:-}" ]; then
  echo "5. List customer capacities"
  request GET "$API_URL/api/customers/$CUSTOMER_ID/capacities"
  if [ "$HTTP_CODE" = "200" ]; then
    pass "returned $HTTP_CODE (empty until collector runs)"
  else
    fail "returned $HTTP_CODE: $BODY"
  fi
fi

# 6. Test ingest endpoint
if [ -n "${INGEST_KEY:-}" ]; then
  echo "6. Test ingest endpoint"
  request POST "$API_URL/api/ingest" \
    -H "Content-Type: application/json" \
    -H "X-Ingest-Key: $INGEST_KEY" \
    -d '{"capacity_name": "test-capacity", "metrics": [{"name": "CU_Utilization_Pct", "value": 75.5, "aggregation": "Average"}]}'

  if [ "$HTTP_CODE" = "404" ]; then
    pass "returned $HTTP_CODE (expected: capacity not found before collector runs)"
  elif [ "$HTTP_CODE" = "202" ]; then
    pass "returned $HTTP_CODE"
  else
    fail "returned $HTTP_CODE: $BODY"
  fi
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
