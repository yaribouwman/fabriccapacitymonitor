targetScope = 'resourceGroup'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Base name for the application')
@minLength(3)
@maxLength(20)
param appName string

@description('Environment type')
@allowed([
  'Starter'
  'Enterprise'
])
param environmentType string = 'Starter'

@description('Container image to deploy')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Database administrator login')
param databaseAdminLogin string = 'dbadmin'

// newGuid() is a deployment-time fallback so first-run works without extra params.
// It is NOT cryptographically random. Production deployments should supply a proper
// password via parameter override or rotate credentials post-deploy.
@description('Database administrator password')
@secure()
param databaseAdminPassword string = newGuid()

@description('Admin API key for management endpoints')
@secure()
param adminApiKey string = newGuid()

@description('Database name')
param databaseName string = 'fabricmon'

@description('Owner name for tagging')
param ownerName string = 'Yari Bouwman'

@description('Cost center for tagging')
param costCenter string = 'Engineering'

@description('Email addresses for alert notifications (comma-separated, e.g. a@example.com,b@example.com)')
param alertEmails string = ''

var alertEmailsArray = empty(alertEmails) ? [] : split(alertEmails, ',')

var nameSuffix = uniqueString(resourceGroup().id)
var tags = {
  Owner: ownerName
  Environment: environmentType
  CostCenter: costCenter
  Project: 'Fabric Capacity Monitor'
}

module identity 'modules/identity.bicep' = {
  name: 'identity-deployment'
  params: {
    location: location
    identityName: 'id-${appName}-${nameSuffix}'
    tags: tags
  }
}

module network 'modules/network.bicep' = {
  name: 'network-deployment'
  params: {
    location: location
    vnetName: 'vnet-${appName}-${nameSuffix}'
    namePrefix: appName
    tags: tags
  }
}

module database 'modules/database.bicep' = {
  name: 'database-deployment'
  params: {
    location: location
    serverName: 'psql-${appName}-${nameSuffix}'
    administratorLogin: databaseAdminLogin
    administratorLoginPassword: databaseAdminPassword
    databaseName: databaseName
    environmentType: environmentType
    subnetId: network.outputs.dbSubnetId
    vnetId: network.outputs.vnetId
    tags: tags
  }
}

module registry 'modules/registry.bicep' = {
  name: 'registry-deployment'
  params: {
    location: location
    registryName: 'acr${appName}${nameSuffix}'
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  params: {
    location: location
    storageAccountName: 'st${appName}${nameSuffix}'
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

var databaseConnectionString = 'postgresql://${databaseAdminLogin}:${databaseAdminPassword}@${database.outputs.fqdn}:5432/${databaseName}?sslmode=require'

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  params: {
    location: location
    keyVaultName: 'kv-${appName}-${nameSuffix}'
    managedIdentityPrincipalId: identity.outputs.principalId
    databaseConnectionString: databaseConnectionString
    adminApiKey: adminApiKey
    environmentType: environmentType
    privateEndpointSubnetId: network.outputs.privateEndpointSubnetId
    vnetId: network.outputs.vnetId
    tags: tags
  }
}

module containerApp 'modules/container-app.bicep' = {
  name: 'containerapp-deployment'
  params: {
    location: location
    environmentName: 'cae-${appName}-${nameSuffix}'
    appName: 'ca-${appName}-${nameSuffix}'
    environmentType: environmentType
    subnetId: network.outputs.appSubnetId
    managedIdentityId: identity.outputs.identityId
    containerImage: containerImage
    keyVaultName: keyVault.outputs.keyVaultName
    storageConnectionString: storage.outputs.connectionString
    tags: tags
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring-deployment'
  params: {
    keyVaultId: resourceId('Microsoft.KeyVault/vaults', keyVault.outputs.keyVaultName)
    containerAppId: resourceId('Microsoft.App/containerApps', containerApp.outputs.appName)
    alertEmails: alertEmailsArray
    environmentType: environmentType
    tags: tags
  }
}

@description('Container App URL')
output appUrl string = 'https://${containerApp.outputs.appFqdn}'

@description('Container Registry login server')
output registryLoginServer string = registry.outputs.loginServer

@description('Container Registry name')
output registryName string = registry.outputs.registryName

@description('Storage account name for distributed locking')
output storageAccountName string = storage.outputs.storageAccountName
