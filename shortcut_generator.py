"""
Apple Shortcut generator for the Hanja API.

Generates .shortcut files (plist format) that call the wallpaper API
and set the result as the device wallpaper.
"""

import plistlib
import uuid
from typing import Literal


def generate_shortcut(
    api_url: str,
    iphone_model: str = "iphone_13_mini",
    character_list: Literal["hsk", "hanja"] = "hsk",
    refresh_rate: int | None = None,
) -> bytes:
    """
    Generate an Apple Shortcut file that fetches a random wallpaper and sets it.

    Args:
        api_url: Base URL of the deployed API (e.g., "https://api.example.com")
        iphone_model: Default iPhone model for the shortcut
        character_list: Default character list ("hsk" or "hanja")
        refresh_rate: Auto-refresh interval in minutes. If provided, the shortcut
                      will loop and fetch a new wallpaper at this interval.

    Returns:
        bytes: The .shortcut file content (plist format)
    """
    # Build the wallpaper URL
    wallpaper_url = f"{api_url.rstrip('/')}/wallpaper?iphone_model={iphone_model}&character_list={character_list}&output_type=png"

    # Core actions: fetch and set wallpaper
    fetch_action = {
        "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
        "WFWorkflowActionParameters": {
            "WFURL": wallpaper_url,
            "WFHTTPMethod": "GET",
            "UUID": str(uuid.uuid4()).upper(),
        },
    }
    set_wallpaper_action = {
        "WFWorkflowActionIdentifier": "is.workflow.actions.setwallpaper",
        "WFWorkflowActionParameters": {
            "WFWallpaperLocation": "Both",
            "UUID": str(uuid.uuid4()).upper(),
        },
    }

    if refresh_rate is not None and refresh_rate > 0:
        # Create a looping shortcut with wait interval
        wait_action = {
            "WFWorkflowActionIdentifier": "is.workflow.actions.delay",
            "WFWorkflowActionParameters": {
                "WFDelayTime": refresh_rate * 60,  # Convert minutes to seconds
                "UUID": str(uuid.uuid4()).upper(),
            },
        }
        # Repeat action wrapping fetch, set, and wait
        repeat_uuid = str(uuid.uuid4()).upper()
        actions = [
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.repeat.count",
                "WFWorkflowActionParameters": {
                    "WFRepeatCount": 999999,  # Large number for "infinite" loop
                    "GroupingIdentifier": repeat_uuid,
                    "WFControlFlowMode": 0,  # Start of repeat
                    "UUID": str(uuid.uuid4()).upper(),
                },
            },
            fetch_action,
            set_wallpaper_action,
            wait_action,
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.repeat.count",
                "WFWorkflowActionParameters": {
                    "GroupingIdentifier": repeat_uuid,
                    "WFControlFlowMode": 2,  # End of repeat
                    "UUID": str(uuid.uuid4()).upper(),
                },
            },
        ]
    else:
        # Single-run shortcut (no loop)
        actions = [fetch_action, set_wallpaper_action]

    # Shortcut structure
    shortcut = {
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 463140863,  # Dark blue
            "WFWorkflowIconGlyphNumber": 59470,  # Photo icon
        },
        "WFWorkflowClientVersion": "2302.0.4",
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowActions": actions,
        "WFWorkflowInputContentItemClasses": [
            "WFAppStoreAppContentItem",
            "WFArticleContentItem",
            "WFContactContentItem",
            "WFDateContentItem",
            "WFEmailAddressContentItem",
            "WFFolderContentItem",
            "WFGenericFileContentItem",
            "WFImageContentItem",
            "WFiTunesProductContentItem",
            "WFLocationContentItem",
            "WFDCMapsLinkContentItem",
            "WFAVAssetContentItem",
            "WFPDFContentItem",
            "WFPhoneNumberContentItem",
            "WFRichTextContentItem",
            "WFSafariWebPageContentItem",
            "WFStringContentItem",
            "WFURLContentItem",
        ],
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": [],
        "WFQuickActionSurfaces": [],
        "WFWorkflowHasShortcutInputVariables": False,
    }

    return plistlib.dumps(shortcut, fmt=plistlib.FMT_BINARY)


if __name__ == "__main__":
    # Test generation - single run
    shortcut_data = generate_shortcut(
        api_url="https://api.example.com",
        iphone_model="iphone_16_pro",
        character_list="hanja",
    )
    with open("test_shortcut.shortcut", "wb") as f:
        f.write(shortcut_data)
    print("Generated test_shortcut.shortcut (single run)")

    # Test generation - with auto-refresh every 60 minutes
    shortcut_data_loop = generate_shortcut(
        api_url="https://api.example.com",
        iphone_model="iphone_16_pro",
        character_list="hanja",
        refresh_rate=60,
    )
    with open("test_shortcut_loop.shortcut", "wb") as f:
        f.write(shortcut_data_loop)
    print("Generated test_shortcut_loop.shortcut (60 min refresh)")
