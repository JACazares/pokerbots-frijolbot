import csv
import numpy

with open('my_starting_ranges.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for idx, row in enumerate(reader):
        if idx % 15 != 0 and idx%15 != 1:
            leftrow=numpy.array([float(num) for num in row[1:13]])
            rightrow=numpy.array([float(num) for num in row[1:14]])
            print(idx, leftrow, "........", rightrow)