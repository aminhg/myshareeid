import httpx
import json

PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
BASE_URL = f"https://services.sheerid.com/rest/v2/program/{PROGRAM_ID}/organization"

PARAMS = {
    "country": "US",
    "type": "UNIVERSITY"
}

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_school(name):
    print(f"Searching for: {name} (key=name)...")
    try:
        response = httpx.get(
            f"{BASE_URL}",
            params={**PARAMS, "name": name},
            headers=HEADERS,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                # Return first match
                school = data[0]
                print(f"FOUND: {school['name']} (ID: {school['id']})")
                return school
            else:
                print(f"NOT FOUND: {name}")
        else:
             print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

TARGETS = [
    "University of Texas at Austin",
    "University of Michigan-Ann Arbor",
    "University of Washington", # Seattle
    "Rutgers, The State University of New Jersey", # Main one
    "Pennsylvania State University", # Main
    "University of Southern California" # USC
]

results = {}
for name in TARGETS:
    res = search_school(name)
    if res:
        results[str(res['id'])] = res

print("\n=== CONFIG FORMAT ===")
print(json.dumps(results, indent=4))
