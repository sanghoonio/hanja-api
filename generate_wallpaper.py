#!/usr/bin/env python3
"""
Generate a wallpaper with a Chinese character, Korean equivalent, pinyin, and English definition.
"""

import json
import random
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Optional

import svgwrite
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---

IPHONE_RESOLUTIONS = {
    "iphone_13_mini": (1080, 2340),
    "iphone_13": (1170, 2532),
    "iphone_13_pro": (1170, 2532),
    "iphone_13_pro_max": (1284, 2778),
    "iphone_14": (1170, 2532),
    "iphone_14_plus": (1284, 2778),
    "iphone_14_pro": (1179, 2556),
    "iphone_14_pro_max": (1290, 2796),
    "iphone_15": (1179, 2556),
    "iphone_15_plus": (1290, 2796),
    "iphone_15_pro": (1179, 2556),
    "iphone_15_pro_max": (1290, 2796),
    "iphone_16": (1179, 2556),
    "iphone_16_plus": (1290, 2796),
    "iphone_16_pro": (1206, 2622),
    "iphone_16_pro_max": (1320, 2868),
}

# Base sizes for 1080x2340 resolution
BASE_RESOLUTION = (1080, 2340)
BASE_FONT_SIZES = {
    "character": 310,
    "korean": 120,
    "pinyin": 72,
    "definition": 60,
}

# Colors
BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#F0F0F0"
SECONDARY_COLOR = "#B4B4BE"

# Font paths
SCRIPT_DIR = Path(__file__).parent
CHINESE_FONT = str(SCRIPT_DIR / "fonts" / "HinaMincho-Regular.ttf")
JAPANESE_FONT = str(SCRIPT_DIR / "fonts" / "HinaMincho-Regular.ttf")
KOREAN_FONT = str(SCRIPT_DIR / "fonts" / "Dongle-Regular.ttf")
LATIN_FONT = str(SCRIPT_DIR / "fonts" / "WDXLLubrifontSC-Regular.ttf")

# --- Helper Functions ---

def wrap_text_svg(text: str, font_size: int, max_width: int, char_width_ratio: float = 0.5) -> list[str]:
    """Wrap text for SVG based on estimated character width."""
    avg_char_width = font_size * char_width_ratio
    max_chars = int(max_width / avg_char_width)

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text to fit within a maximum width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def get_character_data(character_list: str, character_id: Optional[int] = None) -> dict:
    """Load character data from the specified JSON file."""
    filename = f"data/{character_list}_characters.json"
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)["characters"]

    if character_id is None:
        return random.choice(data)
    else:
        for char_data in data:
            if char_data["id"] == character_id:
                return char_data
        raise ValueError(f"Character ID {character_id} not found in {character_list}")

def get_scaled_fonts(scale_factor: float, character_list: str = "hanja") -> dict:
    """Get fonts with sizes scaled proportionally."""
    # Use Japanese font for hanja characters, Chinese font for HSK
    char_font = JAPANESE_FONT if character_list == "hanja" else CHINESE_FONT
    
    return {
        "character": ImageFont.truetype(char_font, int(BASE_FONT_SIZES["character"] * scale_factor)),
        "korean": ImageFont.truetype(KOREAN_FONT, int(BASE_FONT_SIZES["korean"] * scale_factor)),
        "pinyin": ImageFont.truetype(LATIN_FONT, int(BASE_FONT_SIZES["pinyin"] * scale_factor)),
        "definition": ImageFont.truetype(LATIN_FONT, int(BASE_FONT_SIZES["definition"] * scale_factor)),
    }

# --- Output Generation (In-Memory) ---

