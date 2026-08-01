import json
import os

# Where the data folder is, relative to this file                                                     
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')  

def load_data(filename):
    """                                                                                          
    Loads data from a JSON file in the data/ directory.                                          
    Creates the directory and file with an empty list if they don't exist.                       
    """                                                                                          
    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    file_path = os.path.join(DATA_DIR, filename)
    
    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(file_path):
        return []
        
    # Read and return the data
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        # If the file is empty or corrupted, return an empty list
        return []

def save_data(filename, data):
    """
    Saves a list of dictionaries (data) to a JSON file.
    """
    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    file_path = os.path.join(DATA_DIR, filename)
    
    # Write the data with indent=4 for human-readable formatting
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
        