"""Script to extract hero templates from AFK Journey screenshots."""

import logging
import os
import sys
from pathlib import Path

import cv2

# Add the src-python directory to the path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# ruff: noqa: E402
from adb_auto_player.games.afk_journey.base import AFKJourneyBase
from adb_auto_player.image_manipulation import Cropping
from adb_auto_player.models.image_manipulation import CropRegions


def extract_hero_templates() -> None:
    """Extract hero portraits from the current screen."""
    logging.basicConfig(level=logging.INFO)

    # Initialize the game instance
    game = AFKJourneyBase()
    game.open_eyes()

    print("Capturing screenshot...")
    screenshot = game.get_screenshot()

    # Define the region where rival heroes are located in the Records view
    region = CropRegions(left="5%", right="5%", top="20%", bottom="20%")
    crop_result = Cropping.crop(screenshot, region)

    output_dir = script_dir / "extracted_heroes"
    os.makedirs(output_dir, exist_ok=True)

    # Save the whole region for debugging
    cv2.imwrite(str(output_dir / "debug_region.png"), crop_result.image)
    print(f"Debug region saved to {output_dir / 'debug_region.png'}")

    print("\nI have saved 'debug_region.png'.")
    print("Please check if you see Evie's portrait in that image.")


if __name__ == "__main__":
    extract_hero_templates()
