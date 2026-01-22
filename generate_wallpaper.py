#!/usr/bin/env python3
"""
Generate a wallpaper with a Chinese character, Korean equivalent, pinyin, and English definition.
"""

import json
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal, Optional

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
    "character": 360,
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
CHINESE_FONT = str(SCRIPT_DIR / "fonts" / "YRDZST-Medium.ttf")
# CHINESE_FONT = str(SCRIPT_DIR / "fonts" / "MaShanZheng-Regular.ttf")
KOREAN_FONT = str(SCRIPT_DIR / "fonts" / "Dongle-Regular.ttf")
# LATIN_FONT = str(SCRIPT_DIR / "fonts" / "Dongle-Regular.ttf")
LATIN_FONT = str(SCRIPT_DIR / "fonts" / "YRDZST-Medium.ttf")

# --- Helper Functions ---

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

def get_scaled_fonts(scale_factor: float) -> dict:
    """Get fonts with sizes scaled proportionally."""
    return {
        "character": ImageFont.truetype(CHINESE_FONT, int(BASE_FONT_SIZES["character"] * scale_factor)),
        "korean": ImageFont.truetype(KOREAN_FONT, int(BASE_FONT_SIZES["korean"] * scale_factor)),
        "pinyin": ImageFont.truetype(LATIN_FONT, int(BASE_FONT_SIZES["pinyin"] * scale_factor)),
        "definition": ImageFont.truetype(LATIN_FONT, int(BASE_FONT_SIZES["definition"] * scale_factor)),
    }

# --- Output Generation ---

