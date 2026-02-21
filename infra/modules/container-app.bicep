@description('Azure region for Container Apps')
param location string

@description('Name of the Container Apps Environment')
param environmentName string

@description('Name of the Container App')
param appName string

@description('Environment type for scaling configuration')
@allowed([
  'Starter'
  'Enterprise'
])
param environmentType string

@description('Resource ID of the app subnet')
param subnetId string

@description('Resource ID of the user assigned managed identity')
param managedIdentityId string

@description('Database connection string')
@secure()
param databaseConnectionString string

@description('Admin API key')
@secure()
param adminApiKey string

@description('Container image to deploy')
param containerImage string

@description('Key Vault name for secret references')
param keyVaultName string

@description('Storage connection string for distributed locking')
@secure()
param storageConnectionString string = ''

@description('Resource tags')
param tags object = {}

var scaleConfig = {
  Starter: {
    minReplicas: 0
    maxReplicas: 3
    cpu: '0.5'
    memory: '1Gi'
  }
  Enterprise: {
    minReplicas: 1
    maxReplicas: 10
    cpu: '2.0'
    memory: '4Gi'
  }
}

var scale = scaleConfig[environmentType]

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: subnetId
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    zoneRedundant: environmentType == 'Enterprise'
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppEnvironment.id
    workloadProfileName: 'Consumption'
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'db-connection-string'
          value: databaseConnectionString
        }
        {
          name: 'admin-api-key'
          value: adminApiKey
        }
        {
          name: 'storage-connection-string'
          value: storageConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'main'
          image: containerImage
          resources: {
            cpu: json(scale.cpu)
            memory: scale.memory
          }
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'db-connection-string'
            }
            {
              name: 'ADMIN_API_KEY'
              secretRef: 'admin-api-key'
            }
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secretRef: 'storage-connection-string'
            }
            {
              name: 'AZURE_KEY_VAULT_URL'
              value: 'https://${keyVaultName}.vault.azure.net'
            }
            {
              name: 'COLLECTOR_INTERVAL_MINUTES'
              value: '15'
            }
            {
              name: 'COLLECTOR_MAX_CONCURRENCY'
              value: '10'
            }
            {
              name: 'LOG_LEVEL'
              value: 'INFO'
            }
          ]
        }
      ]
      scale: {
        minReplicas: scale.minReplicas
        maxReplicas: scale.maxReplicas
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

@description('Fully qualified domain name of the Container App')
output appFqdn string = containerApp.properties.configuration.ingress.fqdn

@description('Name of the Container App')
output appName string = containerApp.name

@description('Name of the Container Apps Environment')
output environmentName string = containerAppEnvironment.name