def generate_png_bytes(char_data: dict, width: int, height: int, scale_factor: float, character_list: str = "hanja") -> BytesIO:
    """Generate the wallpaper as PNG in memory."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    fonts = get_scaled_fonts(scale_factor, character_list)

    center_y = height // 2 - int(100 * scale_factor)

    # Layout and draw text
    character_bbox = draw.textbbox((0, 0), char_data["character"], font=fonts["character"])
    character_width = character_bbox[2] - character_bbox[0]
    character_height = character_bbox[3] - character_bbox[1]
    char_x = (width - character_width) // 2
    char_y = center_y - character_height // 2
    draw.text((char_x, char_y), char_data["character"], font=fonts["character"], fill=TEXT_COLOR)

    y_cursor = char_y + character_height + int(140 * scale_factor)

    pinyin_bbox = draw.textbbox((0, 0), char_data["pinyin"], font=fonts["pinyin"])
    pinyin_width = pinyin_bbox[2] - pinyin_bbox[0]
    pinyin_height = pinyin_bbox[3] - pinyin_bbox[1]
    pinyin_x = (width - pinyin_width) // 2
    draw.text((pinyin_x, y_cursor), char_data["pinyin"], font=fonts["pinyin"], fill=SECONDARY_COLOR)
    y_cursor += pinyin_height + int(90 * scale_factor)

    if char_data.get("korean"):
        korean_bbox = draw.textbbox((0, 0), char_data["korean"], font=fonts["korean"])
        korean_width = korean_bbox[2] - korean_bbox[0]
        korean_height = korean_bbox[3] - korean_bbox[1]
        korean_x = (width - korean_width) // 2
        draw.text((korean_x, y_cursor), char_data["korean"], font=fonts["korean"], fill=SECONDARY_COLOR)
        y_cursor += korean_height + int(70 * scale_factor)

    max_text_width = int(width * 0.85)
    definition_lines = wrap_text(char_data["definition"], fonts["definition"], max_text_width, draw)
    line_height = int(BASE_FONT_SIZES["definition"] * scale_factor * 1.3)

    for line in definition_lines:
        line_bbox = draw.textbbox((0, 0), line, font=fonts["definition"])
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        draw.text((line_x, y_cursor), line, font=fonts["definition"], fill=SECONDARY_COLOR)
        y_cursor += line_height

    # Save to BytesIO instead of file
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def generate_svg_string(char_data: dict, width: int, height: int, scale_factor: float, character_list: str = "hanja") -> str:
    """Generate the wallpaper as SVG string."""
    dwg = svgwrite.Drawing(size=(width, height), profile="full")
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=BACKGROUND_COLOR))

    # Use appropriate font family for character
    char_font_family = "HinaMincho-Regular" if character_list == "hanja" else "YRDZST-Medium"

    center_y = height // 2 - int(100 * scale_factor)
    y_cursor = center_y

    # Add text elements
    char_font_size = int(BASE_FONT_SIZES["character"] * scale_factor)
    dwg.add(dwg.text(char_data["character"], insert=(width / 2, y_cursor),
                     font_family=char_font_family, font_size=char_font_size,
                     fill=TEXT_COLOR, text_anchor="middle", dominant_baseline="middle"))
    y_cursor += char_font_size / 2 + int(100 * scale_factor)

    pinyin_font_size = int(BASE_FONT_SIZES["pinyin"] * scale_factor)
    dwg.add(dwg.text(char_data["pinyin"], insert=(width / 2, y_cursor),
                     font_family="Dongle-Light", font_size=pinyin_font_size,
                     fill=SECONDARY_COLOR, text_anchor="middle", dominant_baseline="middle"))
    y_cursor += pinyin_font_size + int(40 * scale_factor)

    if char_data.get("korean"):
        korean_font_size = int(BASE_FONT_SIZES["korean"] * scale_factor)
        dwg.add(dwg.text(char_data["korean"], insert=(width / 2, y_cursor),
                         font_family="Dongle-Regular", font_size=korean_font_size,
                         fill=SECONDARY_COLOR, text_anchor="middle", dominant_baseline="middle"))
        y_cursor += korean_font_size + int(20 * scale_factor)

    definition_font_size = int(BASE_FONT_SIZES["definition"] * scale_factor)
    max_text_width = int(width * 0.85)
    definition_lines = wrap_text_svg(char_data["definition"], definition_font_size, max_text_width)
    line_height = int(definition_font_size * 1.3)

    for line in definition_lines:
        dwg.add(dwg.text(line, insert=(width / 2, y_cursor),
                         font_family="Dongle-Light", font_size=definition_font_size,
                         fill=SECONDARY_COLOR, text_anchor="middle", dominant_baseline="middle"))
        y_cursor += line_height

    return dwg.tostring()

def generate_xml_string(char_data: dict, width: int, height: int, model: str, character_list: str = "hanja") -> str:
    """Generate an XML string with character data."""
    root = ET.Element("wallpaper")
    ET.SubElement(root, "character", id=str(char_data["id"])).text = char_data["character"]
    ET.SubElement(root, "pinyin").text = char_data["pinyin"]
    if char_data.get("korean"):
        ET.SubElement(root, "korean").text = char_data["korean"]
    ET.SubElement(root, "definition").text = char_data["definition"]
    ET.SubElement(root, "resolution", width=str(width), height=str(height), model=model)

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)
