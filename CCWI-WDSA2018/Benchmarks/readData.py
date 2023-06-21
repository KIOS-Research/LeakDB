# Read all benchmark data in pandas dataframe.
import os
import re
import pandas as pd

# pip install pandas

def extract_scenario_number(scenario_name):
    match = re.search(r'Scenario-(\d+)', scenario_name)
    if match:
        return int(match.group(1))
    return -1


def read_scenario_data(benchmark, root_folder):
    data_dict = {}

    root_folder = os.path.join(root_folder, benchmark)
    for root, dirs, files in sorted(os.walk(root_folder), key=lambda x: extract_scenario_number(x[0])):
        folder_path = os.path.relpath(root, root_folder)
        folder_name = folder_path.replace(os.sep, '_')
        folder_name = folder_name.replace('-', '_')
        folder_name = folder_name.replace('.', '')
        current_dict = data_dict
        print(folder_path)

        for subfolder in folder_name.split('_'):
            if subfolder:
                if subfolder not in current_dict:
                    current_dict[subfolder] = {}
                current_dict = current_dict[subfolder]

        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                current_dict[file] = df

    return data_dict


G = read_scenario_data('Hanoi_CMH', os.getcwd())
print(G['Scenario'])
# Scenario 1, Demands
print(G['Scenario']['1']['Demands'])
# Scenario 2, Demands
print(G['Scenario']['2']['Demands'])