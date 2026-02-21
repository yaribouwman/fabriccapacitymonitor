# Fabric Capacity Monitor - Klant Onboarding Handleiding

**Van**: [Naam van uw adviesbureau]  
**Voor**: [Naam klantorganisatie]  
**Doel**: Read-only monitoring van uw Microsoft Fabric capaciteit mogelijk maken

---

## Samenvatting

Wij willen uw Microsoft Fabric capaciteit monitoren om proactieve gezondheidsmonitoring en capaciteitsplanning inzichten te bieden. Dit vereist een eenmalige setup (10 minuten) waarbij u ons read-only toegang geeft tot uw capaciteitsmetadata.

**Wat wij kunnen zien:**
- Capaciteitsstatus (Actief, Gepauzeerd, Opgeschort)
- Capaciteits-SKU tier en regio
- Basis resource informatie

**Wat wij NIET kunnen zien:**
- Uw data (lakehouses, warehouses, semantische modellen)
- Fabric artefacten (rapporten, dashboards, notebooks)
- Gebruikersinformatie of workspace inhoud
- Mogelijkheid om resources te wijzigen

**Beveiligingsmodel:**
- Read-only Azure "Reader" rol (geen schrijfrechten)
- Beperkt tot uw specifieke Fabric capaciteit resource
- Controleerbaar in uw Azure Activity Log
- U kunt de toegang op elk moment direct intrekken

---

## Waarom Dit Veilig Is

Deze setup volgt de aanbevolen beveiligingspraktijken van Microsoft:

1. **Minimale Privileges**: Alleen "Reader" rol op uw capaciteit resource (niet subscription-breed)
2. **Single Tenant**: De Service Principal bestaat alleen in uw tenant (niet gedeeld tussen klanten)
3. **Read-Only**: Kan geen Azure resources aanmaken, wijzigen of verwijderen
4. **Geen Data Toegang**: Kan uw werkelijke data of Fabric artefacten niet opvragen
5. **Transparant**: Alle API calls worden gelogd in uw Azure Activity Log
6. **Herroepbaar**: Verwijder de roltoewijzing om toegang direct in te trekken

Dit is hetzelfde patroon dat wordt gebruikt door Azure Managed Service Providers (MSPs) en is goedgekeurd door Azure beveiligingspraktijken.

---

## Setup Opties

Kies de optie die het beste past bij de processen en beveiligingseisen van uw organisatie. Alle drie de opties creëren identieke Service Principals met identieke rechten.

### Optie A: Snelle Portal Setup

