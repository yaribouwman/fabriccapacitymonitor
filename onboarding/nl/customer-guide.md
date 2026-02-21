# Fabric Capacity Monitor - Klant Onboarding Handleiding

**Van**: [Naam van uw adviesbureau]  
**Voor**: [Naam klantorganisatie]  
**Doel**: Read-only monitoring van uw Microsoft Fabric capaciteit mogelijk maken

---

## Samenvatting

Wij willen uw Microsoft Fabric capaciteit monitoren om proactieve gezondheidsmonitoring en capaciteitsplanning inzichten te bieden. Dit vereist een eenmalige setup (5-10 minuten) waarbij u ons read-only toegang geeft tot uw capaciteitsmetadata.

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

### Portal Setup (Aanbevolen voor de Meesten)

**Voor**: Kleine organisaties, snelle setup

Snelle Azure Portal walkthrough. Geen command line tools nodig.  
→ [Portal Setup Handleiding](portal.md)

### CLI Script Setup

**Voor**: Organisaties die herhaalbare, controleerbare setup willen

Bash script dat het setup proces automatiseert.  
→ [CLI Script Handleiding](script.md)

### Infrastructure as Code (Bicep)

**Voor**: Enterprises met change management vereisten

Deploy met Bicep template voor volledige audit trail.  
→ [IaC Setup Handleiding](iac.md)

---

## Snelle Vergelijking

| Functie | Portal | CLI Script | Bicep IaC |
|---------|--------|------------|-----------|
| Setup Tijd | 5 min | 5 min | 10 min |
| Command Line Vereist | Nee | Ja | Ja |
| Audit Trail | Handmatig | Script logs | Volledig IaC |
| Change Management | Nee | Optioneel | Ja |
| Best Voor | Snelle setup | Herhaalbaar | Enterprise |

---

## Wat Gebeurt Er Hierna

Na het voltooien van de setup:

1. **Verstuur credentials** naar uw consultant via beveiligde email
2. **Wacht 15 minuten** - Uw consultant voegt u toe aan hun monitoring systeem
3. **Ontvang bevestiging** - Data collectie begint automatisch
4. **Optioneel**: U kunt een "Ingest Key" ontvangen voor gedetailleerde CU metrics

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

Dit is **optioneel** - de basis monitoring werkt zonder dit.

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
A: Wij bewaren: capaciteit status (Actief/Gepauzeerd), SKU tier (F2/F4/F64), Azure regio en timestamps. Als u optionele CU metrics inschakelt, bewaren we ook gebruik percentages en overbelasting events.

**V: Waar wordt de data bewaard?**  
A: In de Azure subscription van uw consultant, in een PostgreSQL database met private networking en encryptie at rest.

**V: Kunnen andere klanten onze data zien?**  
A: Nee. Data is geïsoleerd per klant met database-niveau segregatie. Uw consultant kan en zal klantdata niet delen.

---

## Contact Uw Consultant

Als u vragen heeft of assistentie nodig heeft:

- **Email**: [your.email@company.com]
- **Telefoon**: [your phone number]
- **Support Portal**: [your support URL]

Wij reageren meestal binnen 4 werkuren.

---

**Bedankt voor uw vertrouwen in onze Fabric capaciteit monitoring!**

Zodra u de setup heeft voltooid, stuur ons de credentials. Wij bevestigen dat alles werkt binnen 1 werkdag.
