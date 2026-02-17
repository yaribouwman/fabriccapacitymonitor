@description('Azure region for the identity')
param location string

@description('Name of the user assigned managed identity')
param identityName string

@description('Resource tags')
param tags object = {}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

@description('Resource ID of the managed identity')
output identityId string = userAssignedIdentity.id

@description('Principal ID of the managed identity')
output principalId string = userAssignedIdentity.properties.principalId

@description('Client ID of the managed identity')
output clientId string = userAssignedIdentity.properties.clientId
