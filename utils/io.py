import csv

def read_csv_as_objects(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            data_object = {headers[i]: row[i] for i in range(len(headers))}
            yield data_object