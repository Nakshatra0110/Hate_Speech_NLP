import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"

def get_font(size: int = 32, is_hindi: bool = False, bold: bool = True):
    if is_hindi:
        hindi_font = FONTS_DIR / "Nirmala.ttc"
        if hindi_font.exists():
            try:
                return ImageFont.truetype(str(hindi_font), size)
            except Exception:
                pass
    if bold:
        arialbd = FONTS_DIR / "arialbd.ttf"
        if arialbd.exists():
            try:
                return ImageFont.truetype(str(arialbd), size)
            except Exception:
                pass
        impact = FONTS_DIR / "impact.ttf"
        if impact.exists():
            try:
                return ImageFont.truetype(str(impact), size)
            except Exception:
                pass
    arial = FONTS_DIR / "arial.ttf"
    if arial.exists():
        try:
            return ImageFont.truetype(str(arial), size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_banner_text(draw: ImageDraw.ImageDraw, text: str, pos: tuple, font: ImageFont.ImageFont,
                     text_color=(0, 0, 0), bg_color=(255, 255, 255), border_color=(0, 0, 0),
                     padding=(16, 8), center: bool = True):
    """Draws clean, high-contrast banner text optimized for human reading and EasyOCR recognition."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return
    x_center, y = pos
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x1 = x_center - (tw // 2) - padding[0] if center else x_center - padding[0]
        y1 = y - padding[1]
        x2 = x1 + tw + 2 * padding[0]
        y2 = y1 + th + 2 * padding[1]
        
        # Solid rectangular plate with clean border
        draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color, width=3)
        draw.text((x1 + padding[0], y1 + padding[1]), line, font=font, fill=text_color)
        y += th + 2 * padding[1] + 10

def generate_drake_template(out_path: str):
    """Template 1: Drake Hotline Bling (Rejecting Hate vs Embracing Respect)."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (245, 245, 248))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 298], fill=(235, 235, 240))
    draw.rectangle([0, 302, w, h], fill=(250, 250, 252))
    draw.line([(0, 300), (w, 300)], fill=(80, 80, 90), width=4)
    draw.line([(300, 0), (300, h)], fill=(80, 80, 90), width=4)

    # Top Panel Left (Drake Rejecting)
    draw.rectangle([10, 10, 290, 290], fill=(225, 220, 210))
    draw.ellipse([110, 50, 190, 130], fill=(160, 110, 80))
    draw.rectangle([110, 100, 190, 135], fill=(50, 30, 20)) # beard
    draw.ellipse([115, 60, 185, 95], fill=(30, 20, 15)) # hair
    draw.polygon([(200, 120), (270, 70), (250, 50), (180, 100)], fill=(160, 110, 80)) # waving hand
    draw.polygon([(60, 135), (240, 135), (280, 280), (20, 280)], fill=(245, 130, 32)) # orange coat
    draw.line([(135, 80), (150, 85)], fill=(30, 20, 15), width=3)
    draw.line([(155, 85), (170, 80)], fill=(30, 20, 15), width=3)

    # Top Panel Right: Text rejecting hate
    font = get_font(size=30, bold=True)
    draw_banner_text(draw, "SPREADING HATE SPEECH\nAND TOXIC SLURS", (550, 90), font, text_color=(180, 20, 20), bg_color=(255, 240, 240), border_color=(217, 45, 32))

    # Bottom Panel Left (Drake Approving)
    draw.rectangle([10, 310, 290, 590], fill=(230, 235, 240))
    draw.ellipse([110, 350, 190, 430], fill=(160, 110, 80))
    draw.rectangle([110, 400, 190, 435], fill=(50, 30, 20)) # beard
    draw.ellipse([115, 360, 185, 395], fill=(30, 20, 15)) # hair
    draw.polygon([(60, 435), (240, 435), (280, 580), (20, 580)], fill=(245, 130, 32))
    draw.polygon([(180, 440), (280, 400), (270, 380), (170, 420)], fill=(160, 110, 80))
    draw.rectangle([270, 385, 290, 395], fill=(160, 110, 80))
    draw.arc([135, 385, 165, 405], start=0, end=180, fill=(30, 20, 15), width=3)

    # Bottom Panel Right: Text approving solidarity
    draw_banner_text(draw, "NO ROOM FOR RACISM\nEQUALITY FOR ALL", (550, 390), font, text_color=(15, 100, 60), bg_color=(240, 255, 245), border_color=(26, 127, 90))

    img.save(out_path, quality=95)
    print(f"Generated Drake template: {out_path}")

def generate_two_buttons_template(out_path: str):
    """Template 2: Two Buttons / Daily Struggle (Sweating Character)."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (220, 225, 230))
    draw = ImageDraw.Draw(img)

    # Control console
    draw.polygon([(80, 20), (720, 20), (780, 250), (20, 250)], fill=(180, 190, 200), outline=(60, 70, 80), width=4)

    # Button 1 (Left - Red)
    draw.ellipse([120, 50, 340, 180], fill=(217, 45, 32), outline=(140, 20, 15), width=6)
    font_btn = get_font(size=24, bold=True)
    draw_banner_text(draw, "SPREAD HATE\nAND SLURS", (230, 85), font_btn, text_color=(255, 255, 255), bg_color=(180, 20, 20), border_color=(255, 255, 255))

    # Button 2 (Right - Green)
    draw.ellipse([460, 50, 680, 180], fill=(26, 127, 90), outline=(15, 80, 50), width=6)
    draw_banner_text(draw, "KINDNESS IS\nCONTAGIOUS", (570, 85), font_btn, text_color=(255, 255, 255), bg_color=(20, 110, 60), border_color=(255, 255, 255))

    # Lower half: Sweating character
    draw.rectangle([0, 250, w, h], fill=(240, 240, 245))
    draw.line([(0, 250), (w, 250)], fill=(60, 70, 80), width=4)

    # Superhero suit & head
    draw.ellipse([260, 380, 540, 700], fill=(30, 80, 180))
    draw.ellipse([320, 290, 480, 460], fill=(245, 200, 170))
    draw.arc([320, 290, 480, 460], start=180, end=360, fill=(217, 45, 32), width=25)
    # Eyes
    draw.ellipse([350, 360, 385, 385], fill=(255, 255, 255))
    draw.ellipse([360, 365, 375, 380], fill=(20, 20, 20))
    draw.ellipse([415, 360, 450, 385], fill=(255, 255, 255))
    draw.ellipse([425, 365, 440, 380], fill=(20, 20, 20))
    # Sweat drops
    draw.ellipse([455, 330, 470, 355], fill=(80, 170, 240))
    # Towel
    draw.ellipse([440, 300, 520, 380], fill=(250, 250, 250), outline=(180, 180, 190), width=2)

    font_caption = get_font(size=30, bold=True)
    draw_banner_text(draw, "PASS IT ON - CHOOSE RESPECT", (400, 520), font_caption, text_color=(20, 20, 20), bg_color=(255, 255, 255), border_color=(0, 0, 0))

    img.save(out_path, quality=95)
    print(f"Generated Two Buttons template: {out_path}")

def generate_distracted_boyfriend_template(out_path: str):
    """Template 3: Distracted Boyfriend Meme."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (230, 235, 240))
    draw = ImageDraw.Draw(img)

    # Street
    draw.rectangle([0, 0, w, 380], fill=(210, 215, 220))
    draw.rectangle([0, 380, w, h], fill=(160, 165, 170))

    # Left character: Girl walking by
    draw.ellipse([140, 120, 220, 200], fill=(240, 195, 165))
    draw.polygon([(110, 200), (250, 200), (280, 450), (90, 450)], fill=(217, 45, 32))
    draw.ellipse([130, 110, 210, 150], fill=(80, 40, 20))

    # Center character: Guy looking back
    draw.ellipse([370, 100, 460, 190], fill=(240, 195, 165))
    draw.polygon([(340, 190), (490, 190), (510, 470), (320, 470)], fill=(50, 110, 180))
    draw.ellipse([365, 90, 445, 130], fill=(40, 30, 20))

    # Right character: Shocked girlfriend
    draw.ellipse([600, 130, 680, 210], fill=(240, 195, 165))
    draw.polygon([(570, 210), (710, 210), (740, 460), (550, 460)], fill=(40, 140, 90))
    draw.ellipse([590, 120, 670, 160], fill=(100, 50, 20))

    font_label = get_font(size=24, bold=True)
    draw_banner_text(draw, "CHEAP HATE\nAND SLURS", (180, 280), font_label, text_color=(180, 20, 20), bg_color=(255, 255, 255), border_color=(217, 45, 32))
    draw_banner_text(draw, "ONLINE TROLLS", (415, 320), font_label, text_color=(20, 20, 20), bg_color=(255, 255, 255), border_color=(50, 110, 180))
    draw_banner_text(draw, "CIVIL DIALOGUE\nAND RESPECT", (640, 280), font_label, text_color=(15, 100, 60), bg_color=(255, 255, 255), border_color=(40, 140, 90))

    font_top = get_font(size=30, bold=True)
    draw_banner_text(draw, "READ BOOKS NOT HATE - KNOWLEDGE EMPOWERS", (400, 30), font_top, text_color=(20, 20, 20), bg_color=(255, 255, 255), border_color=(0, 0, 0))

    img.save(out_path, quality=95)
    print(f"Generated Distracted Boyfriend template: {out_path}")

def generate_hostile_vermin_template(out_path: str):
    """Template 4: Hostile Propaganda Dehumanizing Poster."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (40, 15, 15))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, w, 25], fill=(217, 45, 32))
    draw.rectangle([0, h-25, w, h], fill=(217, 45, 32))
    draw.rectangle([15, 15, w-15, h-15], outline=(217, 45, 32), width=5)

    # Hazard emblem
    draw.polygon([(400, 140), (560, 390), (240, 390)], fill=(217, 45, 32), outline=(255, 255, 255), width=4)
    draw.polygon([(400, 175), (520, 370), (280, 370)], fill=(20, 10, 10))
    draw.rectangle([390, 210, 410, 310], fill=(217, 45, 32))
    draw.ellipse([390, 330, 410, 350], fill=(217, 45, 32))

    font_hostile = get_font(size=44, bold=True)
    draw_banner_text(draw, "SUBHUMAN VERMIN", (400, 60), font_hostile, text_color=(255, 255, 255), bg_color=(180, 20, 20), border_color=(255, 255, 255))
    draw_banner_text(draw, "GET OUT OF OUR LAND", (400, 460), font_hostile, text_color=(255, 255, 255), bg_color=(180, 20, 20), border_color=(255, 255, 255))

    img.save(out_path, quality=95)
    print(f"Generated Hostile Vermin template: {out_path}")

def generate_hostile_parasite_template(out_path: str):
    """Template 5: Hostile Xenophobic Meme Poster."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (30, 20, 30))
    draw = ImageDraw.Draw(img)

    draw.rectangle([20, 20, w-20, h-20], outline=(180, 30, 30), width=4)
    draw.ellipse([300, 180, 500, 380], fill=(60, 20, 30), outline=(217, 45, 32), width=6)
    draw.line([(330, 210), (470, 350)], fill=(217, 45, 32), width=10)
    draw.line([(330, 350), (470, 210)], fill=(217, 45, 32), width=10)

    font_hostile = get_font(size=36, bold=True)
    draw_banner_text(draw, "PARASITES INFESTING OUR NATION", (400, 80), font_hostile, text_color=(255, 255, 255), bg_color=(160, 20, 20), border_color=(255, 255, 255))
    draw_banner_text(draw, "EXTERMINATE THEM", (400, 460), font_hostile, text_color=(255, 255, 255), bg_color=(180, 20, 20), border_color=(255, 255, 255))

    img.save(out_path, quality=95)
    print(f"Generated Hostile Parasite template: {out_path}")

def generate_desi_cricket_template(out_path: str):
    """Template 6: Desi Hinglish Meme (Cricket Passion & National Unity)."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (255, 250, 240))
    draw = ImageDraw.Draw(img)

    # Tricolor stripe
    draw.rectangle([0, 0, w, 15], fill=(245, 130, 32))
    draw.rectangle([0, 15, w, 30], fill=(255, 255, 255))
    draw.rectangle([0, 30, w, 45], fill=(26, 127, 90))

    # Stadium illustration
    draw.rectangle([40, 130, w-40, 430], fill=(70, 160, 90), outline=(50, 110, 60), width=4)
    draw.rectangle([340, 150, 460, 410], fill=(225, 200, 150), outline=(180, 150, 100), width=2)
    # Wickets
    draw.line([(390, 160), (390, 200)], fill=(255, 255, 255), width=4)
    draw.line([(400, 160), (400, 200)], fill=(255, 255, 255), width=4)
    draw.line([(410, 160), (410, 200)], fill=(255, 255, 255), width=4)
    # Ball
    draw.ellipse([490, 340, 520, 370], fill=(217, 45, 32))

    font_desi = get_font(size=40, bold=True)
    draw_banner_text(draw, "DESH KI SHAAN", (400, 70), font_desi, text_color=(245, 130, 32), bg_color=(255, 255, 255), border_color=(245, 130, 32))
    draw_banner_text(draw, "TEAMWORK AND PASSION OVER HATE", (400, 490), font_desi, text_color=(26, 127, 90), bg_color=(255, 255, 255), border_color=(26, 127, 90))

    img.save(out_path, quality=95)
    print(f"Generated Desi Cricket template: {out_path}")

def generate_hindi_unity_template(out_path: str):
    """Template 7: Devanagari Hindi Solidarity Poster Meme."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([20, 20, w-20, h-20], outline=(26, 127, 90), width=6)
    draw.rectangle([28, 28, w-28, h-28], outline=(245, 130, 32), width=3)

    draw.ellipse([270, 160, 530, 420], fill=(255, 248, 240), outline=(245, 130, 32), width=4)
    draw.ellipse([340, 240, 460, 340], fill=(26, 127, 90))
    draw.polygon([(400, 220), (440, 300), (360, 300)], fill=(255, 255, 255))

    font_hindi_top = get_font(size=38, is_hindi=True, bold=True)
    draw_banner_text(draw, "नफ़रत की कोई जगह नहीं", (400, 75), font_hindi_top, text_color=(180, 20, 20), bg_color=(255, 245, 245), border_color=(217, 45, 32))

    font_hindi_bot = get_font(size=32, is_hindi=True, bold=True)
    draw_banner_text(draw, "एकता और सद्भाव ही भारत की शक्ति है", (400, 485), font_hindi_bot, text_color=(15, 100, 60), bg_color=(240, 255, 245), border_color=(26, 127, 90))

    img.save(out_path, quality=95)
    print(f"Generated Hindi Unity template: {out_path}")

def generate_change_my_mind_template(out_path: str):
    """Template 8: Change My Mind Table Meme."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (235, 245, 250))
    draw = ImageDraw.Draw(img)

    # Park grass & trees
    draw.rectangle([0, 340, w, h], fill=(90, 160, 90))
    draw.rectangle([60, 90, 90, 340], fill=(120, 80, 50))
    draw.ellipse([20, 20, 130, 140], fill=(50, 120, 60))
    draw.rectangle([700, 110, 730, 340], fill=(120, 80, 50))
    draw.ellipse([660, 40, 770, 150], fill=(50, 120, 60))

    # Guy behind table
    draw.ellipse([360, 140, 440, 220], fill=(240, 195, 165))
    draw.ellipse([355, 130, 435, 170], fill=(60, 40, 30))
    draw.polygon([(340, 220), (460, 220), (490, 360), (310, 360)], fill=(40, 90, 160))

    # White Table & Banner
    draw.polygon([(120, 300), (680, 300), (710, 530), (90, 530)], fill=(255, 255, 255), outline=(50, 50, 60), width=4)
    # Coffee mug
    draw.rectangle([180, 270, 210, 310], fill=(217, 45, 32))
    draw.arc([165, 280, 185, 300], start=90, end=270, fill=(217, 45, 32), width=3)

    font_banner = get_font(size=26, bold=True)
    draw_banner_text(draw, "DIVERSITY AND EQUALITY\nMAKE OUR NATION STRONGER", (400, 350), font_banner, text_color=(20, 20, 20), bg_color=(255, 255, 255), border_color=(200, 200, 200))

    font_sub = get_font(size=34, bold=True)
    draw_banner_text(draw, "CHANGE MY MIND", (400, 460), font_sub, text_color=(245, 130, 32), bg_color=(255, 255, 255), border_color=(245, 130, 32))

    img.save(out_path, quality=95)
    print(f"Generated Change My Mind template: {out_path}")

if __name__ == "__main__":
    out_dir = Path("data/raw/images")
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_drake_template(str(out_dir / "meme_counter.png"))
    generate_two_buttons_template(str(out_dir / "meme_kindness.png"))
    generate_distracted_boyfriend_template(str(out_dir / "meme_education.png"))
    generate_hostile_vermin_template(str(out_dir / "meme_vermin.png"))
    generate_hostile_parasite_template(str(out_dir / "meme_parasite.png"))
    generate_desi_cricket_template(str(out_dir / "meme_cricket.png"))
    generate_hindi_unity_template(str(out_dir / "meme_hindi_civil.png"))
    generate_change_my_mind_template(str(out_dir / "meme_change_my_mind.png"))
    print("All 8 diverse meme templates successfully generated!")