def _generate_png(output_path: str, char_data: dict, width: int, height: int, scale_factor: float):
    """Generate the wallpaper as a PNG image."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    fonts = get_scaled_fonts(scale_factor)

    center_y = height // 2 - int(100 * scale_factor)
    total_text_height = 0

    # Layout and draw text
    character_bbox = draw.textbbox((0, 0), char_data["character"], font=fonts["character"])
    character_width = character_bbox[2] - character_bbox[0]
    character_height = character_bbox[3] - character_bbox[1]
    char_x = (width - character_width) // 2
    char_y = center_y - character_height // 2
    draw.text((char_x, char_y), char_data["character"], font=fonts["character"], fill=TEXT_COLOR)
    total_text_height += character_height

    y_cursor = char_y + character_height + int(96 * scale_factor)

    pinyin_bbox = draw.textbbox((0, 0), char_data["pinyin"], font=fonts["pinyin"])
    pinyin_width = pinyin_bbox[2] - pinyin_bbox[0]
    pinyin_height = pinyin_bbox[3] - pinyin_bbox[1]
    pinyin_x = (width - pinyin_width) // 2
    draw.text((pinyin_x, y_cursor), char_data["pinyin"], font=fonts["pinyin"], fill=SECONDARY_COLOR)
    y_cursor += pinyin_height + int(68 * scale_factor)

    if char_data.get("korean"):
        korean_bbox = draw.textbbox((0, 0), char_data["korean"], font=fonts["korean"])
        korean_width = korean_bbox[2] - korean_bbox[0]
        korean_height = korean_bbox[3] - korean_bbox[1]
        korean_x = (width - korean_width) // 2
        draw.text((korean_x, y_cursor), char_data["korean"], font=fonts["korean"], fill=SECONDARY_COLOR)
        y_cursor += korean_height + int(60 * scale_factor)

    definition_bbox = draw.textbbox((0, 0), char_data["definition"], font=fonts["definition"])
    definition_width = definition_bbox[2] - definition_bbox[0]
    definition_x = (width - definition_width) // 2
    draw.text((definition_x, y_cursor), char_data["definition"], font=fonts["definition"], fill=SECONDARY_COLOR)

    img.save(output_path, "PNG")

def _generate_svg(output_path: str, char_data: dict, width: int, height: int, scale_factor: float):
    """Generate the wallpaper as an SVG image."""
    dwg = svgwrite.Drawing(output_path, size=(width, height), profile="tiny")
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=BACKGROUND_COLOR))

    center_y = height // 2 - int(100 * scale_factor)
    y_cursor = center_y

    # Add text elements
    char_font_size = int(BASE_FONT_SIZES["character"] * scale_factor)
    dwg.add(dwg.text(char_data["character"], insert=(width / 2, y_cursor),
                     font_family="YRDZST-Medium", font_size=char_font_size,
                     fill=TEXT_COLOR, text_anchor="middle", alignment_baseline="middle"))
    y_cursor += char_font_size / 2 + int(100 * scale_factor)

    pinyin_font_size = int(BASE_FONT_SIZES["pinyin"] * scale_factor)
    dwg.add(dwg.text(char_data["pinyin"], insert=(width / 2, y_cursor),
                     font_family="Dongle-Light", font_size=pinyin_font_size,
                     fill=SECONDARY_COLOR, text_anchor="middle", alignment_baseline="middle"))
    y_cursor += pinyin_font_size + int(40 * scale_factor)

    if char_data.get("korean"):
        korean_font_size = int(BASE_FONT_SIZES["korean"] * scale_factor)
        dwg.add(dwg.text(char_data["korean"], insert=(width / 2, y_cursor),
                         font_family="Dongle-Regular", font_size=korean_font_size,
                         fill=SECONDARY_COLOR, text_anchor="middle", alignment_baseline="middle"))
        y_cursor += korean_font_size + int(20 * scale_factor)

    definition_font_size = int(BASE_FONT_SIZES["definition"] * scale_factor)
    dwg.add(dwg.text(char_data["definition"], insert=(width / 2, y_cursor),
                     font_family="Dongle-Light", font_size=definition_font_size,
                     fill=SECONDARY_COLOR, text_anchor="middle", alignment_baseline="middle"))

    dwg.save()

def _generate_xml(output_path: str, char_data: dict, width: int, height: int, model: str):
    """Generate an XML file with character data."""
    root = ET.Element("wallpaper")
    ET.SubElement(root, "character", id=str(char_data["id"])).text = char_data["character"]
    ET.SubElement(root, "pinyin").text = char_data["pinyin"]
    if char_data.get("korean"):
        ET.SubElement(root, "korean").text = char_data["korean"]
    ET.SubElement(root, "definition").text = char_data["definition"]
    ET.SubElement(root, "resolution", width=str(width), height=str(height), model=model)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

# --- Main Function ---

def generate_wallpaper(
    output_path: str = "wallpaper.png",
    character_id: Optional[int] = None,
    iphone_model: str = "iphone_13_mini",
    output_type: Literal["png", "svg", "xml"] = "png",
    character_list: Literal["hsk", "hanja"] = "hsk",
) -> str:
    """
    Generate a wallpaper or data file with a character and its definitions.

    Args:
        output_path: The path to save the output file.
        character_id: The ID of the character to use. If None, a random character is chosen.
        iphone_model: The iPhone model to generate the resolution for.
        output_type: The type of output to generate ("png", "svg", "xml").
        character_list: The character list to use ("hsk" or "hanja").

    Returns:
        A confirmation message with the path to the generated file.
    """
    # Validate parameters
    if iphone_model not in IPHONE_RESOLUTIONS:
        raise ValueError(f"Invalid iPhone model: {iphone_model}. See IPHONE_RESOLUTIONS for options.")
    if output_type not in ["png", "svg", "xml"]:
        raise ValueError(f"Invalid output type: {output_type}. Must be 'png', 'svg', or 'xml'.")
    if character_list not in ["hsk", "hanja"]:
        raise ValueError(f"Invalid character list: {character_list}. Must be 'hsk' or 'hanja'.")

    # Get data and resolution
    char_data = get_character_data(character_list, character_id)
    width, height = IPHONE_RESOLUTIONS[iphone_model]
    scale_factor = width / BASE_RESOLUTION[0]

    # Generate output
    if output_type == "png":
        _generate_png(output_path, char_data, width, height, scale_factor)
    elif output_type == "svg":
        _generate_svg(output_path, char_data, width, height, scale_factor)
    elif output_type == "xml":
        _generate_xml(output_path, char_data, width, height, iphone_model)

    return f"Successfully generated {output_type.upper()} file at: {output_path}"


if __name__ == "__main__":
    # Example usage:
    # python generate_wallpaper.py --output_type svg --character_list hanja --iphone_model iphone_15_pro_max
    import argparse

    parser = argparse.ArgumentParser(description="Generate a character wallpaper.")
    parser.add_argument("--output_path", default="wallpaper.png", help="Output file path.")
    parser.add_argument("--character_id", type=int, default=None, help="Character ID (random if not specified).")
    parser.add_argument("--iphone_model", default="iphone_13_mini", help=f"iPhone model (e.g., {', '.join(IPHONE_RESOLUTIONS.keys())}).")
    parser.add_argument("--output_type", default="png", choices=["png", "svg", "xml"], help="Output format.")
    parser.add_argument("--character_list", default="hsk", choices=["hsk", "hanja"], help="Character set to use.")

    args = parser.parse_args()

    try:
        message = generate_wallpaper(
            output_path=args.output_path,
            character_id=args.character_id,
            iphone_model=args.iphone_model,
            output_type=args.output_type,
            character_list=args.character_list,
        )
        print(message)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")