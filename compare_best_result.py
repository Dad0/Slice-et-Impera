"""
Script che mi è stato utile per vedere le differenze tra le varie sub caricate su Kaggle
"""

import os
import csv

def compare_csv_sets(csv_path1, csv_path2):
    def load_csv_to_set(csv_path):
        data = {}
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Salta l'header
            for row in reader:
                row_id = row[0]
                print(row)
                numbers = set(map(str.strip, row[1].strip('"').split(',')))
                data[row_id] = numbers
        return data

    data1 = load_csv_to_set(csv_path1)
    data2 = load_csv_to_set(csv_path2)

    diff_records = []

    all_keys = set(data1.keys()) | set(data2.keys())
    for key in all_keys:
        set1 = data1.get(key, set())
        set2 = data2.get(key, set())
        if set1 ^ set2:  # Confronto con XOR
            diff_records.append([key, ', '.join(set1), ', '.join(set2)])

    if diff_records:
        diff_filename = f"{os.path.basename(csv_path1).replace('.csv', '')}_"
        diff_filename += f"{os.path.basename(csv_path2).replace('.csv', '')}_diff.csv"

        with open(diff_filename, 'w', newline='', encoding='utf-8') as diff_file:
            writer = csv.writer(diff_file)
            writer.writerow(["row_id", "csv1_values", "csv2_values"])
            writer.writerows(diff_records)
        print(f"Differenze salvate in: {diff_filename}")
    else:
        print("Nessuna differenza trovata.")

best_result = "PATH"
current_result = "PATH"
# Esempio di utilizzo
compare_csv_sets(best_result, current_result)

