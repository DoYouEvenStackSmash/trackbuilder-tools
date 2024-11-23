#!/usr/bin/python3
import json
import os
import sys

def update_image_paths(json_data, path):
    """
    Updates the file paths for images in the given JSON data.
    """
    if not path.endswith('/'):
        path += '/'

    for image in json_data.get('images', []):
        filename = os.path.basename(image['file_name'])
        image['file_name'] = f'{path}{filename}'
    
    return json_data

def main():
    # Check command-line arguments
    if len(sys.argv) < 3:
        print("Usage: script.py <destination_path> <input_file>")
        sys.exit(1)
    
    # Read command-line arguments
    destination_path = sys.argv[1]
    input_file_path = sys.argv[2]

    # Read and parse the JSON file
    try:
        with open(input_file_path, 'r') as input_file:
            data = json.load(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{input_file_path}'.")
        sys.exit(1)

    # Update the image paths
    updated_data = update_image_paths(data, destination_path)

    # Output the updated JSON
    print(json.dumps(updated_data, indent=2))

if __name__ == '__main__':
    main()
