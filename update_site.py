import os
import json
import re

# --- AYARLAR ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
LANG_DIR = os.path.join(ROOT_DIR, "languages")
OUTPUT_FILE = os.path.join(ROOT_DIR, "content.js")

def load_language_files():
    """languages klasöründeki tüm .json dosyalarını okur."""
    lang_data = {}
    if not os.path.exists(LANG_DIR):
        print("HATA: 'languages' klasörü bulunamadı!")
        return {}
    
    for f in os.listdir(LANG_DIR):
        if f.endswith(".json"):
            lang_code = f.split(".")[0] # 'en.json' -> 'en'
            with open(os.path.join(LANG_DIR, f), "r", encoding="utf-8") as file:
                try:
                    lang_data[lang_code] = json.load(file)
                    print(f"Dil yüklendi: {lang_code}")
                except json.JSONDecodeError as e:
                    print(f"HATA: {f} dosyası bozuk JSON formatında! {e}")
    return lang_data

def get_files_for_language(folder_path, lang_code):
    """
    Belirli bir dil için doğru dosyaları seçer.
    Mantık:
    1. Önce dosya_adı_{lang_code}.png var mı diye bakar (örn: cv_tr.png).
    2. Yoksa, varsayılan (suffixsiz) dosyayı alır (örn: cv.png).
    3. Diğer dillerin dosyalarını (örn: cv_ru.png) görmezden gelir.
    """
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}
    selected_files = []
    
    if not os.path.exists(folder_path):
        return []

    all_files = sorted(os.listdir(folder_path))
    
    # Dosyaları grupla: { "cv": {"base": "cv.png", "tr": "cv_tr.png", "en": "cv_en.png"} }
    file_groups = {}

    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in valid_extensions:
            continue
            
        name_no_ext = os.path.splitext(f)[0]
        
        # Dil suffix'i var mı kontrol et (örn: image_tr)
        parts = name_no_ext.rsplit('_', 1)
        suffix = parts[1] if len(parts) > 1 and len(parts[1]) == 2 else None
        base_name = parts[0] if suffix else name_no_ext
        
        if base_name not in file_groups:
            file_groups[base_name] = {}
        
        if suffix:
            file_groups[base_name][suffix] = f
        else:
            file_groups[base_name]["base"] = f

    # Şimdi bu dil için en uygun dosyayı seç
    for base_name, variants in file_groups.items():
        chosen_file = None
        
        # 1. Öncelik: Tam dil eşleşmesi (örn: cv_tr.png)
        if lang_code in variants:
            chosen_file = variants[lang_code]
        # 2. Öncelik: Varsayılan dosya (örn: cv.png)
        elif "base" in variants:
            chosen_file = variants["base"]
        # 3. Öncelik: Eğer 'en' varsa ve biz base bulamadıysak fallback yap (opsiyonel)
        elif "en" in variants:
            chosen_file = variants["en"]
            
        if chosen_file:
            abs_path = os.path.join(folder_path, chosen_file)
            rel_path = os.path.relpath(abs_path, ROOT_DIR)
            selected_files.append(rel_path.replace("\\", "/"))
            
    return sorted(selected_files)

def scan_category(category_name, lang_code):
    base_path = os.path.join(ASSETS_DIR, category_name)
    items = []

    if not os.path.exists(base_path):
        return []

    folders = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

    for folder in folders:
        full_path = os.path.join(base_path, folder)
        # BURADA DİLE GÖRE FİLTRELEME YAPIYORUZ
        media_files = get_files_for_language(full_path, lang_code)
        
        if media_files:
            clean_title = re.sub(r'^[\d_]+', '', folder).replace("_", " ").upper()
            items.append({
                "images": media_files,
                "title": clean_title
            })
    return items

def main():
    print("--- Cosmos Lab Multi-Language Builder ---")
    
    # 1. Metin dosyalarını yükle (en.json, tr.json...)
    all_texts = load_language_files()
    
    if not all_texts:
        print("Kritik Hata: Hiçbir dil dosyası bulunamadı!")
        return

    final_content = {}

    # 2. Her dil için site içeriğini oluştur
    for lang_code, text_data in all_texts.items():
        print(f"[{lang_code.upper()}] İçerik oluşturuluyor...")
        
        projects = scan_category("projects", lang_code)
        team = scan_category("team", lang_code)
        automation = scan_category("automation", lang_code)
        
        # Metin verisiyle Asset verisini birleştir
        final_content[lang_code] = {
            "header": text_data.get("header", {}),
            "about": text_data.get("about", {}),
            "projects": projects,
            "team": team,
            "automation": {
                "title": text_data.get("automation_info", {}).get("title", ""),
                "description": text_data.get("automation_info", {}).get("description", ""),
                "items": automation
            },
            "contact": text_data.get("contact", {}),
            "ui": text_data.get("ui", {}) # UI metinleri (butonlar vs)
        }

    # 3. content.js dosyasına yaz
    js_content = f"const siteContent = {json.dumps(final_content, indent=4, ensure_ascii=False)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"BAŞARILI: content.js güncellendi. {len(final_content)} dil eklendi.")

if __name__ == "__main__":
    main()