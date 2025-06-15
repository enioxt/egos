# @references:
#   - subsystems/KOIOS/schemas/validate_pdd.py
# 
# validate_pdd.py
# Description: Validates a Prompt Design Document (PDD) YAML file against the PddSchema.
# Requirements: PyYAML, Pydantic (pip install pyyaml pydantic)
# Usage: python validate_pdd.py <path_to_pdd_yaml_file>

import argparse
import yaml
import sys
import os
import shutil
import json

# Adjust path to import PddSchema from the same directory
# This assumes pdd_schema.py is in the same directory as validate_pdd.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    from pdd_schema import PddSchema, SpecializedHandlerPddSchema
except ImportError as e:
    print(f"Error: Could not import schemas from pdd_schema.py. Ensure it's in the same directory ({SCRIPT_DIR}).")
    print(f"Details: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Validate a PDD YAML file against PddSchema and optionally save to a vault as JSON.')
    parser.add_argument('pdd_file_path', type=str, help='Path to the PDD YAML file to validate.')
    parser.add_argument('--vault', type=str, help='Optional path to a directory where the PDD will be saved as a JSON file if validation is successful.')
    args = parser.parse_args()

    file_path = args.pdd_file_path
    vault_path = args.vault

    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)

    if vault_path and not os.path.isdir(vault_path):
        print(f"Error: Vault path '{vault_path}' is not a valid directory.")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)

    print(f"Attempting to validate PDD file: {file_path}\n")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            pdd_data = yaml.safe_load(f)
            if pdd_data is None:
                print("Error: PDD file is empty or not valid YAML.")
                sys.exit(1)

    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {file_path}")
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        sys.exit(1)

    try:
        pdd_type = pdd_data.get('pdd_type', 'generic') # Get pdd_type, default to 'generic'

        if pdd_type == 'specialized_handler':
            print("Using SpecializedHandlerPddSchema for validation.")
            pdd_instance = SpecializedHandlerPddSchema(**pdd_data)
        else:
            print("Using PddSchema (generic) for validation.")
            pdd_instance = PddSchema(**pdd_data)

        print("Validation Successful!")
        print(f"PDD '{pdd_instance.name}' (Type: {pdd_type}, ID: {pdd_instance.id}, Version: {pdd_instance.version}) validated successfully.")

        if vault_path:
            try:
                base_name = os.path.basename(file_path)
                json_file_name = os.path.splitext(base_name)[0] + ".json"
                destination_path = os.path.join(vault_path, json_file_name)

                with open(destination_path, 'w', encoding='utf-8') as json_f:
                    json.dump(pdd_data, json_f, indent=2, ensure_ascii=False)
                
                print(f"Successfully saved validated PDD as JSON to '{destination_path}'.")
            except Exception as e:
                print(f"Error: Could not save PDD as JSON to vault path '{vault_path}'.")
                print(f"Details: {e}")
                # Consider sys.exit(1) if vaulting failure is critical

    except Exception as e: # Pydantic's ValidationError is a subclass of Exception
        print("Validation Failed!")
        print("Details:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()