
import requests
import base64
from io import BytesIO
from PIL import Image

# Multiple candidate URLs per school
LOGO_CANDIDATES = {
    '75': [ # ASU - Arizona State University
        'https://upload.wikimedia.org/wikipedia/en/thumb/8/82/Arizona_State_Sun_Devils_logo.svg/1200px-Arizona_State_Sun_Devils_logo.svg.png',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Arizona_State_Sun_Devils_logo.svg/800px-Arizona_State_Sun_Devils_logo.svg.png',
        'https://stickershop.line-scdn.net/stickershop/v1/product/1465222/LINEStorePC/main.png',
    ],
    '334': [ # UF - University of Florida
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/University_of_Florida_logo.svg/1200px-University_of_Florida_logo.svg.png',
    ],
    '339': [ # OSU - Ohio State University
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Ohio_State_Buckeyes_logo.svg/1200px-Ohio_State_Buckeyes_logo.svg.png',
        'https://upload.wikimedia.org/wikipedia/en/thumb/d/d7/Ohio_State_Buckeyes_logo.svg/800px-Ohio_State_Buckeyes_logo.svg.png',
    ],
    '1623': [ # NYU - New York University
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/New_York_University_Seal.svg/1200px-New_York_University_Seal.svg.png',
        'https://upload.wikimedia.org/wikipedia/en/thumb/4/47/New_York_University_seal.svg/1024px-New_York_University_seal.svg.png',
        'https://seeklogo.com/images/N/nyu-new-york-university-logo-2B6002FD5A-seeklogo.com.png'
    ],
    '3429': [ # USC - University of Southern California
        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/USC_Trojans_logo.svg/1200px-USC_Trojans_logo.svg.png',
        'https://upload.wikimedia.org/wikipedia/en/thumb/e/e9/USC_Trojans_logo.svg/800px-USC_Trojans_logo.svg.png',
        'https://logos-world.net/wp-content/uploads/2023/02/USC-Trojans-Logo.png'
    ],
    '3499': [ # UCLA - University of California, Los Angeles
        'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/UCLA_Bruins_script_logo.svg/1200px-UCLA_Bruins_script_logo.svg.png',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/UCLA_Bruins_logo.svg/1280px-UCLA_Bruins_logo.svg.png',
        'https://logos-world.net/wp-content/uploads/2023/01/UCLA-Bruins-Logo.png'
    ],
    '3589': [ # Michigan - University of Michigan
        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/University_of_Michigan_logo.svg/1200px-University_of_Michigan_logo.svg.png', 
        'https://upload.wikimedia.org/wikipedia/commons/f/fb/Michigan_Wolverines_logo.svg'
    ]
}

OUTPUT_FILE = "one/logos_data.py"

def fetch_and_process_logo(school_id, urls):
    for url in urls:
        print(f"Attempting fetch {school_id} from {url}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"Request failed: {resp.status_code}")
                continue
            
            # Open image
            img = Image.open(BytesIO(resp.content))
            img = img.convert("RGBA")
            img.thumbnail((300, 300), Image.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            b64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return b64_str
        except Exception as e:
            print(f"Error: {e}")
            continue
    return None

def main():
    logos_data = {}
    
    for sid, urls in LOGO_CANDIDATES.items():
        b64 = fetch_and_process_logo(sid, urls)
        if b64:
            logos_data[sid] = b64
            print(f"[SUCCESS] {sid}")
        else:
            print(f"[FAIL] {sid}")

    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('"""University Logos (Base64 Encoded)"""\n')
        f.write('LOGOS = {\n')
        for sid, b64 in logos_data.items():
            f.write(f'    "{sid}": "{b64}",\n')
        f.write('}\n')
    
    print(f"\nSaved {len(logos_data)} logos to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
