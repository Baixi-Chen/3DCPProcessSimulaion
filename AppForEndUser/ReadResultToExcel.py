import csv
import math
from odbAccess import *

# Read the required details from 'req.txt'
with open('req.txt', 'r') as file:
    odb_directory = file.readline().strip()  # Path of the odb directory
    odb_file_name = file.readline().strip()  # Name of the odb file
    csv_directory = file.readline().strip()  # Directory to save the csv file

# Construct full paths for ODB and CSV files
odb_path = odb_directory + '\\' + odb_file_name + '.odb'
csv_file_path = csv_directory + '\\' + odb_file_name + '-Results.csv'

# Open the ODB file
odb = openOdb(odb_path)

# List to store the data
results_data = []

# Function to calculate horizontal displacement
def calculate_horizontal_disp(x, y):
    return math.sqrt(x**2 + y**2)

# Loop through each step
for step_name in odb.steps.keys():
    step = odb.steps[step_name]

    # Check if there are frames in the step
    if not step.frames:
        print("No frames in step '{}'. Skipping this step.".format(step_name))
        continue

    # Get the last frame of the step
    last_frame = step.frames[-1]
    total_time = last_frame.frameValue

    max_horizontal_disp = float('-inf')
    min_vertical_disp = float('inf')
    max_peeq = float('-inf')
    max_mises_stress = float('-inf')

    # Check and calculate displacements and PEEQ
    if 'U' in last_frame.fieldOutputs and 'PEEQ' in last_frame.fieldOutputs:
        for value in last_frame.fieldOutputs['U'].values:
            horizontal_disp = calculate_horizontal_disp(value.data[0], value.data[1])
            max_horizontal_disp = max(max_horizontal_disp, horizontal_disp)
            min_vertical_disp = min(min_vertical_disp, value.data[2])

        for value in last_frame.fieldOutputs['PEEQ'].values:
            max_peeq = max(max_peeq, value.data)

        for value in last_frame.fieldOutputs['S'].values:
            mises_stress = value.mises
            max_mises_stress = max(max_mises_stress, mises_stress)

    if max_horizontal_disp == float('-inf') or min_vertical_disp == float('inf') or max_peeq == float(
            '-inf') or max_mises_stress == float('-inf'):
        print("Incomplete data in last frame of step '{}'.".format(step_name))
    else:
        results_data.append([step_name, total_time, max_horizontal_disp, min_vertical_disp, max_peeq, max_mises_stress])

odb.close()

# Write data to a CSV file
with open(csv_file_path, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(
        ['Step', 'Time at Last Frame', 'Max Horizontal Displacement', 'Min Vertical Displacement', 'Max PEEQ',
         'Max Mises Stress'])
    writer.writerows(results_data)

print("Results data saved to {}".format(csv_file_path))
