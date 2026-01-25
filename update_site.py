import os
import json

# --- AYARLAR (TAŞINABİLİRLİK SİHRİ BURADA) ---
# __file__ : Bu betiğin dosya yolu
# os.path.dirname(...) : Bu betiğin içinde olduğu klasör
# Bu sayede klasörü nereye taşırsan taşı, ROOT_DIR orası olur.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
OUTPUT_FILE = os.path.join(ROOT_DIR, "content.js")

# --- SABİT İÇERİKLER ---
STATIC_DATA = {
    "header": {
        "title": "COSMOS.LAB STUDIO",
        "menu": [
            {"text": "WHO WE ARE", "link": "#about-section"},
            {"text": "PROJECTS", "link": "#projects-section"},
            {"text": "AUTOMATION", "link": "#automation-section"},
            {"text": "CONTACT", "link": "#contact-section"}
        ]
    },
    "about": {
        "whoWeAreTitle": "WHO WE ARE",
        "whoWeAreText": "We are a multidisciplinary design studio redefining architectural boundaries. By merging computational design with traditional craftsmanship, we create spaces that are not just built, but calculated, optimized, and alive.",
        "whatWeDoTitle": "WHAT WE DO",
        "whatWeDoText": "We specialize in Digital Workflows, Project Automation, and Generative Design. From Python scripts automating Revit tasks to complex grasshopper definitions for facade optimization, we bridge the gap between code and concrete."
    },
    "automation_info": {
        "title": "DIGITAL WORKFLOWS & PROJECT AUTOMATION",
        "description": "Custom scripts, Grasshopper definitions, and Revit API solutions."
    },
    "contact": {
        "email": "hello@cosmoslab.studio",
        "location": "Ankara, Turkey"
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
            # Dosyanın tam yolu
            abs_file_path = os.path.join(folder_path, f)
            
            # ROOT_DIR'a göre göreceli yolunu al (Örn: C:\...\assets\img.jpg -> assets\img.jpg)
            rel_path = os.path.relpath(abs_file_path, ROOT_DIR)
            
            # Windows ters slash'lerini (\\) web için düz slash (/) yap
            web_path = rel_path.replace("\\", "/") 
            files_list.append(web_path)
    return files_list

def scan_category(category_name):
    base_path = os.path.join(ASSETS_DIR, category_name)
    items = []

    if not os.path.exists(base_path):
        print(f"UYARI: '{category_name}' klasörü bulunamadı. Beklenen yol: {base_path}")
        return []

    # Sadece klasörleri al
    folders = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

    for folder in folders:
        full_path = os.path.join(base_path, folder)
        media_files = get_files_from_folder(full_path)
        
        if media_files:
            # Klasör adını temizle (örn: 01_Project -> PROJECT)
            clean_title = folder.split("_", 1)[-1] if "_" in folder else folder
            clean_title = clean_title.upper()
            
            items.append({
                "images": media_files,
                "title": clean_title
            })
    return items

def main():
    print("--- Cosmos Lab Site Güncelleyici v3 (Portable) ---")
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
    
    print(f"BAŞARILI: content.js güncellendi.")
    print(f"Bulunan: {len(projects)} proje, {len(automation_items)} otomasyon.")

if __name__ == "__main__":
    main()