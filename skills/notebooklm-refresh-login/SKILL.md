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
> Jeśli lokalna sesja jest jeszcze ważna (`list` zwraca notebooki), **wystarczy
> skopiować plik** — nie trzeba ponawiać `notebooklm login`. Interaktywne logowanie
> robisz tylko gdy żywe zapytanie zgłosi wygasłą autoryzację.

> [!warning] `doctor` to za mało — testuj `list`
> `doctor` sprawdza tylko **obecność cookie SID** w pliku, nie wykonuje realnego
> zapytania. Wygasła sesja potrafi dawać **Auth ✓ pass** w `doctor`, a mimo to żywe
> wywołanie przekierowuje na login Google (`Authentication expired or invalid`).
> Rozstrzygający jest dopiero `python -m notebooklm list` — jeśli zwraca notebooki,
> sesja działa; jeśli zgłasza błąd auth, trzeba `notebooklm login`.

## Automatyzacja: nieinteraktywne odświeżanie z Firefoksa (zalecane dla cronów)

Dla serwerów z cyklicznym cronem ręczny `notebooklm login` + SCP co kilka dni można
**całkowicie wyeliminować**. `notebooklm login --browser-cookies <przeglądarka>` czyta
ciasteczka Google wprost z zainstalowanej przeglądarki — **nieinteraktywnie, bez
otwierania okna**. Na desktopie planujesz zadanie, które robi ekstrakcję → żywą
weryfikację → `scp` świeżego pliku na serwer, tuż przed cronem.

> [!warning] Tylko Firefox — Chrome/Edge blokuje App-Bound Encryption
> Chrome i Edge (Chromium 127+) szyfrują ciasteczka **App-Bound Encryption** →
> `Could not decrypt`. Kotwicą musi być **Firefox** zalogowany do Google (zostaje
> zalogowany miesiącami). Zależność: `pip install rookiepy` (na Pythonie 3.14 build
> wymaga `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` — PyO3 0.20 wspiera ≤3.12).

```powershell
# 1. ekstrakcja z Firefoksa do pliku tymczasowego (nieinteraktywna)
python -m notebooklm login --browser-cookies firefox --storage <tmp>
# 2. zywa weryfikacja (list, nie doctor)
python -m notebooklm --storage <tmp> list --json
# 3. wypchniecie na serwer
scp <tmp> <serwer>:/root/.notebooklm/profiles/default/storage_state.json
```

Wtedy ręczna procedura niżej staje się **fallbackiem** — potrzebnym tylko gdy Google
wyloguje kotwicę z Firefoksa (rzadko). Wdrożony przykład (Mikrus, Windows Task
Scheduler 21:40, skrypt `notebooklm-refresh-push.ps1`): zob. `[[Daily digest - Mikrus]]`
→ sekcja „Trwałe odświeżanie sesji".

## Kiedy użyć

- Cron/skrypt na serwerze z `--summarizer notebooklm` (lub innym wywołaniem CLI) pada
  z błędem autoryzacji / „wygasła sesja".
- Po reinstalacji środowiska na serwerze (świeży profil bez `storage_state.json`).
- Profilaktycznie, gdy sesja Google jest bliska wygaśnięcia.
- **Jednorazowy bootstrap** automatyzacji z Firefoksa (sekcja wyżej) — albo gdy
  automat zgłosi, że kotwica FF wygasła i trzeba ją zalogować ponownie.

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

Na **desktopie** zrób **żywy test** — nie polegaj na `doctor` (patrz ostrzeżenie wyżej):

```powershell
python -m notebooklm list --json
```

- **Zwraca notebooki** → sesja ważna, przejdź do kroku 2 (kopiowanie).
- **Błąd auth / „Authentication expired or invalid" / redirect na accounts.google.com**
  → zaloguj się interaktywnie (otwiera przeglądarkę):

  ```powershell
  notebooklm login
  ```

  Po zalogowaniu ponownie `python -m notebooklm list --json`, aż zwróci notebooki.

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
              cd /root && python -m notebooklm list --json'
```

Sukces: rozmiar pliku zgadza się z lokalnym, a `list` **zwraca notebooki** (JSON).
`doctor` możesz odpalić pomocniczo (sprawdzi uprawnienia profilu), ale o ważności
sesji rozstrzyga `list`, nie `doctor`.

## Weryfikacja

Read-only, bez efektów ubocznych — uruchom na serwerze:

```bash
ssh <serwer> 'cd /root && python -m notebooklm list --json'
```

`list` zwraca JSON z notebookami = sesja **realnie** działa zdalnie (to żywe zapytanie,
w przeciwieństwie do `doctor`, który tylko sprawdza obecność cookie). Po tym zdalny
cron/skrypt z `notebooklm-py` autoryzuje się bez błędu.

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
