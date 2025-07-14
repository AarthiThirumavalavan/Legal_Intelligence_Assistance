import json
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

# Clear existing collection and recreate to fix corrupted data
try:
    client.delete_collection("legal_cases")
    print("Deleted existing collection")
except Exception:
    print("No existing collection to delete")

collection = client.create_collection("legal_cases")

with open("/Users/aarthithirumavalavan/Desktop/Job_related_UK/Scrumconnect/db/cases.json") as f:
    data = json.load(f)
    for case in data:
        # FIXED: Properly handle list metadata fields
        case_cleaned = case.copy()
        for key, value in case_cleaned.items():
            if isinstance(value, list):
                # Store as JSON string instead of comma-separated string
                case_cleaned[key] = json.dumps(value)

        emb = model.encode(case_cleaned["summary"]).tolist()
        collection.add(
            documents=[case_cleaned["summary"]],
            embeddings=[emb],
            metadatas=[case_cleaned],
            ids=[case_cleaned["case_id"]],
        )

print(f"Successfully imported {len(data)} cases")

def retrieve_similar_cases(query, k=3):
    emb = model.encode(query).tolist()
    results = collection.query(query_embeddings=[emb], n_results=k)
    
    cases = []
    for metadata in results["metadatas"][0]:
        case = metadata.copy()
        
        # Convert JSON strings back to lists
        for key, value in case.items():
            if isinstance(value, str) and (value.startswith('[') and value.endswith(']')):
                try:
                    case[key] = json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, keep as string
                    pass
        
        cases.append(case)
    
    return cases

# Test function to verify the fix
def test_retrieval():
    """Test function to verify the fix works"""
    test_cases = retrieve_similar_cases("impaired driving", k=1)
    if test_cases:
        case = test_cases[0]
        print("Test retrieval successful!")
        print(f"Case ID: {case.get('case_id')}")
        print(f"Key Legal Issues: {case.get('key_legal_issues')}")
        print(f"Type of key_legal_issues: {type(case.get('key_legal_issues'))}")
        
        if isinstance(case.get('key_legal_issues'), list):
            print("SUCCESS: key_legal_issues is properly stored as a list")
        else:
            print("ISSUE: key_legal_issues is not a list")
    else:
        print("No test cases retrieved")

if __name__ == "__main__":
    test_retrieval()


# Alternative approach if ChromaDB has issues with JSON in metadata
# You can also try this approach:

def alternative_approach():
    """Alternative approach that flattens lists differently"""
    
    # Clear and recreate collection
    try:
        client.delete_collection("legal_cases_alt")
    except Exception:
        pass
    
    collection_alt = client.create_collection("legal_cases_alt")
    
    with open("/Users/aarthithirumavalavan/Desktop/Job_related_UK/Scrumconnect/db/cases.json") as f:
        data = json.load(f)
        for case in data:
            case_cleaned = case.copy()
            
            # Handle lists by creating separate fields
            if 'key_legal_issues' in case_cleaned and isinstance(case_cleaned['key_legal_issues'], list):
                # Store the list as a pipe-separated string (easier to split later)
                case_cleaned['key_legal_issues'] = " | ".join(case_cleaned['key_legal_issues'])
                
                # Also store individual issues as separate fields for better searchability
                for i, issue in enumerate(case['key_legal_issues']):
                    case_cleaned[f'legal_issue_{i+1}'] = issue
            
            emb = model.encode(case_cleaned["summary"]).tolist()
            collection_alt.add(
                documents=[case_cleaned["summary"]],
                embeddings=[emb],
                metadatas=[case_cleaned],
                ids=[case_cleaned["case_id"]],
            )
    
    print("Alternative approach completed")

def retrieve_similar_cases_alt(query, k=3):
    """Alternative retrieval function"""
    emb = model.encode(query).tolist()
    results = collection_alt.query(query_embeddings=[emb], n_results=k)
    
    cases = []
    for metadata in results["metadatas"][0]:
        case = metadata.copy()
        
        # Convert pipe-separated string back to list
        if 'key_legal_issues' in case and isinstance(case['key_legal_issues'], str):
            if ' | ' in case['key_legal_issues']:
                case['key_legal_issues'] = case['key_legal_issues'].split(' | ')
        
        cases.append(case)
    
    return cases


# Debug function to check what's actually stored in ChromaDB
def debug_chromadb_storage():
    """Debug function to see what's actually stored"""
    try:
        # Get all items from collection
        all_items = collection.get()
        
        if all_items['metadatas']:
            print("=== CHROMADB STORAGE DEBUG ===")
            first_item = all_items['metadatas'][0]
            print(f"First item metadata: {first_item}")
            print(f"Key legal issues: {first_item.get('key_legal_issues')}")
            print(f"Type: {type(first_item.get('key_legal_issues'))}")
            
            # Check each character
            issues = first_item.get('key_legal_issues', '')
            if isinstance(issues, str):
                print(f"String length: {len(issues)}")
                print(f"First 20 chars: {issues[:20]}")
                print(f"Contains ', ': {', ' in issues}")
        
    except Exception as e:
        print(f"Debug error: {e}")

if __name__ == "__main__":
    debug_chromadb_storage()