#!/usr/bin/env python3
"""
Skript zur Berechnung aller Primzahlen von 1 bis 1.000.000
Verwendet den Sieb des Eratosthenes für optimale Performance.
Speichert Ergebnisse als CSV-Datei aus.
"""

import csv


def prime_sieve(limit):
    """
    Berechnet alle Primzahlen bis zu einer Grenze mit dem Sieb des Eratosthenes.
    
    Parameter:
        limit: Die obere Grenze (inklusive) für die Primzahlberechnung
    
    Rückgabe:
        Liste aller Primzahlen bis zur angegebenen Grenze
    """
    # Initialisiert alle Zahlen als potenziell prim (True)
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False  # 0 und 1 sind keine Primzahlen
    
    # Sieb-Algorithmus
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            # Markiere alle Vielfachen von i als nicht prim
            is_prime[i*i:limit+1:i] = [False] * len(range(i*i, limit+1, i))
    
    # Sammle alle Primzahlen
    return [num for num, prime in enumerate(is_prime) if prime]


def save_to_csv(primes, filename=None):
    """
    Speichert die Primzahlen in einer CSV-Datei.
    
    Parameter:
        primes: Liste der Primzahlen
        filename: Dateiname der CSV-Datei (optional, Standard: 'primzahlen.csv')
    """
    if filename is None:
        filename = "primzahlen.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Kopfzeile hinzufügen
        writer.writerow(['number'])
        
        # Alle Primzahlen in die CSV-Datei schreiben
        for prime in primes:
            writer.writerow([prime])
    
    print(f"\nErgebnisse wurden in '{filename}' gespeichert ({len(primes)} Zeilen)")


def main():
    limit = 1_000_000
    
    print(f"Berechne Primzahlen bis {limit}...")
    
    # Berechnung durchführen
    primes = prime_sieve(limit)
    
    # Ergebnisse anzeigen (Console)
    print(f"\nAnzahl der Primzahlen bis {limit}: {len(primes)}")
    
    if len(primes) <= 20:
        print(f"Primzahlen: {primes}")
    else:
        print(f"Zu erste: {primes[:10]}")
        print(f"... und weitere {len(primes) - 20} Primzahlen bis {limit}")
        print(f"Zu letzte: {primes[-10:]}")
    
    # Ergebnisse als CSV-Datei speichern
    save_to_csv(primes)


if __name__ == "__main__":
    main()
