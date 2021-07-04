# Python program to convert
# JSON file to CSV
 
 
import json
import csv
import ast

 
 
# Opening JSON file and loading the data
# into the variable data
# with open('/home/dishant/Downloads/crypto.txt') as json_file:
#    data = json.load(json_file)

file = open("/home/dishant/Downloads/aa_out_BTC.txt", "r")
csv_columns = ['id', 'isBuyerMaker', 'quoteQty', 'isBestMatch','price', 'qty', 'time']

contents = file.read()

dictionary = ast.literal_eval(contents)

file.close()

#req_data = dictionary['symbols']
#print(req_data)
# now we will open a file for writing
csv_file = "/home/dishant/Downloads/Names.csv"
 
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dictionary:
            writer.writerow(data)
except IOError:
    print("I/O error")
 