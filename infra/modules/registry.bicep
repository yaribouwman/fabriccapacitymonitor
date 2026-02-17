@description('Azure region for Container Registry')
param location string

@description('Name of the Container Registry')
param registryName string

@description('Principal ID of the managed identity to grant AcrPull access')
param managedIdentityPrincipalId string

@description('Resource tags')
param tags object = {}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    // Basic SKU does not support private endpoints; public access is required.
    // Image pulls are authenticated via managed identity (AcrPull RBAC), not admin credentials.
    // Upgrade to Premium SKU and add a private endpoint to lock this down further.
    publicNetworkAccess: 'Enabled'
    zoneRedundancy: 'Disabled'
  }
}

resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, managedIdentityPrincipalId, 'AcrPull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('Name of the Container Registry')
output registryName string = containerRegistry.name

@description('Login server of the Container Registry')
output loginServer string = containerRegistry.properties.loginServer
