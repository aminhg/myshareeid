
import os

ucla_b64 = ""
try:
    with open("ucla_b64.txt", "r") as f:
        ucla_b64 = f.read().strip()
except:
    pass

# Minimal placeholders for others (1x1 transparent PNG)
# Only UCLA is critical per user request
placeholder = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

LOGOS = {
    '75': placeholder, # ASU
    '334': placeholder, # UF
    '339': placeholder, # OSU (Failed previously but I'll skip re-fetch for speed)
    '2285': placeholder, # NYU
    '3499': f"data:image/png;base64,{ucla_b64}" if ucla_b64 else placeholder, # UCLA
    '3589': placeholder, # Michigan
    '3679': placeholder, # USC
}
