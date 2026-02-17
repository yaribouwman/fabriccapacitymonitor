@description('Resource ID of the Key Vault')
param keyVaultId string

@description('Resource ID of the Container App')
param containerAppId string

@description('Action group email addresses for alerts')
param alertEmails array = []

@description('Environment type')
@allowed(['Starter', 'Enterprise'])
param environmentType string = 'Starter'

@description('Resource tags')
param tags object = {}

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = if (length(alertEmails) > 0) {
  name: 'ag-fabricmon-alerts'
  location: 'global'
  tags: tags
  properties: {
    groupShortName: 'FabricMon'
    enabled: true
    emailReceivers: [for (email, i) in alertEmails: {
      name: 'email-${i}'
      emailAddress: email
      useCommonAlertSchema: true
    }]
  }
}

resource keyVaultAccessAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (length(alertEmails) > 0) {
  name: 'alert-keyvault-failed-requests'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when Key Vault has failed authentication requests (potential breach or misconfiguration)'
    severity: 1
    enabled: true
    scopes: [
      keyVaultId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'FailedRequests'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'ServiceApiResult'
          metricNamespace: 'Microsoft.KeyVault/vaults'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Count'
          dimensions: [
            {
              name: 'StatusCode'
              operator: 'Include'
              values: [
                '401'
                '403'
              ]
            }
          ]
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource keyVaultAvailabilityAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (length(alertEmails) > 0) {
  name: 'alert-keyvault-availability'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when Key Vault availability drops below 99.9%'
    severity: 2
    enabled: true
    scopes: [
      keyVaultId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'Availability'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'Availability'
          metricNamespace: 'Microsoft.KeyVault/vaults'
          operator: 'LessThan'
          threshold: 99
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource containerAppCpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (length(alertEmails) > 0 && environmentType == 'Enterprise') {
  name: 'alert-containerapp-high-cpu'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when Container App CPU usage exceeds 80%'
    severity: 2
    enabled: true
    scopes: [
      containerAppId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'CpuUsage'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'UsageNanoCores'
          metricNamespace: 'Microsoft.App/containerApps'
          operator: 'GreaterThan'
          threshold: 1600000000
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource containerAppMemoryAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (length(alertEmails) > 0 && environmentType == 'Enterprise') {
  name: 'alert-containerapp-high-memory'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when Container App memory usage exceeds 80%'
    severity: 2
    enabled: true
    scopes: [
      containerAppId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'MemoryUsage'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'WorkingSetBytes'
          metricNamespace: 'Microsoft.App/containerApps'
          operator: 'GreaterThan'
          threshold: 3355443200
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

@description('Action Group ID')
output actionGroupId string = length(alertEmails) > 0 ? actionGroup.id : ''
