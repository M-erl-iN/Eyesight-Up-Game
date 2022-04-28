import csv

with open('level.csv', 'w', newline='', encoding='utf8') as csvfile:
    writer = csv.writer(
        csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows([(1, 3, 3, 0, 2, 1, 10, 2, 2, 480, 600), (1, 3, 3, 0, 2, 1, 10, 2, 2, 480, 600, 0.5, 2, 2)])
