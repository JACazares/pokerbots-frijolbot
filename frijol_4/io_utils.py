import csv

def read_csv_table(filename):
    """Reads a CSV file and returns a dictionary mapping a tuple of the first columns to the last column."""
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        table = {tuple(row[:-1]): row[-1] for row in reader}

    return table