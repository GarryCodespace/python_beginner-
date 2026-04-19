import csv


def load_csv(file_path):
    data = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            data.append(row)

    return data


def search_rows(data, column, value):
    results = []

    for row in data:
        if row[column] == value:
            results.append(row)

    return results


def filter_greater_than(data, column, threshold):
    results = []

    for row in data:
        try:
            if float(row[column]) > threshold:
                results.append(row)
        except:
            pass

    return results


def compute_average(data, column):
    total = 0
    count = 0

    for row in data:
        try:
            total += float(row[column])
            count += 1
        except:
            pass

    if count == 0:
        return 0

    return total / count


def sort_data(data, column):
    try:
        return sorted(data, key=lambda x: float(x[column]))
    except:
        return sorted(data, key=lambda x: x[column])


def export_csv(data, output_file):
    if not data:
        return

    keys = data[0].keys()

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


# ---- RUN ----
file_path = "data.csv"
data = load_csv(file_path)

print("Loaded rows:", len(data))

# Example usage
filtered = filter_greater_than(data, "age", 25)
print("Filtered rows:", len(filtered))

avg = compute_average(data, "age")
print("Average age:", avg)

sorted_data = sort_data(data, "age")

export_csv(filtered, "filtered.csv")
