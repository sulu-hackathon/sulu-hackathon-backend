# Define the path to your file
file_path = 'pages_ids.txt'

# Initialize an empty dictionary
data_dict = {}

# Open and read the file
with open(file_path, 'r') as file:
    for line in file:
        # Strip whitespace and split each line by the colon
        if ':' in line:
            value, key = line.strip().split(': ')
            data_dict[value] = key

print(data_dict)
