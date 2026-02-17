#!/bin/bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 -g <resource-group> -l <location> -n <app-name> [-e <environment-type>]

Options:
  -g    Resource group name (will be created if it doesn't exist)
  -l    Azure region (e.g., eastus, westeurope)
  -n    Application name (3-20 chars, alphanumeric)
  -e    Environment type: Starter or Enterprise (default: Starter)
  -h    Show this help message

Example:
  $0 -g rg-fabricmon-prod -l eastus -n fabricmon -e Enterprise
EOF
  exit 1
}

RESOURCE_GROUP=""
LOCATION=""
APP_NAME=""
ENV_TYPE="Starter"

while getopts "g:l:n:e:h" opt; do
  case $opt in
    g) RESOURCE_GROUP="$OPTARG" ;;
    l) LOCATION="$OPTARG" ;;
    n) APP_NAME="$OPTARG" ;;
    e) ENV_TYPE="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

if [[ -z "$RESOURCE_GROUP" || -z "$LOCATION" || -z "$APP_NAME" ]]; then
  echo "Error: Missing required parameters"
  usage
fi

if [[ ! "$ENV_TYPE" =~ ^(Starter|Enterprise)$ ]]; then
  echo "Error: Environment type must be 'Starter' or 'Enterprise'"
  exit 1
fi

echo "Checking prerequisites..."
if ! command -v az &> /dev/null; then
  echo "Error: Azure CLI not found. Install from https://aka.ms/azure-cli"
  exit 1
fi

if ! az account show &> /dev/null; then
  echo "Error: Not logged in to Azure. Run 'az login' first"
  exit 1
fi

PASSWORD=$(openssl rand -base64 32)

echo "Creating resource group if needed..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

echo "Deploying infrastructure..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main.bicep \
  --parameters \
    appName="$APP_NAME" \
    environmentType="$ENV_TYPE" \
    databaseAdminPassword="$PASSWORD" \
    location="$LOCATION" \
  --query "properties.outputs" \
  --output json)

APP_URL=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.appUrl.value')
REGISTRY_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.registryName.value')
REGISTRY_LOGIN_SERVER=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.registryLoginServer.value')

echo ""
echo "Deployment complete."
echo "Application URL:    $APP_URL"
echo "Container Registry: $REGISTRY_LOGIN_SERVER"
