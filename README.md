# Poll Watcher – Automatische Newsletter-Benachrichtigung

Dieses Repository enthält eine automatische Überwachung für deutsche Wahlumfragen.
Bei neuen Umfragen wird automatisch ein Newsletter via Buttondown versendet.

## 🚀 Einrichtung (10 Minuten)

### Schritt 1: Buttondown Account erstellen

1. Gehe zu [buttondown.email](https://buttondown.email) und erstelle einen kostenlosen Account
2. Notiere deinen **Username** (z.B. `pollwatcher`)
3. Gehe zu **Settings → API** und kopiere deinen **API Key**

### Schritt 2: GitHub Repository einrichten

1. Erstelle ein neues Repository auf GitHub (z.B. `poll-watcher`)
2. Lade alle Dateien aus diesem Ordner hoch:
   ```
   poll-watcher/
   ├── .github/
   │   └── workflows/
   │       └── check-polls.yml
   ├── scripts/
   │   └── check_polls.py
   ├── data/
   │   └── last-check.json
   ├── index.html          ← Deine Poll Watcher App
   └── README.md
   ```

### Schritt 3: GitHub Secret anlegen

1. Gehe zu deinem Repository → **Settings** → **Secrets and variables** → **Actions**
2. Klicke **New repository secret**
3. Name: `BUTTONDOWN_API_KEY`
4. Value: Dein Buttondown API Key
5. Klicke **Add secret**

### Schritt 4: GitHub Actions aktivieren

1. Gehe zu **Actions** Tab in deinem Repository
2. Klicke auf **"I understand my workflows, go ahead and enable them"**
3. Der Workflow läuft nun automatisch alle 2 Stunden

### Schritt 5: Manuell testen

1. Gehe zu **Actions** → **Check for new polls**
2. Klicke **Run workflow** → **Run workflow**
3. Warte ~30 Sekunden und prüfe das Ergebnis

## ⚙️ Konfiguration

### Newsletter sofort versenden (statt Entwurf)

In `scripts/check_polls.py` Zeile 124 ändern:
```python
"status": "sent"  # statt "draft"
```

### Prüfintervall ändern

In `.github/workflows/check-polls.yml` den Cron-Ausdruck anpassen:
```yaml
schedule:
  - cron: '0 */2 * * *'   # Alle 2 Stunden
  - cron: '0 */6 * * *'   # Alle 6 Stunden  
  - cron: '0 8 * * *'     # Täglich um 8 Uhr
```

### Link zur App anpassen

In `scripts/check_polls.py` Zeile 119 deinen GitHub Pages Link eintragen:
```python
"[Alle Umfragen im Poll Watcher ansehen](https://DEIN-USERNAME.github.io/poll-watcher/)"
```

## 📊 So funktioniert es

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions (alle 2 Stunden)                        │
│       ↓                                                  │
│  Python-Skript ruft dawum.de API ab                     │
│       ↓                                                  │
│  Vergleicht mit data/last-check.json                    │
│       ↓                                                  │
│  Wenn NEUE Umfragen:                                    │
│    → Speichert neuen Stand im Repository                │
│    → Sendet Newsletter via Buttondown API               │
│       ↓                                                  │
│  Abonnenten erhalten E-Mail mit neuen Umfragewerten     │
└─────────────────────────────────────────────────────────┘
```

## 💰 Kosten

- **GitHub Actions**: Kostenlos (2.000 Minuten/Monat für private Repos)
- **Buttondown**: Kostenlos bis 100 Abonnenten
- **dawum.de API**: Kostenlos

## 🔧 Fehlerbehebung

### Workflow läuft nicht
- Prüfe ob Actions aktiviert sind (Repository → Actions)
- Prüfe ob der Secret `BUTTONDOWN_API_KEY` korrekt angelegt ist

### Keine E-Mails
- Prüfe Buttondown Dashboard auf Entwürfe
- Ändere `"status": "draft"` zu `"status": "sent"` im Skript

### API-Fehler
- dawum.de könnte temporär nicht erreichbar sein
- Der Workflow versucht es beim nächsten Intervall erneut

## 📝 Lizenz

MIT License – Frei verwendbar
