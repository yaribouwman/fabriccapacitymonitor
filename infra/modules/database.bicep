@description('Azure region for database resources')
param location string

@description('Name of the PostgreSQL server')
param serverName string

@description('Administrator login username')
param administratorLogin string

@description('Administrator login password')
@secure()
param administratorLoginPassword string

@description('Database name')
param databaseName string

@description('Environment type for SKU selection')
@allowed([
  'Starter'
  'Enterprise'
])
param environmentType string

@description('Resource ID of the database subnet')
param subnetId string

@description('Resource ID of the virtual network')
param vnetId string

@description('Resource tags')
param tags object = {}

var skuConfig = {
  Starter: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
    storageSizeGB: 32
    backupRetentionDays: 7
    geoRedundantBackup: 'Disabled'
    highAvailability: 'Disabled'
  }
  Enterprise: {
    name: 'Standard_D2s_v3'
    tier: 'GeneralPurpose'
    storageSizeGB: 128
    backupRetentionDays: 35
    geoRedundantBackup: 'Enabled'
    highAvailability: 'ZoneRedundant'
  }
}

var sku = skuConfig[environmentType]

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.postgres.database.azure.com'
  location: 'global'
  tags: tags
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: '${serverName}-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: sku.name
    tier: sku.tier
  }
  properties: {
    version: '16'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    storage: {
      storageSizeGB: sku.storageSizeGB
    }
    backup: {
      backupRetentionDays: sku.backupRetentionDays
      geoRedundantBackup: sku.geoRedundantBackup
    }
    highAvailability: {
      mode: sku.highAvailability
    }
    network: {
      delegatedSubnetResourceId: subnetId
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
  dependsOn: [
    privateDnsZoneLink
  ]
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: databaseName
}

@description('Fully qualified domain name of the PostgreSQL server')
output fqdn string = postgresServer.properties.fullyQualifiedDomainName

@description('Name of the PostgreSQL server')
output serverName string = postgresServer.name

@description('Name of the database')
output databaseName string = database.name
