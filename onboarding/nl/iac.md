# Infrastructure as Code Setup (Bicep)

**Aanbevolen voor**: Enterprises met change management vereisten

**Tijd**: 10 minuten  
**Vereisten**: Azure CLI, Bicep kennis, change management proces

Infrastructure-as-Code template voor enterprise change management en audit trails.

## Vereisten

- Azure CLI met Bicep geïnstalleerd
- Kennis van Azure Bicep/ARM templates
- Change management proces van uw organisatie
- Azure Administrator of Owner rol op uw Fabric capaciteit

## Stap 1: Download de Bicep Template

Download deze bestanden van uw consultant of GitHub repository:
- `setup-customer.bicep`
- `bicepconfig.json` (optioneel)

## Stap 2: Bekijk de Template

Bekijk de Bicep template om de resources te begrijpen die worden aangemaakt:

```bash
cat setup-customer.bicep
```

De template maakt aan:
1. Azure AD App Registration
2. Service Principal
3. Role assignment (Reader) op de Fabric capaciteit

## Stap 3: Indienen voor Change Management

Als uw organisatie change management vereist voor infrastructuur wijzigingen, dien de Bicep template in via uw standaard goedkeuringsproces.

Neem op in uw change request:
- Beschrijving: "Aanmaken read-only Service Principal voor Fabric capaciteit monitoring"
- Risico niveau: Laag (read-only toegang, beperkt tot enkele resource)
- Rollback plan: Verwijder App Registration via `az ad app delete`

## Stap 4: Deploy de Template

```bash
az login

az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

Vervang de `capacityResourceId` met uw werkelijke Fabric capacity resource ID.

Om uw capacity resource ID te vinden:

```bash
az resource list \
  --resource-type "Microsoft.Fabric/capacities" \
  --query "[].id" -o tsv
```

## Stap 5: Haal Deployment Outputs Op

De deployment toont:
- Tenant ID
- Client ID
- Service Principal ID

Voorbeeld:

```bash
az deployment subscription show \
  --name setup-customer \
  --query properties.outputs
```

## Stap 6: Maak Client Secret Handmatig Aan

Bicep kan geen secrets tonen om beveiligingsredenen. Maak het client secret handmatig aan:

### Via Portal:
1. Ga naar Azure Portal → **Entra ID** → **App registrations**
2. Vind `FabricCapacityMonitor-ReadOnly`
3. Ga naar **Certificates & secrets** → **New client secret**
4. Kopieer de secret waarde

### Via CLI:
```bash
az ad app credential reset \
  --id <application-id> \
  --append \
  --display-name "Fabric Monitor Access" \
  --years 2
```

Kopieer de `password` waarde uit de output.

## Stap 7: Verstuur Credentials naar Uw Consultant

Stuur deze waarden naar uw consultant via een beveiligd kanaal:
- Tenant ID (van deployment output)
- Client ID (van deployment output)
- Client Secret (van stap 6)
- Subscription ID
- Resource Group
- Capacity Name

## Deployment Parameters

De Bicep template accepteert deze parameters:

| Parameter | Verplicht | Beschrijving |
|-----------|-----------|--------------|
| `appName` | Ja | Naam voor de App Registration |
| `capacityResourceId` | Ja | Volledige resource ID van uw Fabric capaciteit |
| `location` | Nee | Azure regio (standaard deployment locatie) |

Voorbeeld parameter bestand (`setup-customer.parameters.json`):

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appName": {
      "value": "FabricCapacityMonitor-ReadOnly"
    },
    "capacityResourceId": {
      "value": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-fabric-prod/providers/Microsoft.Fabric/capacities/fabriccap01"
    }
  }
}
```

Deploy met parameter bestand:

```bash
az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters setup-customer.parameters.json
```

## Valideren van de Deployment

Valideer de template voordat u deployt:

```bash
az deployment subscription validate \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

## Verificatie van de Setup

Controleer de App Registration:

```bash
az ad app list --display-name "FabricCapacityMonitor-ReadOnly"
```

Controleer de role assignment:

```bash
az role assignment list \
  --scope /subscriptions/.../Microsoft.Fabric/capacities/... \
  --role "Reader"
```

## Deployment Logs

Bekijk deployment logs:

```bash
az deployment subscription show \
  --name setup-customer \
  --query properties.error
```

## Probleemoplossing

**Probleem: Deployment validatie faalt**  
**Oplossing**: Controleer of de capacity resource ID correct is en u de juiste rechten heeft

**Probleem: Kan App Registration niet aanmaken**  
**Oplossing**: Vereist Azure AD Application Administrator rol of hoger

**Probleem: Role assignment faalt**  
**Oplossing**: Vereist Owner of User Access Administrator op de capacity resource

**Probleem: Deployment bestaat al**  
**Oplossing**: Gebruik een andere deployment naam:

```bash
az deployment subscription create \
  --name setup-customer-v2 \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters ...
```

## Hoe Toegang In Te Trekken

### Verwijder de volledige deployment:

```bash
# Haal het Service Principal ID op
SP_ID=$(az ad sp list --display-name "FabricCapacityMonitor-ReadOnly" --query "[0].id" -o tsv)

# Verwijder role assignment
az role assignment delete \
  --assignee $SP_ID \
  --scope /subscriptions/.../Microsoft.Fabric/capacities/...

# Verwijder App Registration
az ad app delete --id <application-id>
```

### Of re-deploy met bijgewerkte parameters:

Update de Bicep template of parameters en deploy opnieuw om de configuratie te wijzigen.

## Change History

Houd een change log bij voor uw deployments:

```bash
# Lijst alle subscription deployments
az deployment subscription list \
  --query "[?contains(name, 'setup-customer')].{Name:name, State:properties.provisioningState, Timestamp:properties.timestamp}" \
  -o table
```

## Template Broncode

Voor transparantie is de Bicep template open source en beschikbaar op:
https://github.com/yaribouwman/fabriccapacitymonitor/blob/main/onboarding/setup-customer.bicep

U kunt de volledige broncode bekijken voordat u deployt.

## Volgende Stappen

Na het versturen van de credentials:
- Uw consultant voegt u toe aan hun monitoring systeem
- Binnen 15 minuten begint de data collectie
- U ontvangt bevestiging wanneer alles werkt
- U kunt een optionele "Ingest Key" ontvangen voor gedetailleerde CU metrics

## Gerelateerde Documentatie

- [Portal Setup](portal.md) - Azure Portal walkthrough
- [CLI Script Setup](script.md) - Bash script automatisering
- [Klant Handleiding](customer-guide.md) - Overzicht van alle opties
