# Portal Setup (Azure Portal)

**Aanbevolen voor**: Kleine organisaties, snelle setup

**Tijd**: 5 minuten  
**Vereisten**: Toegang tot Azure Portal

Snelle Azure Portal walkthrough - geen command line tools nodig.

## Stap 1: Inloggen op Azure Portal

1. Ga naar [portal.azure.com](https://portal.azure.com)
2. Log in met uw werk account
3. Verifieer dat u in de juiste directory/tenant bent

## Stap 2: Service Principal Aanmaken

1. Zoek naar **"App registrations"** in de zoekbalk bovenaan
2. Klik op **"+ New registration"**
3. Vul in:
   - **Name**: `FabricCapacityMonitor-ReadOnly`
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Laat leeg
4. Klik op **"Register"**

**Wat u ziet**: Een overzichtspagina met twee belangrijke IDs

5. **Kopieer deze waarden** (u heeft ze later nodig):
   - **Application (client) ID**: (ziet eruit als: 12345678-1234-1234-1234-123456789abc)
   - **Directory (tenant) ID**: (ziet eruit als: 87654321-4321-4321-4321-210987654321)

## Stap 3: Client Secret Aanmaken

1. Klik in het linkermenu op **"Certificates & secrets"**
2. Klik op **"+ New client secret"**
3. Description: `Fabric Monitor Access`
4. Expiration: **24 months** (of uw organisatie beleid)
5. Klik op **"Add"**
6. **KOPIEER DIRECT de Value** - u kunt het nooit meer zien!
   - Ziet eruit als: `abc123~defGHI456...`

## Stap 4: Toegang Verlenen tot Fabric Capaciteit

1. Zoek naar **"Fabric capacities"** in Azure Portal
2. Klik op uw capaciteit (bijv. "MyFabricCapacity")
3. Klik op **"Access control (IAM)"** in het linkermenu
4. Klik op **"+ Add"** → **"Add role assignment"**
5. Selecteer **"Reader"** rol → Klik op **"Next"**
6. Klik op **"+ Select members"**
7. Zoek naar: `FabricCapacityMonitor-ReadOnly`
8. Selecteer het → Klik op **"Select"**
9. Klik op **"Review + assign"** (twee keer)

**Verificatie**: U zou "FabricCapacityMonitor-ReadOnly" met "Reader" rol in de lijst moeten zien.

## Stap 5: Resource Informatie Verzamelen

Op uw Fabric capaciteit overzichtspagina, noteer:
- **Subscription ID**: (zichtbaar in het overzicht)
- **Resource Group**: (zichtbaar in het overzicht)
- **Capacity Name**: (de naam waarop u klikte)

## Stap 6: Credentials Versturen naar Uw Consultant

Stuur de volgende informatie via beveiligde email:

```
Onderwerp: Fabric Capacity Monitor Setup - [Uw Bedrijfsnaam]

Hallo [Consultant Naam],

Ik heb de Fabric Capacity Monitor setup voltooid. Hier zijn de credentials:

Organisatie Naam: [Uw Bedrijfsnaam]
Tenant ID: [Van Stap 2]
Client ID: [Van Stap 2]
Client Secret: [Van Stap 3]
Subscription ID: [Van Stap 5]
Resource Group: [Van Stap 5]
Capacity Name: [Van Stap 5]

De Service Principal heeft "Reader" rol op onze Fabric capaciteit.

Met vriendelijke groet,
[Uw Naam]
[Uw Functie]
[Contactinformatie]
```

**Beveiligingstip**: Verstuur via versleutelde email of het beveiligde bestandsdeel systeem van uw organisatie.

## Probleemoplossing

**Probleem: Kan "App registrations" niet vinden**  
**Oplossing**: U heeft mogelijk Azure AD rechten nodig. Neem contact op met uw Global Administrator of Azure AD administrator.

**Probleem: "Access control (IAM)" knop is uitgegrijsd**  
**Oplossing**: U heeft "Owner" of "User Access Administrator" rol nodig op de Fabric capaciteit resource.

**Probleem: Kan de Client Secret waarde niet zien**  
**Oplossing**: Het wordt slechts één keer getoond. Maak een nieuw secret aan als u het gemist heeft.

**Probleem: Weet niet welke Fabric capaciteit te selecteren**  
**Oplossing**: Vraag uw Fabric Administrator of controleer de Fabric Admin Portal voor capaciteit namen.

## Volgende Stappen

Na het versturen van de credentials:
- Uw consultant voegt u toe aan hun monitoring systeem
- Binnen 15 minuten begint de data collectie
- U ontvangt bevestiging wanneer alles werkt
- U kunt een optionele "Ingest Key" ontvangen voor gedetailleerde CU metrics

## Hoe Te Verifiëren Dat Het Werkt

Na 15 minuten:

1. Ga naar Azure Portal → Uw Fabric Capacity → **"Activity log"**
2. Filter op "Operation name" → "List Fabric Capacities"
3. U zou API calls moeten zien van "FabricCapacityMonitor-ReadOnly"

## Hoe Toegang In Te Trekken

Als u de toegang op enig moment wilt verwijderen:

1. Ga naar Azure Portal → Uw Fabric Capacity
2. Klik op **"Access control (IAM)"**
3. Vind **"FabricCapacityMonitor-ReadOnly"**
4. Klik op **"..."** → **"Remove"**
5. Bevestig verwijdering

**Toegang is direct ingetrokken** - data collectie stopt binnen 15 minuten.
