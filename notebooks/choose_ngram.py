#!/usr/bin/env python3
"""
Outil d'annotation de n-grammes (bigrammes/trigrammes) en ligne de commande.
Pour chaque ligne d'un CSV, demande si l'association est pertinente (o/n).
Enregistre uniquement les lignes validées dans un nouveau CSV.
"""

import csv
import sys
import os
import argparse
from pathlib import Path


def detect_columns(header):
    """Détecte les colonnes mot et fréquence dans l'en-tête."""
    header_lower = [h.lower().strip() for h in header]
    freq_col = None
    word_cols = []

    for i, h in enumerate(header_lower):
        if h in ('freq', 'frequency', 'fréquence', 'frequence', 'count', 'nb', 'n'):
            freq_col = i
        else:
            word_cols.append(i)

    return word_cols, freq_col


def format_row(row, word_cols, freq_col, header):
    """Formate une ligne pour l'affichage."""
    parts = []
    if word_cols:
        words = [row[i] for i in word_cols if i < len(row)]
        parts.append(" + ".join(words))
    if freq_col is not None and freq_col < len(row):
        parts.append(f"(freq: {row[freq_col]})")
    return "  ".join(parts) if parts else "  ".join(row)


def process_file(input_path):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"[ERREUR] Fichier introuvable : {input_path}")
        return

    # Nom du fichier de sortie
    output_path = input_path.parent / f"{input_path.stem}_annotated{input_path.suffix}"

    print(f"\n{'='*60}")
    print(f"Fichier : {input_path.name}")
    print(f"Sortie  : {output_path.name}")
    print(f"{'='*60}")
    print("  [o] = pertinent   [n] = non pertinent   [q] = quitter\n")

    try:
        with open(input_path, newline='', encoding='utf-8-sig') as f:
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(f, dialect)
            rows = list(reader)
    except Exception as e:
        print(f"[ERREUR] Impossible de lire le fichier : {e}")
        return

    if not rows:
        print("[INFO] Fichier vide.")
        return

    header = rows[0]
    data_rows = rows[1:]
    word_cols, freq_col = detect_columns(header)

    accepted = []
    total = len(data_rows)
    skipped = 0

    for idx, row in enumerate(data_rows, 1):
        if not any(cell.strip() for cell in row):
            continue  # ignore lignes vides

        display = format_row(row, word_cols, freq_col, header)
        prompt = f"[{idx}/{total}] {display}  → "

        while True:
            try:
                answer = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n\n[INTERRUPTION] Enregistrement partiel...")
                answer = 'q'

            if answer in ('o', 'oui', 'y', 'yes'):
                accepted.append(row)
                break
            elif answer in ('n', 'non', 'no'):
                skipped += 1
                break
            elif answer == 'q':
                print(f"\n[INFO] Annotation interrompue à la ligne {idx}/{total}.")
                # Sauvegarder quand même ce qui a été fait
                _save(output_path, header, accepted, dialect)
                print(f"[INFO] {len(accepted)} entrées sauvegardées dans {output_path.name}")
                return
            else:
                print("        → Tapez 'o' (oui) ou 'n' (non), 'q' pour quitter.")

    _save(output_path, header, accepted, dialect)
    print(f"\n{'='*60}")
    print(f"Terminé ! {len(accepted)}/{total} entrées acceptées.")
    print(f"Fichier enregistré : {output_path}")
    print(f"{'='*60}\n")


def _save(output_path, header, rows, dialect):
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, dialect=dialect)
            writer.writerow(header)
            writer.writerows(rows)
    except Exception as e:
        print(f"[ERREUR] Impossible d'enregistrer : {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Annotation interactive de n-grammes CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python annotate_ngrams.py bigrammes.csv
  python annotate_ngrams.py bigrammes.csv trigrammes.csv
  python annotate_ngrams.py *.csv
        """
    )
    parser.add_argument('files', nargs='+', help='Fichier(s) CSV à annoter')
    args = parser.parse_args()

    for filepath in args.files:
        process_file(filepath)

    print("Tous les fichiers ont été traités.")


if __name__ == '__main__':
    main()
