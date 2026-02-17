@description('Azure region for network resources')
param location string

@description('Name of the virtual network')
param vnetName string

@description('Name prefix for subnets and NSGs')
param namePrefix string

@description('Resource tags')
param tags object = {}

var vnetAddressPrefix = '10.0.0.0/16'
var appSubnetAddressPrefix = '10.0.0.0/23'
var dbSubnetAddressPrefix = '10.0.2.0/24'
var privateEndpointSubnetAddressPrefix = '10.0.3.0/24'

resource nsgApp 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: '${namePrefix}-nsg-app'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowAzureLoadBalancer'
        properties: {
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: 'AzureLoadBalancer'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource nsgDb 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: '${namePrefix}-nsg-db'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowAppSubnet'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '5432'
          sourceAddressPrefix: appSubnetAddressPrefix
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource nsgPrivateEndpoint 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: '${namePrefix}-nsg-pe'
  location: location
  tags: tags
  properties: {
    securityRules: []
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: '${namePrefix}-snet-app'
        properties: {
          addressPrefix: appSubnetAddressPrefix
          networkSecurityGroup: {
            id: nsgApp.id
          }
          delegations: [
            {
              name: 'Microsoft.App.environments'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: '${namePrefix}-snet-db'
        properties: {
          addressPrefix: dbSubnetAddressPrefix
          networkSecurityGroup: {
            id: nsgDb.id
          }
          delegations: [
            {
              name: 'Microsoft.DBforPostgreSQL.flexibleServers'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
      {
        name: '${namePrefix}-snet-pe'
        properties: {
          addressPrefix: privateEndpointSubnetAddressPrefix
          networkSecurityGroup: {
            id: nsgPrivateEndpoint.id
          }
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

@description('Resource ID of the virtual network')
output vnetId string = vnet.id

@description('Resource ID of the app subnet')
output appSubnetId string = vnet.properties.subnets[0].id

@description('Resource ID of the database subnet')
output dbSubnetId string = vnet.properties.subnets[1].id

@description('Resource ID of the private endpoint subnet')
output privateEndpointSubnetId string = vnet.properties.subnets[2].id

@description('Name of the virtual network')
output vnetName string = vnet.name
