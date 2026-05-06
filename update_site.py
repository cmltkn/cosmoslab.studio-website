import os
import json

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
    """Belirli bir dil için doğru dosyaları seçer."""
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}
    selected_files = []
    
    if not os.path.exists(folder_path):
        return []

    all_files = sorted(os.listdir(folder_path))
    file_groups = {}

    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in valid_extensions:
            continue
            
        name_no_ext = os.path.splitext(f)[0]
        parts = name_no_ext.rsplit('_', 1)
        suffix = parts[1] if len(parts) > 1 and len(parts[1]) == 2 else None
        base_name = parts[0] if suffix else name_no_ext
        
        if base_name not in file_groups:
            file_groups[base_name] = {}
        
        if suffix:
            file_groups[base_name][suffix] = f
        else:
            file_groups[base_name]["base"] = f

    for base_name, variants in file_groups.items():
        chosen_file = None
        if lang_code in variants:
            chosen_file = variants[lang_code]
        elif "base" in variants:
            chosen_file = variants["base"]
        elif "en" in variants:
            chosen_file = variants["en"]
            
        if chosen_file:
            abs_path = os.path.join(folder_path, chosen_file)
            rel_path = os.path.relpath(abs_path, ROOT_DIR)
            selected_files.append(rel_path.replace("\\", "/"))
            
    return sorted(selected_files)

# --- YENİ EKLENEN AKILLI FORMATLAYICI FONKSİYON ---
def format_case_study(file_path):
    """TXT dosyasını okuyup profesyonel mimari dergi formatına (HTML) çevirir."""
    if not os.path.exists(file_path):
        return ""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    formatted_html = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue # Boş satırları atla

        # 1. BAŞLIKLAR (Eğer satır tamamen büyük harfse ve 5 karakterden uzunsa)
        if line.isupper() and len(line) > 5:
            formatted_html += f"<br><br><h3 style='color:#fff; margin-bottom:10px; border-bottom:1px solid #333; padding-bottom:5px;'>{line}</h3>"
        
        # 2. KÜNYE BİLGİLERİ (İki nokta üst üste var ve ilk kısım kısa bir kelimeyse)
        elif ":" in line and len(line.split(":")[0]) < 30:
            key, value = line.split(":", 1)
            formatted_html += f"<b>{key}:</b>{value}<br>"
        
        # 3. MADDELER (Tire veya yıldız ile başlayanlar)
        elif line.startswith(("-", "•", "*")):
            formatted_html += f"<br><b>•</b> {line[1:].strip()}<br>"
            
        # 4. NORMAL PARAGRAF
        else:
            formatted_html += f"{line}<br><br>"
            
    # En baştaki gereksiz boşluğu (ilk satır boşluklarını) temizle
    if formatted_html.startswith("<br><br>"):
        formatted_html = formatted_html[8:]
        
    # JavaScript'in bozulmaması için tırnak işaretlerini kaçış karakteriyle koru
    return formatted_html.replace("'", "\\'")

def scan_category(category_name, lang_code):
    base_path = os.path.join(ASSETS_DIR, category_name)
    items = []

    if not os.path.exists(base_path):
        print(f"UYARI: '{category_name}' klasörü bulunamadı.")
        return []

    folders = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

    for folder in folders:
        full_path = os.path.join(base_path, folder)
        media_files = get_files_for_language(full_path, lang_code)
        
        # --- ESKİ DÜZ OKUMA YERİNE, YENİ AKILLI FONKSİYONU ÇAĞIRIYORUZ ---
        txt_path_tr = os.path.join(full_path, "info_tr.txt")
        text_tr = format_case_study(txt_path_tr)

        txt_path_en = os.path.join(full_path, "info_en.txt")
        text_en = format_case_study(txt_path_en)
        # ------------------------------------------------------------------
        
        if media_files:
            clean_title = folder.split("_", 1)[-1] if "_" in folder else folder
            clean_title = clean_title.upper()
            
            thumbnail = media_files[0]
            case_images = media_files[1:] if len(media_files) > 1 else []
            
            items.append({
                "title": clean_title,
                "thumbnail": thumbnail,
                "case_images": case_images,
                "description_tr": text_tr,
                "description_en": text_en
            })
    return items

def main():
    print("--- Cosmos Lab Multi-Language Builder ---")
    all_texts = load_language_files()
    
    if not all_texts:
        print("Kritik Hata: Hiçbir dil dosyası bulunamadı!")
        return

    final_content = {}

    for lang_code, text_data in all_texts.items():
        print(f"[{lang_code.upper()}] İçerik oluşturuluyor...")
        
        # YENİ: whatwedo klasöründeki ilk görseli otomatik bul
        wwd_path = os.path.join(ASSETS_DIR, "whatwedo")
        wwd_img = ""
        if os.path.exists(wwd_path):
            files = [f for f in os.listdir(wwd_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            if files:
                wwd_img = f"assets/whatwedo/{files[0]}"

        projects = scan_category("projects", lang_code)
        team = scan_category("team", lang_code)
        automation = scan_category("automation", lang_code)
        
        final_content[lang_code] = {
            "header": text_data.get("header", {}),
            "about": {
                **text_data.get("about", {}),
                "whatWeDoImage": wwd_img # Otomatik bulunan görsel yolu buraya ekleniyor
            },
            "projects": projects,
            "team": team,
            "automation": {
                "title": text_data.get("automation_info", {}).get("title", ""),
                "description": text_data.get("automation_info", {}).get("description", ""),
                "items": automation
            },
            "contact": text_data.get("contact", {}),
            "ui": text_data.get("ui", {})
        }

    js_content = f"const siteContent = {json.dumps(final_content, indent=4, ensure_ascii=False)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"BAŞARILI: content.js güncellendi. {len(final_content)} dil eklendi.")

if __name__ == "__main__":
    main()