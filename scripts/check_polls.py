#!/usr/bin/env python3
"""
Poll Watcher - Automatische Umfrage-Überwachung
Prüft dawum.de API auf neue Bundestagswahl-Umfragen und sendet Newsletter via Buttondown.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

# Konfiguration
DAWUM_API = "https://api.dawum.de/"
BUTTONDOWN_API = "https://api.buttondown.email/v1/emails"
DATA_FILE = Path(__file__).parent.parent / "data" / "last-check.json"

# Partei-Mapping
PARTY_NAMES = {
    1: "CDU/CSU",
    2: "SPD",
    3: "Grüne",
    4: "FDP",
    5: "Linke",
    7: "AfD",
    801: "BSW"
}

# Institut-Mapping
INSTITUTE_NAMES = {
    1: "Infratest dimap (ARD)",
    2: "Forsa (RTL/n-tv)",
    3: "Forschungsgruppe Wahlen (ZDF)",
    4: "INSA (BILD)",
    5: "Allensbach (FAZ)",
    6: "GMS",
    8: "Ipsos",
    10: "Verian",
    14: "YouGov"
}


def load_last_state():
    """Lädt den letzten bekannten Stand."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"last_survey_ids": [], "last_check": None}


def save_state(state):
    """Speichert den aktuellen Stand."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch_dawum_data():
    """Holt aktuelle Daten von dawum.de API."""
    try:
        response = requests.get(DAWUM_API, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Fehler beim API-Abruf: {e}")
        return None


def get_bundestag_surveys(data):
    """Filtert Bundestagswahl-Umfragen (Parliament_ID = 0)."""
    if not data or "Surveys" not in data:
        return []
    
    surveys = []
    for survey_id, survey in data["Surveys"].items():
        if survey.get("Parliament_ID") == 0:
            surveys.append({
                "id": survey_id,
                "date": survey.get("Date"),
                "institute_id": survey.get("Institute_ID"),
                "results": survey.get("Results", {})
            })
    
    # Nach Datum sortieren (neueste zuerst)
    surveys.sort(key=lambda x: x["date"], reverse=True)
    return surveys


def format_survey_for_email(survey):
    """Formatiert eine Umfrage für die E-Mail."""
    institute = INSTITUTE_NAMES.get(survey["institute_id"], f"Institut {survey['institute_id']}")
    date = survey["date"]
    
    # Ergebnisse formatieren
    results = []
    for party_id, value in sorted(survey["results"].items(), key=lambda x: -x[1]):
        party_name = PARTY_NAMES.get(int(party_id), f"Partei {party_id}")
        results.append(f"  • {party_name}: {value}%")
    
    return f"""**{institute}** ({date})

{chr(10).join(results)}"""


def send_buttondown_email(new_surveys):
    """Sendet Newsletter via Buttondown API."""
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    
    if not api_key:
        print("WARNUNG: BUTTONDOWN_API_KEY nicht gesetzt. E-Mail wird nicht gesendet.")
        print("Neue Umfragen gefunden:")
        for survey in new_surveys:
            print(format_survey_for_email(survey))
            print("---")
        return False
    
    # E-Mail-Inhalt erstellen
    survey_count = len(new_surveys)
    subject = f"📊 {survey_count} neue Wahlumfrage{'n' if survey_count > 1 else ''}"
    
    body_parts = [
        "# Neue Bundestagswahl-Umfragen\n",
        f"Es {'gibt' if survey_count > 1 else 'gibt'} {survey_count} neue Umfrage{'n' if survey_count > 1 else ''}:\n"
    ]
    
    for survey in new_surveys[:5]:  # Maximal 5 anzeigen
        body_parts.append(format_survey_for_email(survey))
        body_parts.append("\n---\n")
    
    body_parts.append("\n[Alle Umfragen im Poll Watcher ansehen](https://DEIN-USERNAME.github.io/poll-watcher/)\n")
    body_parts.append("\n*Diese E-Mail wurde automatisch generiert.*")
    
    body = "\n".join(body_parts)
    
    # API-Request an Buttondown
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "subject": subject,
        "body": body,
        "status": "draft"  # Erst als Entwurf, dann manuell oder auf "sent" ändern
    }
    
    try:
        response = requests.post(BUTTONDOWN_API, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print(f"✓ Newsletter-Entwurf erstellt: {subject}")
        return True
    except Exception as e:
        print(f"Fehler beim Senden: {e}")
        return False


def main():
    print(f"Poll Watcher Check - {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Letzten Stand laden
    state = load_last_state()
    known_ids = set(state.get("last_survey_ids", []))
    
    print(f"Bekannte Umfragen: {len(known_ids)}")
    
    # Aktuelle Daten holen
    data = fetch_dawum_data()
    if not data:
        print("Keine Daten erhalten. Abbruch.")
        return
    
    # Bundestagswahl-Umfragen filtern
    surveys = get_bundestag_surveys(data)
    print(f"Aktuelle Bundestagswahl-Umfragen: {len(surveys)}")
    
    # Neue Umfragen finden
    current_ids = {s["id"] for s in surveys}
    new_ids = current_ids - known_ids
    
    if new_ids:
        new_surveys = [s for s in surveys if s["id"] in new_ids]
        print(f"\n🆕 {len(new_surveys)} NEUE Umfrage(n) gefunden!")
        
        for survey in new_surveys:
            institute = INSTITUTE_NAMES.get(survey["institute_id"], "Unbekannt")
            print(f"  - {institute} vom {survey['date']}")
        
        # Newsletter senden
        send_buttondown_email(new_surveys)
    else:
        print("\n✓ Keine neuen Umfragen.")
    
    # Stand aktualisieren
    state["last_survey_ids"] = list(current_ids)
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    print(f"\nStand gespeichert. Nächster Check in 2 Stunden.")


if __name__ == "__main__":
    main()
