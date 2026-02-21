# CLI Script Setup

**Aanbevolen voor**: Organisaties die herhaalbare, controleerbare setup willen

**Tijd**: 5 minuten  
**Vereisten**: Azure CLI geïnstalleerd, bash shell

Controleerbaar bash script voor herhaalbare setup met security review.

## Vereisten

- Azure CLI geïnstalleerd (`az --version` om te controleren)
- Bash shell (Linux, macOS, WSL, of Git Bash op Windows)
- Azure Administrator of Owner rol op uw Fabric capaciteit

## Stap 1: Download het Script

Download het `setup-customer.sh` script van uw consultant of van de GitHub repository.

## Stap 2: Bekijk het Script

Voordat u een script uitvoert, bekijk de inhoud:

```bash
cat setup-customer.sh
```

Het script voert deze acties uit:
1. Controleert of Azure CLI geïnstalleerd is en u bent ingelogd
2. Maakt een App Registration aan in uw tenant
3. Maakt een client secret aan
4. Verleent Reader rol op uw Fabric capaciteit
5. Toont de credentials om te delen met uw consultant

## Stap 3: Inloggen op Azure

```bash
az login
```

## Stap 4: Voer het Script Uit

```bash
bash setup-customer.sh
```

Het script vraagt u om:
- **Subscription ID**: Uw Azure subscription ID
- **Capacity Resource ID**: Volledige resource ID van uw Fabric capaciteit (of laat leeg om hele subscription te scannen)

## Stap 5: Bewaar de Output

Het script toont:
- Tenant ID
- Client ID
- Client Secret
- Subscription ID
- Resource ID (indien opgegeven)

**Kopieer deze waarden en stuur ze naar uw consultant via een beveiligd kanaal.**

Voorbeeld output:

```
Setup voltooid!

Stuur deze credentials naar uw consultant:

Organisatie: UwBedrijf
Tenant ID: 12345678-1234-1234-1234-123456789012
Client ID: 87654321-4321-4321-4321-210987654321
Client Secret: abc123~defGHI456...
Subscription ID: aaaabbbb-cccc-dddd-eeee-ffffffffffff
Resource Group: rg-fabric-prod
Capacity Name: fabriccap01

De Service Principal 'FabricCapacityMonitor-ReadOnly' heeft de
'Reader' rol op uw Fabric capaciteit.
```

## Stap 6: Verstuur Credentials naar Uw Consultant

Stuur de output naar uw consultant via beveiligde email of het beveiligde bestandsdeel systeem van uw organisatie.

## Verificatie van de Setup

Controleer of de App Registration is aangemaakt:

```bash
az ad app list --display-name "FabricCapacityMonitor-ReadOnly"
```

Controleer de role assignment:

```bash
az role assignment list \
  --scope /subscriptions/UW_SUBSCRIPTION_ID/resourceGroups/UW_RG/providers/Microsoft.Fabric/capacities/UW_CAPACITY \
  --role "Reader"
```

## Probleemoplossing

**Probleem: Azure CLI niet gevonden**  
**Oplossing**: Installeer Azure CLI van https://docs.microsoft.com/cli/azure/install-azure-cli

**Probleem: Niet ingelogd**  
**Oplossing**: Voer `az login` uit en volg de instructies

**Probleem: Geen toestemming bij het aanmaken van App Registration**  
**Oplossing**: U heeft Azure AD rechten nodig. Neem contact op met uw Global Administrator.

**Probleem: Kan Reader rol niet toewijzen**  
**Oplossing**: U heeft "Owner" of "User Access Administrator" rol nodig op de Fabric capaciteit resource.

**Probleem: Capacity resource niet gevonden**  
**Oplossing**: Verifieer dat de subscription ID en capacity naam correct zijn. U kunt capaciteiten lijsten met:

```bash
az resource list --resource-type "Microsoft.Fabric/capacities"
```

## Hoe Toegang In Te Trekken

Verwijder de role assignment:

```bash
az role assignment delete \
  --assignee <service-principal-id> \
  --scope <capacity-resource-id>
```

Of verwijder de App Registration volledig:

```bash
az ad app delete --id <application-id>
```

## Script Broncode

Voor transparantie is het script open source en beschikbaar op:
https://github.com/yaribouwman/fabriccapacitymonitor/blob/main/onboarding/setup-customer.sh

U kunt de volledige broncode bekijken voordat u het uitvoert.

## Volgende Stappen

Na het versturen van de credentials:
- Uw consultant voegt u toe aan hun monitoring systeem
- Binnen 15 minuten begint de data collectie
- U ontvangt bevestiging wanneer alles werkt
- U kunt een optionele "Ingest Key" ontvangen voor gedetailleerde CU metrics
