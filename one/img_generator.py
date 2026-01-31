"""PNG 学生证生成模块 - Penn State LionPATH"""
import random
from datetime import datetime, timedelta
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageTransform
import io
import random
import piexif


from . import config


from .logos_data import LOGOS

# School Themes (Colors & App Titles & Real Logos)
SCHOOL_THEMES = {
    '75': { # ASU
        'primary': '#8C1D40', 'secondary': '#FFC627', 'title': 'MyASU',
        'logo': LOGOS.get('75', '')
    },
    '334': { # UF
        'primary': '#FA4616', 'secondary': '#0021A5', 'title': 'GatorSafe',
        'logo': LOGOS.get('334', '')
    },
    '339': { # OSU
        'primary': '#BB0000', 'secondary': '#666666', 'title': 'Ohio State',
        'logo': LOGOS.get('339', '')
    },
    '2285': { # NYU
        'primary': '#57068c', 'secondary': '#8900e1', 'title': 'NYU Mobile',
        'logo': LOGOS.get('2285', '')
    },
    '3499': { # UCLA
        'primary': '#2D68C4', 'secondary': '#F2A900', 'title': 'UCLA Mobile',
        'logo': LOGOS.get('3499', '')
    },
    '3589': { # Michigan
        'primary': '#00274C', 'secondary': '#FFCB05', 'title': 'Michigan App',
        'logo': LOGOS.get('3589', '')
    },
    '3679': { # USC
        'primary': '#9D2235', 'secondary': '#FFC72C', 'title': 'USC Mobile',
        'logo': LOGOS.get('3679', '')
    },
}

def create_fallback_logo(school_id, theme):
    """Generates a text-based logo if the image is missing."""
    width, height = 400, 400
    # Create transparent image
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Approx font size
    font_size = 120
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Get Initials or Name
    school_name = config.SCHOOLS.get(school_id, {}).get('name', 'University')
    text = "".join([w[0] for w in school_name.split() if w[0].isupper()][:3])
    if 'University' in school_name and len(text) < 2:
        text = "UNIV"
    
    # Draw Text centered
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older Pillow
        text_width, text_height = draw.textsize(text, font=font)

    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Draw with main primary color
    draw.text((x, y), text, font=font, fill=theme['primary'])
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

def generate_asu_id():
    return f"{random.randint(100000000, 999999999)}"

def generate_edu_email(first_name, last_name, domain="asu.edu"):
    """
    Generate Student Email with dynamic domain
    """
    style = random.choice(['fLast', 'dot'])
    if style == 'fLast':
        email = f"{first_name[0].lower()}{last_name.lower()}{random.randint(1,99)}@{domain.lower()}"
    else:
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@{domain.lower()}"
    return email

# Backward compatibility (for import safety)
def generate_asu_email(first_name, last_name):
    return generate_edu_email(first_name, last_name, "asu.edu")

