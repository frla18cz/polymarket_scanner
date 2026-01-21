# Plán: Zvýraznění Rewards/System Peněženek

## Phase 1: Backend & Database
- [ ] **Task 1: Update Schema**
    - Upravit `ensure_indices` v `main.py`: přidat sloupec `wallet_tag` (TEXT) do tabulky `wallets_stats`.
    - Přidat SQL příkaz, který nastaví `wallet_tag = 'REWARDS'` pro adresu `0xa5ef39c3d3e10d0b270233af41cac69796b12966`.
- [ ] **Task 2: Update API Endpoint**
    - Upravit endpoint `/api/markets/{id}/holders` v `main.py`.
    - Zahrnout sloupec `ws.wallet_tag` do SELECTu a vrátit ho v modelu `HolderDetail`.

## Phase 2: Frontend Implementation
- [ ] **Task 3: Update Holders Table UI**
    - Upravit `frontend_deploy/index.html`.
    - V tabulkách (Mobile Yes/No, Desktop Yes/No) přidat podmíněné zobrazení ikony vedle jména/adresy, pokud `holder.wallet_tag === 'REWARDS'`.
    - Přidat tooltip (pomocí `title` atributu nebo custom tooltipu) s vysvětlujícím textem.

## Phase 3: Verification
- [ ] **Task 4: Verify**
    - Restartovat server (`./dev_local.sh`).
    - Otevřít trh, kde figuruje `0xa5ef...` (např. ten s nejvíce holdery).
    - Ověřit, že se ikona zobrazuje a tooltip funguje.
