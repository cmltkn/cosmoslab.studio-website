import os
import json
import re  # Regex kütüphanesini ekledik

# --- AYARLAR ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
OUTPUT_FILE = os.path.join(ROOT_DIR, "content.js")

# --- SABİT İÇERİKLER ---
STATIC_DATA = {
    "header": {
        "title": "COSMOS.LAB STUDIO",
        "menu": [
            {"text": "VISION", "link": "#about-section"},      # Menüde VISION yazacak
            {"text": "PORTFOLIO", "link": "#projects-section"}, # Menüde PORTFOLIO yazacak
            {"text": "TECHNOLOGY", "link": "#automation-section"}, # Menüde TECHNOLOGY yazacak
            {"text": "CONTACT", "link": "#contact-section"}
        ]
    },
   "about": {
        "whoWeAreTitle": "WHO WE ARE",  # Ana Başlık sabit kaldı
        # Metnin en başına kalın harflerle veya büyük harflerle vurguyu ekliyoruz:
        "whoWeAreText": "BIM SOLUTION PARTNER & TECHNICAL LEADERSHIP. We are not just architects; we are the technical backbone of complex construction projects. Acting as a BIM Solution Partner, we bridge the gap between architectural intent and engineering reality. By integrating Computational Design with ISO 19650 standards, we deliver conflict-free, fabrication-ready models (LOD 400) where data accuracy is guaranteed by algorithms, not just human effort.",
        
        "whatWeDoTitle": "WHAT WE DO", # Ana Başlık sabit kaldı
        # Yine metnin girişinde teknik vurguyu yapıyoruz:
        "whatWeDoText": "COMPUTATIONAL DELIVERY & ALGORITHMIC AUDITING. We replace manual drafting with Digital Workflows and Algorithmic Auditing. Our expertise covers Advanced BIM Coordination (Clash Detection), Automated Documentation via Revit API, and Complex Geometry Rationalization. Whether it's a high-rise facade or a hospital's MEP coordination, we use Python and Dynamo scripts to ensure speed, precision, and scalability beyond traditional limits."
    },
    "automation_info": {
        "title": "ALGORITHMIC PRECISION & R&D", # Teknoloji bölümünün başlığı
        "description": "We don't just use software; we build tools. Our custom scripts and R&D solutions eliminate manual errors and optimize project timelines."
    },
    "contact": {
        "email": "hello@cosmoslab.studio",
        "phone": "+90 546 662 49 68",
        "location": "Global Service / Based in Ankara"
    }
}

def get_files_from_folder(folder_path):
    """Resim ve Video dosyalarını bulur."""
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}
    files_list = []
    
    if not os.path.exists(folder_path):
        return []

    files = sorted(os.listdir(folder_path))
    
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            abs_file_path = os.path.join(folder_path, f)
            rel_path = os.path.relpath(abs_file_path, ROOT_DIR)
            web_path = rel_path.replace("\\", "/") 
            files_list.append(web_path)
    return files_list

def scan_category(category_name):
    base_path = os.path.join(ASSETS_DIR, category_name)
    items = []

    if not os.path.exists(base_path):
        print(f"UYARI: '{category_name}' klasörü bulunamadı.")
        return []

    folders = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

    for folder in folders:
        full_path = os.path.join(base_path, folder)
        media_files = get_files_from_folder(full_path)
        
        if media_files:
            # --- GELİŞMİŞ TEMİZLİK (REGEX) ---
            # 1. Adım: Klasör isminin başındaki sayıları ve tireleri (örn: "01_", "02_") sil.
            clean_title = re.sub(r'^[\d_]+', '', folder)
            
            # 2. Adım: Geriye kalan kelimelerin arasındaki alt tireleri (_) boşluğa çevir.
            clean_title = clean_title.replace("_", " ")
            
            # 3. Adım: Hepsini büyük harf yap.
            clean_title = clean_title.upper()
            
            items.append({
                "images": media_files,
                "title": clean_title
            })
    return items

def main():
    print("--- Cosmos Lab Site Güncelleyici v5 (Final Fix) ---")
    print(f"Çalışma Konumu: {ROOT_DIR}")
    
    print("Projeler taranıyor...")
    projects = scan_category("projects")
    
    print("Otomasyonlar taranıyor...")
    automation_items = scan_category("automation")

    site_content = {
        "header": STATIC_DATA["header"],
        "about": STATIC_DATA["about"],
        "projects": projects,
        "automation": {
            "title": STATIC_DATA["automation_info"]["title"],
            "description": STATIC_DATA["automation_info"]["description"],
            "items": automation_items
        },
        "contact": STATIC_DATA["contact"]
    }

    js_content = f"const siteContent = {json.dumps(site_content, indent=4, ensure_ascii=False)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"BAŞARILI: content.js güncellendi. Tüm alt tireler temizlendi.")

if __name__ == "__main__":
    main()