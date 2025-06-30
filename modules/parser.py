import json
import yaml
import os

def parse_file(filepath):
    _, ext = os.path.splitext(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            if ext == '.json':
                data = json.load(f)
                yield from extract_strings_from_data(data)
            elif ext in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
                yield from extract_strings_from_data(data)
            elif '.env' in os.path.basename(filepath):
                for line in f:
                    if '=' in line:
                        yield line.split('=', 1)[1].strip()
            else: 
                for line in f:
                    yield line
    except Exception as e:
        print(f"[ERROR] Failed to parse {filepath}: {e}")

def extract_strings_from_data(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str): yield k
            yield from extract_strings_from_data(v)
    elif isinstance(data, list):
        for item in data:
            yield from extract_strings_from_data(item)
    elif isinstance(data, str):
        yield data