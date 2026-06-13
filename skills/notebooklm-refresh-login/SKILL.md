---
name: notebooklm-refresh-login
description: 'Odswieza wygasla sesje Google NotebookLM na zdalnym/headless serwerze (VPS, kontener, CI) przez przeniesienie pliku sesji storage_state.json z lokalnego desktopu — bez interaktywnego logowania na serwerze, ktory tam nie ma przegladarki. Uzywaj gdy uzytkownik prosi "odswiez poswiadczenia notebooklm na serwerze", "zaloguj notebooklm na VPS/mikrusie", "skopiuj sesje notebooklm na serwer", albo gdy zdalny skrypt/cron z notebooklm-py konczy sie bledem autoryzacji (wygasla sesja, brak SID cookie). Rozszerzenie notebooklm-setup dla srodowisk zdalnych.'
---

# notebooklm-refresh-login

Przenosi **świeżą sesję Google** NotebookLM z desktopu (gdzie da się otworzyć
przeglądarkę) na **zdalny serwer** (VPS, kontener, headless CI), gdzie automat
`notebooklm-py` woła `python -m notebooklm` z crona lub skryptu.

## Po co to istnieje

`notebooklm login` jest **interaktywne** — otwiera przeglądarkę i wymaga zalogowania
kontem Google. Na headless serwerze nie ma przeglądarki, więc logowania **nie da się
tam wykonać**. Rozwiązanie: zalogować się raz na desktopie, a potem przegrać sam plik
sesji (`storage_state.json`) na serwer. CLI po obu stronach jest identyczne, więc
serwer używa tej samej, ważnej sesji.

> [!important] Pełne logowanie zwykle nie jest potrzebne
> Jeśli lokalna sesja jest jeszcze ważna (`doctor` → Auth ✓), **wystarczy skopiować
> plik** — nie trzeba ponawiać `notebooklm login`. Interaktywne logowanie robisz tylko
> gdy lokalny `doctor` zgłosi wygasłą autoryzację.

## Kiedy użyć

- Cron/skrypt na serwerze z `--summarizer notebooklm` (lub innym wywołaniem CLI) pada
  z błędem autoryzacji / „wygasła sesja".
- Po reinstalacji środowiska na serwerze (świeży profil bez `storage_state.json`).
- Profilaktycznie, gdy sesja Google jest bliska wygaśnięcia.

## Lokalizacja pliku sesji

Domyślny profil `notebooklm-py`:

| System | Ścieżka |
|--------|---------|
| Desktop (Windows) | `C:\Users\<user>\.notebooklm\profiles\<profil>\storage_state.json` |
| Desktop (macOS/Linux) | `~/.notebooklm/profiles/<profil>/storage_state.json` |
| Serwer (root) | `/root/.notebooklm/profiles/<profil>/storage_state.json` |

Profil domyślny to `default`. Jeśli używasz innego — `python -m notebooklm profile list`.

## Procedura

### 1. Sprawdź i (jeśli trzeba) odśwież lokalną sesję

Na **desktopie**:

```powershell
python -m notebooklm doctor
```

- **Auth ✓ pass** → sesja ważna, przejdź do kroku 2 (kopiowanie).
- **Auth błąd / wygasła** → zaloguj się interaktywnie (otwiera przeglądarkę):

  ```powershell
  notebooklm login
  ```

  Po zalogowaniu ponownie `python -m notebooklm doctor`, aż Auth ✓.

Logowania **nie wykonuje się za użytkownika** — jeśli wymagane, poproś go, by sam
uruchomił `notebooklm login`.

### 2. Ustal ścieżkę lokalnego pliku

```powershell
# Windows
Get-ChildItem "$env:USERPROFILE\.notebooklm\profiles\default\storage_state.json" |
  Select-Object FullName, LastWriteTime, Length
```

Zanotuj rozmiar i datę — przydadzą się do weryfikacji po stronie serwera.

### 3. Zrób backup pliku na serwerze (jeśli istnieje)

Zanim nadpiszesz — zabezpiecz dotychczasowy plik. Przez SSH:

```bash
ssh <serwer> 'mkdir -p /root/.notebooklm/profiles/default; \
  [ -f /root/.notebooklm/profiles/default/storage_state.json ] && \
  cp /root/.notebooklm/profiles/default/storage_state.json \
     /root/.notebooklm/profiles/default/storage_state.json.bak-$(date +%Y%m%d) \
  && echo BACKUP_DONE || echo NO_EXISTING_FILE'
```

### 4. Skopiuj świeży plik na serwer

`scp` (najprościej) lub `rsync`:

```powershell
scp "$env:USERPROFILE\.notebooklm\profiles\default\storage_state.json" `
    <serwer>:/root/.notebooklm/profiles/default/storage_state.json
```

> [!tip] Osobne, czyste połączenie jest pewniejsze
> Jeśli zdalna powłoka bywa wolna (mały VPS, kontener pod presją RAM), długie
> sesje SSH z wieloetapowymi komendami potrafią się zawiesić. `scp` nawiązuje
> własne, krótkie połączenie i jest odporniejszy.

`scp` nadpisuje samą treść istniejącego pliku, zachowując jego uprawnienia — przy
odświeżeniu nie trzeba ich ustawiać ponownie (patrz uwaga o uprawnieniach niżej).

### 5. Zweryfikuj po stronie serwera

```bash
ssh <serwer> 'ls -la /root/.notebooklm/profiles/default/storage_state.json; \
              cd /root && python -m notebooklm doctor'
```

Sukces: rozmiar pliku zgadza się z lokalnym, a `doctor` pokazuje **Auth ✓ pass**
i **All checks passed**.

## Weryfikacja

Read-only, bez efektów ubocznych — uruchom na serwerze:

```bash
ssh <serwer> 'cd /root && python -m notebooklm doctor && python -m notebooklm list --json'
```

`doctor` bez błędu auth + `list` zwraca JSON z notebookami = sesja działa zdalnie.
Po tym zdalny cron/skrypt z `notebooklm-py` autoryzuje się bez błędu.

## Uwagi

- **Uprawnienia ustawiasz raz.** `notebooklm-py` oczekuje katalogu `0700` i pliku
  `0600`. Dotyczy to tylko **pierwszej** konfiguracji świeżego profilu na serwerze:
  ```bash
  ssh <serwer> 'chmod 700 /root/.notebooklm/profiles/default && \
                chmod 600 /root/.notebooklm/profiles/default/storage_state.json'
  ```
  Przy kolejnych odświeżeniach `scp` zachowuje uprawnienia istniejącego pliku, więc
  ten krok jest zbędny.
- `storage_state.json` to **poświadczenie sesji Google** — traktuj jak sekret. Nie
  commituj go, nie wrzucaj do logów, przesyłaj tylko zaufanym kanałem (SSH/SCP).
- Sesja w końcu wygasa — gdy zdalny `doctor` znów zgłosi błąd auth, powtórz procedurę.
- Logowania nie wykonujemy za użytkownika (konto Google, interaktywne) — patrz
  `[[notebooklm-setup]]`.
- Nie wysyłaj do NotebookLM treści poufnych/wrażliwych (hasła, dane osobowe, sekrety).
