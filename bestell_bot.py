import sys
import json
import random
import ollama

# Name der JSON-Datenbank
DB_FILE = "bestellstatus_bottest.json"

# ==========================================
# 1. DIE LOKALEN PYTHON-FUNKTIONEN (TOOLS)
# ==========================================

def hole_bestellstatus(bestell_id: str) -> str:
    """Sucht den Status einer Bestellung anhand der Bestell-ID in der JSON-Datei."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            daten = json.load(f)
        
        if bestell_id in daten:
            info = daten[bestell_id]
            return f"Bestellung {bestell_id}: Status ist '{info['status']}'. Artikel: {info['artikel']}, Datum: {info['datum']}."
        else:
            return f"Die Bestell-ID {bestell_id} wurde nicht gefunden."
    except FileNotFoundError:
        # Falls die Datei noch nicht existiert, erstellen wir eine leere Struktur
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return f"Die Bestell-ID {bestell_id} wurde nicht gefunden (Datenbank war leer)."

def speichere_neue_bestellung(artikel_zusammenfassung: str) -> str:
    """Speichert eine neu aufgenommene Bestellung in der JSON-Datei und generiert eine ID."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            daten = json.load(f)
    except FileNotFoundError:
        daten = {}

    # Generiere eine neue ID (z.B. DE-1001, DE-1002...)
    existierende_ids = [int(id.split("-")[1]) for id in daten.keys() if id.startswith("DE-")]
    naechste_nummer = max(existierende_ids) + 1 if existierende_ids else 1001
    neue_id = f"DE-{naechste_nummer}"

    # Importiere Datum für den Eintrag
    from datetime import datetime
    heute = datetime.today().strftime('%Y-%m-%d')

    # Neuen Eintrag erstellen
    daten[neue_id] = {
        "artikel": artikel_zusammenfassung,
        "status": "In Bearbeitung",
        "datum": heute
    }

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=4)

    return f"Erfolg: Bestellung wurde unter der ID {neue_id} gespeichert. Status: 'In Bearbeitung'."

# ==========================================
# 2. TOOL-DEFINITIONEN FÜR DAS LLM (SCHEMATA)
# ==========================================

tool_status = {
    'type': 'function',
    'function': {
        'name': 'hole_bestellstatus',
        'description': 'Holt den aktuellen Status und Details einer bestehenden Bestellung aus der Datenbank mithilfe der Bestell-ID (z.B. DE-1001).',
        'parameters': {
            'type': 'object',
            'properties': {
                'bestell_id': {
                    'type': 'string',
                    'description': 'Die genaue ID der Bestellung, z.B. DE-1001',
                },
            },
            'required': ['bestell_id'],
        },
    },
}

tool_speichern = {
    'type': 'function',
    'function': {
        'name': 'speichere_neue_bestellung',
        'description': 'Speichert eine fertig aufgenommene Bestellung in der Datenbank, sobald der Kunde alle Details (Speisen, Getränke, Anzahl) genannt hat und bestellen möchte.',
        'parameters': {
            'type': 'object',
            'properties': {
                'artikel_zusammenfassung': {
                    'type': 'string',
                    'description': 'Kurze Zusammenfassung der Bestellung, z.B. "1x Pizza Margherita, 2x Cola"',
                },
            },
            'required': ['artikel_zusammenfassung'],
        },
    },
}

ALL_TOOLS = [tool_status, tool_speichern]

# ==========================================
# 3. INTERAKTIVE CHAT-SCHLEIFE
# ==========================================

def order_chatbot():
    modell_name = 'gemma4:latest'
    
    system_instruction = (
        "Du bist ein freundlicher, digitaler Bestell-Assistent für ein Restaurant. "
        "Deine Aufgaben:\n"
        "1. Bestellungen aufnehmen: Frage nach Speisen/Getränken und Details (Größe, Anzahl). Wenn der Kunde fertig ist, "
        "nutze das Tool 'speichere_neue_bestellung', um sie abzuspeichern. Nenne dem Kunden danach unbedingt die generierte ID!\n"
        "2. Status abfragen: Wenn ein Kunde nach einer bestehenden Bestellung fragt (z.B. DE-1001), nutze das Tool 'hole_bestellstatus'.\n"
        "Antworte immer auf Deutsch und halte dich kurz."
    )

    messages = [
        {"role": "system", "content": system_instruction}
    ]

    print("--- 🤖 Bestell- & Status-Chatbot gestartet (Schreibe 'exit' zum Beenden) ---")
    print("Bot: Hallo! Möchtest du etwas bestellen oder den Status einer Bestellung abfragen?\n")

    messages.append({"role": "assistant", "content": "Hallo! Möchtest du etwas bestellen oder den Status einer Bestellung abfragen?"})

    while True:
        try:
            user_input = input("Du: ")
            
            if user_input.strip().lower() == 'exit':
                print("Bot: Vielen Dank! Auf Wiedersehen.")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            # Erster Aufruf: Prüfen, ob das LLM ein Tool triggern will
            response = ollama.chat(
                model=modell_name,
                messages=messages,
                tools=ALL_TOOLS
            )

            # Falls das Modell ein Tool aufrufen möchte
            if response.get('message', {}).get('tool_calls'):
                messages.append(response['message'])
                
                for tool_call in response['message']['tool_calls']:
                    funk_name = tool_call['function']['name']
                    argumente = tool_call['function']['arguments']
                    tool_ergebnis = ""

                    if funk_name == 'hole_bestellstatus':
                        gesuchte_id = argumente.get('bestell_id')
                        tool_ergebnis = hole_bestellstatus(gesuchte_id)
                        
                    elif funk_name == 'speichere_neue_bestellung':
                        zusammenfassung = argumente.get('artikel_zusammenfassung')
                        tool_ergebnis = speichere_neue_bestellung(zusammenfassung)

                    # Tool-Ergebnis in den Verlauf einspeisen
                    messages.append({
                        'role': 'tool',
                        'content': tool_ergebnis,
                        'name': funk_name
                    })
                
                # Zweiter Aufruf: Finale Antwort für den Nutzer generieren lassen
                finale_response = ollama.chat(model=modell_name, messages=messages)
                bot_response = finale_response['message']['content']
            else:
                # Normale Konversation ohne Tool-Einsatz
                bot_response = response['message']['content']
            
            print(f"Bot: {bot_response}\n")
            messages.append({"role": "assistant", "content": bot_response})

        except KeyboardInterrupt:
            print("\nBot: Programm abgebrochen. Auf Wiedersehen!")
            sys.exit()
        except Exception as e:
            print(f"\nFehler: {e}")
            print("Stelle sicher, dass Ollama läuft und das Modell installiert ist.\n")
            break

if __name__ == "__main__":
    order_chatbot()



json sample script

{
    "DE-1001": {
        "status": "Versandt",
        "datum": "2026-10-01",
        "artikel": "Laptop"
    },
    "DE-1002": {
        "status": "In Bearbeitung",
        "datum": "2026-10-05",
        "artikel": "Smartphone"
    },
    "DE-1003": {
        "status": "Zugestellt",
        "datum": "2026-09-28",
        "artikel": "Kopfhörer"
    },
    "DE-1004": {
        "artikel": "2x große Tomaten",
        "status": "In Bearbeitung",
        "datum": "2026-10-06"
    },
    "DE-1005": {
        "artikel": "2x Matcha Latte (gerührt)",
        "status": "fertig",
        "datum": "2026-10-06"
    }
}