def generate_html_mobile(first_name, last_name, school_id='75'):
    """
    Generate Mobile App Screenshot (Dynamic School Name)
    """
    # Generate School-Specific ID Format (Regex Match)
    if str(school_id) == '334': # UF (8 digits)
        school_id_num = f"{random.randint(10000000, 99999999)}"
    elif str(school_id) == '2285': # NYU (N + 9 digits)
        school_id_num = f"N{random.randint(100000000, 999999999)}"
    elif str(school_id) in ['3679', '75']: # USC / ASU (10 digits)
        school_id_num = f"{random.randint(1000000000, 9999999999)}"
    elif str(school_id) == '339': # Ohio State (BuckID - 8 or 9 digits)
        school_id_num = f"{random.randint(100000000, 999999999)}"
    else: # Default 9 digits
        school_id_num = f"{random.randint(100000000, 999999999)}"
    name = f"{first_name} {last_name}"
    date_str = datetime.now().strftime('%b %d, %Y')
    
    # Get School Info from Config
    school_config = config.SCHOOLS.get(str(school_id), config.SCHOOLS['75'])
    school_name = school_config['name']
    
    # School Themes (Colors & App Titles & Real Logos)
    # MOVED TO GLOBAL SCOPE


    # Default Theme
    theme = SCHOOL_THEMES.get(str(school_id), SCHOOL_THEMES['75'])
    
    app_title = theme['title']
    primary_color = theme['primary']
    secondary_color = theme['secondary']
    logo_url = theme['logo']
    
    # Fallback if logo is missing (Realism Booster)
    if not logo_url or len(logo_url) < 100:
        logo_url = create_fallback_logo(str(school_id), theme)

    # Dynamic Status Bar Info
    # Random Time
    hour = datetime.now().hour
    minute = datetime.now().minute
    # Occasionally vary the time slightly (simulated delay)
    if random.choice([True, False]):
        minute = (minute + random.randint(1, 5)) % 60
    time_str = f"{hour:02d}:{minute:02d}"

    # Random Battery
    battery_level = random.randint(45, 98)
    
    # Random Signal
    signal_type = random.choice(['5G', '5G', 'LTE', '5G'])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{app_title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        
        :root {{
            --primary: {primary_color}; 
            --secondary: {secondary_color};
            --bg: #f5f5f7;
            --card-bg: #ffffff;
            --text-main: #1c1c1e;
            --text-sub: #8e8e93;
            --success: #2e7d32;
        }}


        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Roboto", Helvetica, Arial, sans-serif;
            background-color: #000;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}

        .screen {{
            width: 375px;
            height: 812px;
            background-color: var(--bg);
            position: relative;
            overflow: hidden;
            border-radius: 40px;
            box-shadow: 0 0 0 10px #333;
        }}

        .status-bar {{
            height: 44px;
            background: var(--primary);
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            font-size: 14px;
            font-weight: 600;
        }}

        .app-header {{
            background-color: var(--primary);
            color: white;
            padding: 15px 20px 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .logo-text {{ font-size: 20px; font-weight: 800; letter-spacing: 0.5px; color: #fff; }}
        .header-icons {{ display: flex; gap: 15px; }}
        .icon-box {{ width: 32px; height: 32px; background: rgba(255,255,255,0.2); border-radius: 50%; }}

        .content {{ padding: 20px; padding-bottom: 80px; }}

        .profile-card {{
            background: #fff;
            border-radius: 16px;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 25px;
            border: 1px solid #eee;
            overflow: hidden;
            position: relative; 
        }}
        
        .card-header {{
            background: var(--primary);
            width: 100%;
            height: 80px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 40px; 
        }}
        
        .avatar {{
            width: 100px; height: 100px;
            background: #eee url('{logo_url}') center/60% no-repeat; 
            border-radius: 50%;
            border: 4px solid #fff;
            position: absolute;
            top: 60px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            background-color: #fff;
        }}

        .profile-info {{ text-align: center; padding: 0 20px 20px; width: 100%; box-sizing: border-box; }}
        .profile-info h2 {{ margin: 10px 0 5px; font-size: 22px; color: #000; font-weight: 800; }}
        .profile-info p {{ margin: 2px 0; color: #333; font-size: 14px; font-weight: 500; }}
        
        .id-badge {{
            background: #f0f0f0; color: #333;
            padding: 4px 12px; border-radius: 20px;
            font-size: 13px; font-weight: bold;
            margin: 10px 0; display: inline-block;
            letter-spacing: 1px;
        }}
        
        .status-pill {{
            background: #e8f5e9; color: #2e7d32;
            padding: 6px 16px; border-radius: 6px;
            font-weight: 900; font-size: 16px;
            margin-top: 15px; display: inline-block;
            border: 2px solid #c8e6c9;
            text-transform: uppercase;
        }}
        
        .barcode-area {{
            margin-top: 20px;
            height: 60px; width: 80%;
            background: repeating-linear-gradient(
                90deg,
                #000, #000 2px,
                #fff 2px, #fff 4px,
                #000 4px, #000 8px,
                #fff 8px, #fff 10px
            );
            opacity: 0.8;
        }}

        .grid-menu {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }}

        .menu-item {{
            background: #fff;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }}
        .menu-icon {{ width: 40px; height: 40px; background: #f0f0f0; border-radius: 10px; margin: 0 auto 10px; }}
        .menu-label {{ font-size: 13px; font-weight: 600; color: #333; }}

        .section-title {{ font-size: 16px; font-weight: 700; margin-bottom: 15px; color: #333; }}
        
        .class-card {{
            background: #fff;
            border-radius: 12px;
            padding: 15px;
            border-left: 4px solid var(--success);
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }}
        
        .class-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
        .class-code {{ font-weight: 700; color: var(--primary); font-size: 14px; }}
        .term-badge {{ background: #eee; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
        
        .class-name {{ font-size: 15px; font-weight: 500; margin-bottom: 5px; }}
        .class-time {{ font-size: 12px; color: #666; }}

        .bottom-nav {{
            position: absolute; bottom: 0; width: 100%; height: 65px;
            background: #fff; border-top: 1px solid #eee;
            display: flex; justify-content: space-around; align-items: center;
        }}
        .nav-item {{ width: 24px; height: 24px; background: #ccc; border-radius: 4px; }}
        .nav-item.active {{ background: var(--primary); }}

    </style>
</head>
<body>

<div class="screen">
    <div class="status-bar">
        <span>{time_str}</span>
        <div style="display: flex; gap: 5px; align-items: center;">
            <span>{signal_type}</span>
            <span style="font-size: 12px;">{battery_level}%</span>
        </div>
    </div>

    <div class="app-header">
        <div class="logo-text">{app_title}</div>
        <img src="{logo_url}" style="height: 35px; width: auto; background: white; padding: 4px; border-radius: 6px;">
    </div>

    <div class="content">
        <div class="profile-card" style="position: relative;">
            <div class="card-header">
                <!-- Using School Colors -->
            </div>
            <div class="avatar"></div>
            
            <div class="profile-info" style="margin-top: 40px;">
                <h2>{name}</h2>
                <div class="id-badge">ID: {school_id_num}</div>
                
                <div style="margin-top: 5px; font-size: 12px; color: #666;">STUDENT ACCESS</div>
                
                <div class="status-pill">ACTIVE STUDENT</div>
                
                <div style="margin-top: 8px; font-size: 12px; font-weight: bold; color: #444;">
                    Valid Thru: {date_str[-4:]}
                </div>

                <div class="barcode-area"></div>
                <div style="font-size: 10px; margin-top: 4px; letter-spacing: 2px;">{school_id_num}</div>
            </div>
        </div>

        <div class="grid-menu">
            <div class="menu-item">
                <div class="menu-icon" style="background: #e3f2fd;"></div>
                <div class="menu-label">Email</div>
            </div>
            <div class="menu-item">
                <div class="menu-icon" style="background: #fff3e0;"></div>
                <div class="menu-label">Courses</div>
            </div>
            <div class="menu-item">
                <div class="menu-icon" style="background: #e8f5e9;"></div>
                <div class="menu-label">Financial Aid</div>
            </div>
            <div class="menu-item">
                <div class="menu-icon" style="background: #f3e5f5;"></div>
                <div class="menu-label">ID Card</div>
            </div>
        </div>

        <h3 class="section-title">Enrolled Courses (Fall)</h3>
        
        <div class="class-card">
            <div class="class-header">
                <span class="class-code">CS 101</span>
                <span class="term-badge">Enrolled</span>
            </div>
            <div class="class-name">Intro to Computer Science</div>
            <div class="class-time">MoWe 10:00 AM - 11:30 AM</div>
        </div>

        <div class="class-card">
            <div class="class-header">
                <span class="class-code">MATH 201</span>
                <span class="term-badge">Enrolled</span>
            </div>
            <div class="class-name">Calculus II</div>
            <div class="class-time">TuTh 9:00 AM - 10:30 AM</div>
        </div>
        
        <div style="text-align: center; color: #999; font-size: 11px; margin-top: 20px;">
            {school_name} © {date_str[-4:]}
        </div>

    </div>

    <div class="bottom-nav">
        <div class="nav-item active"></div>
        <div class="nav-item"></div>
        <div class="nav-item"></div>
    </div>
</div>

</body>
</html>"""
    return html


def generate_html_schedule(first_name, last_name, school_id='75'):
    """
    Generate Class Schedule (Dynamic School Name)
    """
    school_id_num = generate_asu_id()
    name = f"{last_name}, {first_name}"
    date_str = datetime.now().strftime('%m/%d/%Y')
    
    # Get School Info from Config
    school_config = config.SCHOOLS.get(str(school_id), config.SCHOOLS['75'])
    school_name = school_config['name']
    
    color = "#333333"
    # Use Theme Color if available
    theme = SCHOOL_THEMES.get(str(school_id), SCHOOL_THEMES['75'])
    color = theme['primary']
    logo_url = theme['logo']

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Registration Summary</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background: #fff; color: #000;
            margin: 40px; line-height: 1.4;
        }}
        .header {{ border-bottom: 2px solid {color}; padding-bottom: 10px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .logo {{ font-size: 20px; font-weight: bold; color: {color}; }}
        .doc-title {{ font-size: 18px; font-weight: bold; text-transform: uppercase; }}
        
        .student-info {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
            margin-bottom: 30px; font-size: 14px;
        }}
        .label {{ font-weight: bold; color: #555; }}
        .value {{ font-weight: bold; font-size: 15px; }}

        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; }}
        th {{ text-align: left; border-bottom: 2px solid #000; padding: 5px; text-transform: uppercase; font-size: 11px; }}
        td {{ padding: 8px 5px; border-bottom: 1px solid #ddd; }}
        
        .enrolled-badge {{
            background: #eee; padding: 3px 6px; border-radius: 3px; font-weight: bold; font-size: 10px; border: 1px solid #ccc;
        }}
        
        .footer {{ margin-top: 50px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 10px; color: #777; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="{logo_url}" style="height: 50px; width: auto;">
            <div>
                <div class="logo" style="margin-bottom: 2px;">{school_name}</div>
                <div class="doc-title" style="font-size: 14px; color: #555;">Class Schedule • Spring 2026</div>
            </div>
        </div>
    </div>

    <div class="student-info">
        <div>
            <div class="label">Student Name</div>
            <div class="value">{name}</div>
        </div>
        <div>
            <div class="label">Student ID</div>
            <div class="value">{school_id_num}</div>
        </div>
        <tr>
            <div class="label">Term</div>
            <div class="value">Spring 2026</div>
        </div>
        <div>
            <div class="label">Date Generated</div>
            <div class="value">{date_str}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Status</th>
                <th>Course</th>
                <th>Title</th>
                <th>Units</th>
                <th>Days & Times</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="enrolled-badge">Enrolled</span></td>
                <td>CS 101</td>
                <td>Intro to Computer Science</td>
                <td>3.0</td>
                <td>MoWe 10:00AM - 11:30AM</td>
            </tr>
            <tr>
                <td><span class="enrolled-badge">Enrolled</span></td>
                <td>MATH 201</td>
                <td>Calculus II</td>
                <td>4.0</td>
                <td>TuTh 9:00AM - 10:30AM</td>
            </tr>
            <tr>
                <td><span class="enrolled-badge">Enrolled</span></td>
                <td>ENG 102</td>
                <td>Academic Writing</td>
                <td>3.0</td>
                <td>Online</td>
            </tr>
        </tbody>
    </table>
    
    <div style="text-align: right; margin-top: 10px; font-weight: bold; font-size: 13px;">
        Total Units: 10.0
    </div>

    <div class="footer">
        This document is an unofficial summary of your class schedule. <br>
        Office of the Registrar • {school_name}
    </div>
</body>
</html>"""
    return html


def apply_camera_effect(png_bytes):
    """
    Simulate a photo taken of a screen (Moire, Blur, Glare) - RESTORED "Real Camera" Mode
    """
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    width, height = image.size

    # === CLASSIC BURIK MODE (Restored) ===
    # This was the config that had "10s Success"
    # Features: Heavy Blur, Noise, Distortion.
    
    # 1. Perspective Skew (Tilt) - Heavy
    w, h = image.size
    distortion = random.randint(15, 30) 
    quad = (
        distortion, 0,  
        0, h,          
        w, h,          
        w-distortion, 0 
    )
    image = image.transform((w, h), Image.QUAD, quad, resample=Image.BICUBIC)
    
    # 2. Rotation
    angle = random.uniform(-1.5, 1.5)
    image = image.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(20, 20, 20))

    # 3. Vignette (Dark Corners)
    vignette_layer = Image.new("L", image.size, 255)
    v_draw = ImageDraw.Draw(vignette_layer)
    c_x, c_y = image.size[0]//2, image.size[1]//2
    v_w, v_h = image.size[0] * 1.5, image.size[1] * 1.2
    v_draw.ellipse((c_x - v_w//2, c_y - v_h//2, c_x + v_w//2, c_y + v_h//2), fill=0)
    vignette_layer = vignette_layer.filter(ImageFilter.GaussianBlur(150))
    
    # Apply Vignette
    radial_mask = ImageOps.invert(vignette_layer)
    black_vignette = Image.new("RGBA", image.size, (0,0,0,0))
    black_vignette.putalpha(radial_mask)
    image = image.convert("RGBA")
    alpha = black_vignette.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.5) 
    black_vignette.putalpha(alpha)
    image = Image.alpha_composite(image, black_vignette)
    image = image.convert("RGB")

    # 4. Glare
    glare_layer = Image.new("RGBA", image.size, (255,255,255,0))
    g_draw = ImageDraw.Draw(glare_layer)
    g_draw.polygon([(0,0), (w//2, 0), (0, h//2)], fill=(255,255,255,15))
    image = image.convert("RGBA")
    image = Image.alpha_composite(image, glare_layer)
    image = image.convert("RGB")

    # 5. Noise & Blur (The "Burik" Effect)
    # Restore original high noise and blur
    noise = Image.effect_noise(image.size, 15).convert("RGB") 
    image = Image.blend(image, noise, 0.05) 
    image = image.filter(ImageFilter.BoxBlur(0.5))

    # Output
    output = io.BytesIO()
    
    # === EXIF (Simple/Safe) ===
    # Minimal authentic headers
    zeroth_ifd = {
        piexif.ImageIFD.Make: u"Samsung",
        piexif.ImageIFD.Model: random.choice([u"SM-G991B", u"SM-S901B", u"SM-A528B"]),
        piexif.ImageIFD.Software: u"Android 13",
        piexif.ImageIFD.Orientation: 1,
        piexif.ImageIFD.DateTime: datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
    }
    exif_dict = {"0th": zeroth_ifd}
    exif_bytes = piexif.dump(exif_dict)

    image.save(output, format='JPEG', quality=80, subsampling=0, exif=exif_bytes)
    
    return output.getvalue()

def apply_paper_effect(png_bytes):
    """
    Simulate a SCANNED or PRINTED PAPER document.
    - Adds Paper Texture (Noise/Grain).
    - Adds Contrast (Toner effect).
    - Subtle warp (Paper isn't 100% flat).
    - NO BLUR (Text remains sharp).
    """
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    
    # 1. Paper Texture (Noise)
    # Add heavily textured noise (Monochrome)
    noise = Image.effect_noise(image.size, 20).convert("L")
    # Blend carefully - Multiply effectively simulates ink on paper texture
    # Create white base
    texture = Image.new("RGB", image.size, (255,255,255))
    texture.paste(noise, (0,0), noise)
    
    # Soft Light blend for texture? Or Multiply?
    # Simple blend is safer for speed.
    image = Image.blend(image, texture.convert("RGB"), 0.05)
    
    # 2. Contrast / Sharpen (Toner Effect)
    # Make text pop out like printed ink
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.4) # Boost contrast
    
    image = image.filter(ImageFilter.SHARPEN)
    
    # 3. Subtle Paper Warmth (Ivory tint? No, keep it white for OCR, maybe slightly off-white)
    # Let's keep it mostly white to avoid background issues.
    
    # 4. Subtle Rotation (Scanner Feed)
    angle = random.uniform(-0.2, 0.2)
    image = image.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=95, subsampling=0)
    return output.getvalue()


def generate_html_tuition(first_name, last_name, school_id='75'):
    """
    Generate Tuition Receipt (Dynamic School Name)
    """
    school_id_num = generate_asu_id()
    name = f"{first_name} {last_name}"
    
    # Backdate 15-45 days (Realistic Payment Date)
    random_days = random.randint(15, 45)
    payment_date = datetime.now() - timedelta(days=random_days)
    date_str = payment_date.strftime('%m/%d/%Y')
    
    # Get School Info from Config
    school_config = config.SCHOOLS.get(str(school_id), config.SCHOOLS['75'])
    school_name = school_config['name']
    
    # Get Theme for Logo
    theme = SCHOOL_THEMES.get(str(school_id), SCHOOL_THEMES['75'])
    logo_url = theme['logo']
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Payment Receipt</title>
    <style>
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; margin: 40px; color: #333; }}
        .header {{ border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }}
        .school-name {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .dept {{ font-size: 14px; color: #555; }}
        
        .receipt-info {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
        .info-block {{ }}
        .label {{ font-size: 11px; text-transform: uppercase; color: #777; margin-bottom: 3px; }}
        .value {{ font-size: 14px; font-weight: bold; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th {{ text-align: left; border-bottom: 1px solid #ccc; padding: 10px 5px; font-size: 12px; }}
        td {{ padding: 15px 5px; border-bottom: 1px solid #eee; font-size: 14px; }}
        .amount {{ text-align: right; }}
        
        .total-row td {{ border-top: 2px solid #000; border-bottom: none; font-weight: bold; font-size: 16px; padding-top: 20px; }}
        
        .status {{ 
            display: inline-block; padding: 5px 10px; border-radius: 4px; 
            background: #e8f5e9; color: #2e7d32; font-weight: bold; font-size: 12px;
            border: 1px solid #c8e6c9;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
             <div>
                <div class="school-name">{school_name}</div>
                <div class="dept">Office of the Bursar / Student Accounts</div>
             </div>
             <img src="{logo_url}" style="height: 60px; width: auto; opacity: 0.9;">
        </div>
    </div>

    <div class="receipt-info">
        <div class="info-block">
            <div class="label">Student Name</div>
            <div class="value">{name}</div>
            <div class="label" style="margin-top: 10px;">Student ID</div>
            <div class="value">{school_id_num}</div>
        </div>
        <div class="info-block" style="text-align: right;">
            <div class="label">Receipt Date</div>
            <div class="value">{date_str}</div>
            <div class="label" style="margin-top: 10px;">Receipt Number</div>
            <div class="value">RCPT-{random.randint(10000000,99999999)}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th class="amount">Amount</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Tuition - Spring 2026</td>
                <td class="amount">$6,450.00</td>
            </tr>
            <tr>
                <td>Technology Fee</td>
                <td class="amount">$250.00</td>
            </tr>
            <tr>
                <td>Student Service Fee</td>
                <td class="amount">$180.00</td>
            </tr>
            <tr class="total-row">
                <td>Total Paid</td>
                <td class="amount">$6,880.00</td>
            </tr>
        </tbody>
    </table>

    <div style="margin-bottom: 20px;">
        <div class="label">Payment Status</div>
        <div class="status">PAID IN FULL</div>
    </div>
    
    <div style="font-size: 11px; color: #999; margin-top: 50px;">
        This is an electronically generated receipt. No signature is required.
    </div>
</body>
</html>"""
    return html

def _generate_screenshot_bytes(html_content, is_mobile=False):
    """Helper to generate screenshot bytes from HTML using Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if not is_mobile:
                # Desktop Viewport for Doc
                browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
                context = browser.new_context(
                    viewport={'width': 1000, 'height': 1200}, 
                    locale='en-US', timezone_id='America/Phoenix',
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            else:
                # Mobile Viewport
                device = p.devices['iPhone 12'] 
                browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
                context = browser.new_context(
                    **device, 
                    locale='en-US', timezone_id='America/Phoenix',
                    permissions=['geolocation'], geolocation={'latitude': 33.424, 'longitude': -111.928}
                )
            
            page = context.new_page()
            page.set_content(html_content, wait_until='networkidle')
            
            if not is_mobile:
                 screenshot_bytes = page.screenshot(type='png', full_page=True)
            else:
                 screenshot_bytes = page.locator('.screen').screenshot(type='png')
            
            browser.close()
            return screenshot_bytes
    except Exception as e:
        raise Exception(f"Playwright Error: {str(e)}")

def generate_mobile_bytes(first_name, last_name, school_id='75'):
    html = generate_html_mobile(first_name, last_name, school_id)
    raw_bytes = _generate_screenshot_bytes(html, is_mobile=True)
    return apply_camera_effect(raw_bytes)

def generate_schedule_bytes(first_name, last_name, school_id='75'):
    html = generate_html_schedule(first_name, last_name, school_id)
    raw_bytes = _generate_screenshot_bytes(html, is_mobile=False)
    # Original Burik Mode for Verification
    return apply_camera_effect(raw_bytes)

def generate_tuition_bytes(first_name, last_name, school_id='75'):
    html = generate_html_tuition(first_name, last_name, school_id)
    raw_bytes = _generate_screenshot_bytes(html, is_mobile=False)
    # Original Burik Mode for Verification
    return apply_camera_effect(raw_bytes)

def generate_image(first_name, last_name, school_id='75', doc_type='mobile'):
    """
    Generate JPEG Document based on doc_type
    doc_type: 'mobile', 'schedule', 'tuition', 'random'
    """
    if doc_type == 'random':
        doc_type = random.choice(['mobile', 'schedule', 'tuition'])

    if doc_type == 'schedule':
        return generate_schedule_bytes(first_name, last_name, school_id)
    elif doc_type == 'tuition':
        return generate_tuition_bytes(first_name, last_name, school_id)
    else:
        # Default to Mobile
        return generate_mobile_bytes(first_name, last_name, school_id)



if __name__ == '__main__':
    # 测试代码
    import sys
    import io

    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("测试 PSU 图片生成...")

    first_name = "John"
    last_name = "Smith"

    print(f"姓名: {first_name} {last_name}")
    print(f"ASU ID: {generate_asu_id()}")
    print(f"邮箱: {generate_edu_email(first_name, last_name)}")

    try:
        img_data = generate_image(first_name, last_name)

        # 保存测试图片
        with open('test_psu_card.png', 'wb') as f:
            f.write(img_data)

        print(f"✓ 图片生成成功! 大小: {len(img_data)} bytes")
        print("✓ 已保存为 test_psu_card.png")

    except Exception as e:
        print(f"✗ 错误: {e}")
