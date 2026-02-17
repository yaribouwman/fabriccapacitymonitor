targetScope = 'subscription'

@description('Name for the App Registration')
param appName string = 'FabricCapacityMonitor-ReadOnly'

@description('Resource ID of the Fabric capacity to monitor (required)')
param capacityResourceId string

var roleScope = capacityResourceId

resource app 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: appName
  displayName: appName
}

resource sp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: app.appId
}

resource readerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(roleScope, sp.id, 'Reader')
  scope: tenant()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
    principalId: sp.id
    principalType: 'ServicePrincipal'
  }
}

output tenantId string = tenant().tenantId
output clientId string = app.appId
output servicePrincipalId string = sp.id
output instructions string = 'Create a client secret in Azure Portal > App registrations > ${appName} > Certificates & secrets. Send Tenant ID, Client ID, and the secret to your consulting partner.'
