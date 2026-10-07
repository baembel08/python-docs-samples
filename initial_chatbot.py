import sys
import ollama

def order_chatbot():
    # Definiere den System-Prompt, um dem Bot seine Rolle zuzuweisen
    system_instruction = (
        "Du bist ein freundlicher, digitaler Bestell-Assistent für ein Restaurant. "
        "Deine Aufgabe ist es, Bestellungen von Kunden entgegenzunehmen. "
        "Frage nach den gewünschten Speisen/Getränken und Details (z. B. Größe, Anzahl). "
        "Fasse am Ende die Bestellung kurz zusammen. Antworte immer auf Deutsch und halte dich kurz."
    )

    # Chat-Verlauf initialisieren (System-Anweisung zuerst)
    messages = [
        {"role": "system", "content": system_instruction}
    ]

    print("--- 🤖 Bestell-Chatbot gestartet (Schreibe 'exit' zum Beenden) ---")
    print("Bot: Hallo! Was möchtest du heute bestellen?\n")

    # Erste Begrüßung nicht in den Verlauf, da manuell ausgegeben
    messages.append({"role": "assistant", "content": "Hallo! Was möchtest du heute bestellen?"})

    while True:
        try:
            # Benutzereingabe abfangen
            user_input = input("Du: ")
            
            # Abbruchbedingung
            if user_input.strip().lower() == 'exit':
                print("Bot: Vielen Dank! Auf Wiedersehen.")
                break
                
            if not user_input.strip():
                continue

            # Benutzernachricht dem Verlauf hinzufügen
            messages.append({"role": "user", "content": user_input})

            # Anfrage an die lokale Ollama-Instanz senden
            # Passe das 'model' an, falls du ein anderes nutzt (z.B. 'mistral')
            response = ollama.chat(
                model='gemma4:latest', 
                messages=messages
            )

            # Antwort des Bots extrahieren
            bot_response = response['message']['content']
            
            print(f"Bot: {bot_response}\n")

            # Bot-Antwort dem Verlauf hinzufügen, damit der Kontext erhalten bleibt
            messages.append({"role": "assistant", "content": bot_response})

        except KeyboardInterrupt:
            print("\nBot: Programm abgebrochen. Auf Wiedersehen!")
            sys.exit()
        except Exception as e:
            print(f"\nFehler bei der Kommunikation mit Ollama: {e}")
            print("Stelle sicher, dass Ollama gestartet ist und das Modell geladen wurde.\n")
            break

if __name__ == "__main__":
    order_chatbot()


 
