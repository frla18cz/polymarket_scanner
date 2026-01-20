# Datové anomálie a známé adresy

Tento dokument slouží k evidenci adres a jevů v datech z Polymarketu/Goldsky, které mohou zkreslovat analytické metriky (zejména Smart Money).

## Identifikované systémové adresy (K odfiltrování)

Tyto adresy drží velké objemy tokenů z technických důvodů (odměny, likvidita) a jejich "PnL" nebo "Win Rate" nereprezentuje skutečný názor trhu.

| Adresa | Název/Účel | Poznámka |
| :--- | :--- | :--- |
| `0xa5ef39c3d3e10d0b270233af41cac69796b12966` | **Polymarket: Rewards** | Slouží k distribuci odměn uživatelům. Identifikováno 20.1.2026. |

## Pozorované jevy
- **Ghost Holders:** Některé adresy s obrovským balance se neobjevují v oficiálním top-listu Polymarketu (odfiltrováno jejich UI).
- **Outcome Mismatch:** Indexy outcome (0, 1) v surových datech musí být vždy pečlivě mapovány na "Yes"/"No", aby nedošlo k záměně držitelů.