**Best voor**: Kleine organisaties, snelle setup, minimale tooling vereisten  
**Benodigde tijd**: 5 minuten  
**Vereisten**: Toegang tot [portal.azure.com](https://portal.azure.com)

[Ga naar Portal Setup Instructies](#optie-a-portal-setup-instructies)

### Optie B: CLI Script

**Best voor**: Middelgrote organisaties, herhaalbare setup, security review  
**Benodigde tijd**: 5 minuten  
**Vereisten**: Azure CLI geïnstalleerd, bash shell

[Ga naar CLI Script Instructies](#optie-b-cli-script-instructies)

### Optie C: Infrastructure as Code (Bicep)

**Best voor**: Enterprise organisaties, change management, audit trails  
**Benodigde tijd**: 10 minuten  
**Vereisten**: Azure CLI, kennis van Bicep/ARM deployments

[Ga naar Bicep IaC Instructies](#optie-c-bicep-iac-instructies)

---

## Optie A: Portal Setup Instructies

### Stap 1: Inloggen op Azure Portal

1. Ga naar [portal.azure.com](https://portal.azure.com)
2. Log in met uw werk account
3. Verifieer dat u in de juiste directory/tenant bent

### Stap 2: Service Principal Aanmaken

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

### Stap 3: Client Secret Aanmaken

1. Klik in het linkermenu op **"Certificates & secrets"**
2. Klik op **"+ New client secret"**
3. Description: `Fabric Monitor Access`
4. Expiration: **24 months** (of uw organisatie beleid)
5. Klik op **"Add"**
6. **KOPIEER DIRECT de Value** - u kunt het nooit meer zien!
   - Ziet eruit als: `abc123~defGHI456...`

### Stap 4: Toegang Verlenen tot Fabric Capaciteit

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

### Stap 5: Resource Informatie Verzamelen

Op uw Fabric capaciteit overzichtspagina, noteer:
- **Subscription ID**: (zichtbaar in het overzicht)
- **Resource Group**: (zichtbaar in het overzicht)
- **Capacity Name**: (de naam waarop u klikte)

### Stap 6: Credentials Versturen naar Uw Consultant

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

---

## Optie B: CLI Script Instructies

### Vereisten

- Azure CLI geïnstalleerd (`az --version`)
- Bash shell (Linux, macOS, WSL, of Git Bash op Windows)
- Azure Administrator of Owner rol op uw Fabric capaciteit

### Stap 1: Download het Script

Download het `setup-customer.sh` script van uw consultant of van de GitHub repository.

### Stap 2: Bekijk het Script

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

### Stap 3: Inloggen op Azure

```bash
az login
```

### Stap 4: Voer het Script Uit

```bash
bash setup-customer.sh
```

Het script vraagt u om:
- **Subscription ID**: Uw Azure subscription ID
- **Capacity Resource ID**: Volledige resource ID van uw Fabric capaciteit (of laat leeg om hele subscription te scannen)

### Stap 5: Bewaar de Output

Het script toont:
- Tenant ID
- Client ID
- Client Secret
- Subscription ID
- Resource ID (indien opgegeven)

**Kopieer deze waarden en stuur ze naar uw consultant via een beveiligd kanaal.**

---

## Optie C: Bicep IaC Instructies

### Vereisten

- Azure CLI geïnstalleerd
- Kennis van Azure Bicep/ARM templates
- Change management proces van uw organisatie

### Stap 1: Download de Bicep Template

Download deze bestanden van uw consultant of GitHub repository:
- `setup-customer.bicep`
- `bicepconfig.json` (optioneel)

### Stap 2: Bekijk de Template

Bekijk de Bicep template om de resources te begrijpen die worden aangemaakt:

```bash
cat setup-customer.bicep
```

De template maakt aan:
1. Azure AD App Registration
2. Service Principal
3. Role assignment (Reader) op de Fabric capaciteit

### Stap 3: Indienen voor Change Management

Als uw organisatie change management vereist voor infrastructuur wijzigingen, dien de Bicep template in via uw standaard goedkeuringsproces.

### Stap 4: Deploy de Template

```bash
az login

az deployment subscription create \
  --location eastus \
  --template-file setup-customer.bicep \
  --parameters appName=FabricCapacityMonitor-ReadOnly \
  --parameters capacityResourceId=/subscriptions/.../Microsoft.Fabric/capacities/...
```

### Stap 5: Haal Deployment Outputs Op

De deployment toont:
- Tenant ID
- Client ID
- Service Principal ID

### Stap 6: Maak Client Secret Handmatig Aan

Bicep kan geen secrets tonen om beveiligingsredenen. Maak het client secret handmatig aan:

1. Ga naar Azure Portal → **Entra ID** → **App registrations**
2. Vind `FabricCapacityMonitor-ReadOnly`
3. Ga naar **Certificates & secrets** → **New client secret**
4. Kopieer de secret waarde

### Stap 7: Verstuur Credentials naar Uw Consultant

Stuur de Tenant ID, Client ID, Client Secret en Subscription ID naar uw consultant via een beveiligd kanaal.

---

## Wat Gebeurt Er Hierna

1. Uw consultant voegt uw organisatie toe aan hun monitoring systeem
2. Binnen 15 minuten bevestigen zij dat de data collectie werkt
3. Zij kunnen een optionele "Ingest Key" verstrekken voor gedetailleerde CU metrics (vereist deployment van een Fabric notebook)
4. Zij zetten monitoring dashboards en alerts op voor uw capaciteit

---

## Optioneel: Gedetailleerde CU Metrics

Voor diepere inzichten in Capacity Unit (CU) gebruik, kunt u optioneel een Fabric notebook deployen die CU metrics naar het monitoring systeem pusht.

**Voordelen:**
- Zie CU gebruik percentages over tijd
- Volg overbelaste minuten en throttling events
- Bewaar metrics langer dan de ingebouwde 14-dagen retentie
- Vergelijk gebruik over meerdere capaciteiten

**Setup:**
1. Uw consultant verstrekt een Python notebook template
2. U deployt het in uw Fabric workspace
3. Plan het om elke 15 minuten te draaien
4. Gebruikt een "Ingest Key" (verstrekt door consultant) voor authenticatie

**Vereisten:**
- Capacity Admin rol in uw Fabric tenant
- 5 minuten om de notebook te deployen

Dit is **optioneel** - de basis monitoring (Tier 1) werkt zonder dit.

---

## Hoe Te Verifiëren Dat Het Werkt

Na 15 minuten:

1. Ga naar Azure Portal → Uw Fabric Capacity → **"Activity log"**
2. Filter op "Operation name" → "List Fabric Capacities"
3. U zou API calls moeten zien van "FabricCapacityMonitor-ReadOnly"

U kunt ook uw consultant vragen om te bevestigen - zij zien uw capaciteit status en SKU in hun dashboard.

---

## Hoe Toegang In Te Trekken

Als u de toegang op enig moment wilt verwijderen:

1. Ga naar Azure Portal → Uw Fabric Capacity
2. Klik op **"Access control (IAM)"**
3. Vind **"FabricCapacityMonitor-ReadOnly"**
4. Klik op **"..."** → **"Remove"**
5. Bevestig verwijdering

**Toegang is direct ingetrokken** - data collectie stopt binnen 15 minuten.

---

## Veelgestelde Vragen

**V: Heeft dit invloed op onze Fabric prestaties?**  
A: Nee. Monitoring gebruikt lichtgewicht Azure API calls (eens per 15 minuten). Geen impact op CU verbruik of query prestaties.

**V: Kunt u onze data zien?**  
A: Nee. Wij zien alleen capaciteits metadata (status, SKU, regio). We hebben geen toegang tot uw lakehouses, warehouses, rapporten of enige werkelijke data.

**V: Hoe weten we wat u toegang heeft?**  
A: Controleer uw Azure Activity Log - alle API calls worden gelogd met timestamps en de Service Principal naam.

**V: Wat als het Client Secret verloopt?**  
A: Wij waarschuwen u als we collectie fouten detecteren. U moet een nieuw secret genereren en naar ons sturen.

**V: Is dit compliant met ons beveiligingsbeleid?**  
A: Dit gebruikt standaard Azure RBAC met minimale privileges. Het is hetzelfde patroon gebruikt door Microsoft partners en MSPs. Controleer met uw beveiligingsteam als u specifieke compliance vereisten heeft.

**V: Welke data bewaart u?**  
A: Wij bewaren: capaciteit status (Actief/Gepauzeerd), SKU tier (F2/F4/F64), Azure regio en timestamps. Als u Tier 3 inschakelt, bewaren we ook CU gebruik percentages en overbelasting events.

**V: Waar wordt de data bewaard?**  
A: In de Azure subscription van uw consultant, in een PostgreSQL database met private networking en encryptie at rest.

**V: Kunnen andere klanten onze data zien?**  
A: Nee. Data is geïsoleerd per klant met database-niveau segregatie. Uw consultant kan en zal klantdata niet delen.

---

## Probleemoplossing

**Probleem: Kan "App registrations" niet vinden**  
**Oplossing**: U heeft mogelijk Azure AD rechten nodig. Neem contact op met uw Global Administrator of Azure AD administrator.

**Probleem: "Access control (IAM)" knop is uitgegrijsd**  
**Oplossing**: U heeft "Owner" of "User Access Administrator" rol nodig op de Fabric capaciteit resource.

**Probleem: Kan de Client Secret waarde niet zien**  
**Oplossing**: Het wordt slechts één keer getoond. Maak een nieuw secret aan als u het gemist heeft.

**Probleem: Weet niet welke Fabric capaciteit te selecteren**  
**Oplossing**: Vraag uw Fabric Administrator of controleer de Fabric Admin Portal voor capaciteit namen.

---

## Contact Uw Consultant

Als u vragen heeft of assistentie nodig heeft:

- **Email**: [your.email@company.com]
- **Telefoon**: [your phone number]
- **Support Portal**: [your support URL]

Wij reageren meestal binnen 4 werkuren.

---

## Document Informatie

**Versie**: 1.0  
**Laatst Bijgewerkt**: Februari 2026  
**Voorbereid door**: [Naam van uw adviesbureau]  
**Geldig voor**: Microsoft Fabric Standard/Premium Capaciteiten

---

**Bedankt voor uw vertrouwen in onze Fabric capaciteit monitoring!**

Zodra u de setup heeft voltooid, stuur ons de credentials via de template hierboven. Wij bevestigen dat alles werkt binnen 1 werkdag.
