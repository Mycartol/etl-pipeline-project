import difflib
import datetime
import argparse
from pymongo import MongoClient
from pathlib import Path
import os
import requests
from dotenv import load_dotenv

# --- Configuration ---
def load_configuration():
    """Load configuration from environment variables"""
    env_path = Path('..') / '.env'
    load_dotenv(env_path)
    
    return {
        'api_url': os.getenv('API_URL', 'http://localhost:5000/api/diffs'),
        'input_db_uri': os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
        'input_db_name': os.getenv('DB_NAME', 'modulo2t'),
        'input_collection': os.getenv('INPUT_COLLECTION', 'bip_pages')
    }

# --- MongoDB Utilities ---
def get_mongo_collection(connection_string, db_name, collection_name):
    """Connect to MongoDB and return the specified collection"""
    client = MongoClient(connection_string)
    db = client[db_name]
    return db[collection_name]

# --- Diff Utilities ---
def find_differences(text1, text2):
    """Find differences between two texts with line numbers"""
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))
    
    differences = []
    line_num = 1  # Track line numbers in the original file
    
    i = 0
    while i < len(diff):
        line = diff[i]
        
        if line.startswith('- '):
            removed_line = line[2:]
            if i+1 < len(diff) and diff[i+1].startswith('+ '):
                # Modification (removal + addition)
                added_line = diff[i+1][2:]
                differences.append({
                    'type': 'modified',
                    'old_line': removed_line,
                    'new_line': added_line,
                    'line_number': line_num,
                })
                i += 1  # Skip the next line
            else:
                # Removal
                differences.append({
                    'type': 'removed',
                    'line': removed_line,
                    'line_number': line_num,
                })
            line_num += 1
        elif line.startswith('+ '):
            # Addition
            added_line = line[2:]
            differences.append({
                'type': 'added',
                'line': added_line,
                'line_number': line_num,
            })
        elif line.startswith('  '):
            # Unchanged line
            line_num += 1
        i += 1
    
    return differences

# --- API Communication ---
def save_diff_via_api(api_url, diff_data):
    """Send diff data to the API endpoint"""
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(api_url, json=diff_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response content: {e.response.text}")
        return None

# --- Core Logic ---
def compare_latest_docs(url, input_collection, api_url):
    """Compare the two most recent documents for a given url and send to API"""
    # Find the two most recent documents with the given url
    cursor = input_collection.find(
        {"url": url},
        sort=[("date", -1)],  # Newest first
        limit=2  # Only fetch the two most recent
    )
    docs = list(cursor)
    
    if len(docs) < 2:
        print(f"⚠️ Only {len(docs)} document(s) found for url '{url}'. Need at least 2 to compare.")
        return
    
    # Extract texts to compare
    doc1, doc2 = docs[0], docs[1]
    text1 = doc1.get("content", "")  # Adjust field name if needed
    text2 = doc2.get("content", "")
    
    # Generate differences
    differences = find_differences(text1, text2)
    
    # Prepare result for API
    diff_data = {
        'url': url,
        'from_version': str(doc1['_id']),
        'to_version': str(doc2['_id']),
        'diff_content': {
            'differences': differences,
            'stats': {
                'total_differences': len(differences),
                'added_lines': sum(1 for d in differences if d['type'] == 'added'),
                'removed_lines': sum(1 for d in differences if d['type'] == 'removed'),
                'modified_lines': sum(1 for d in differences if d['type'] == 'modified')
            }
        }
    }
    
    # Send to API
    api_response = save_diff_via_api(api_url, diff_data)
    if api_response:
        print(f"✅ Compared {url}. Results sent to API. Response: {api_response}")
    else:
        print(f"❌ Failed to save comparison for {url}")

# --- Main ---
if __name__ == "__main__":
    # Load configuration
    config = load_configuration()
    
    # Set up CLI argument parser
    parser = argparse.ArgumentParser(description="Compare the two most recent documents for a given url.")
    parser.add_argument("url", help="The url to compare documents for.")
    args = parser.parse_args()
    
    # Connect to MongoDB (input only)
    input_coll = get_mongo_collection(
        config['input_db_uri'], 
        config['input_db_name'], 
        config['input_collection']
    )
    
    # Run comparison and send to API
    compare_latest_docs(args.url, input_coll, config['api_url'])