"""Template optimization script for AFK Journey heroes."""

import logging
import sys
from pathlib import Path
from typing import cast

import cv2
import numpy as np

# Add the src-python directory to the path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# ruff: noqa: E402
from adb_auto_player.file_loader import SettingsLoader
from adb_auto_player.games.afk_journey.base import AFKJourneyBase
from adb_auto_player.image_manipulation import Color, ColorFormat, Cropping
from adb_auto_player.models.image_manipulation import CropRegions


def optimize_template() -> None:
    """Optimize hero template scale based on current emulator screen."""
    logging.basicConfig(level=logging.INFO)

    config_dir = project_root / "src-tauri" / "Settings"
    resource_dir = project_root / "src-tauri"

    SettingsLoader.set_app_config_dir(config_dir)
    SettingsLoader.set_resource_dir(resource_dir)

    game = AFKJourneyBase()
    game.open_eyes()

    template_path = (
        project_root
        / "adb_auto_player"
        / "games"
        / "afk_journey"
        / "templates"
        / "heroes"
        / "evie.png"
    )
    if not template_path.exists():
        print(f"Error: {template_path} not found!")
        return

    print(f"Loading template: {template_path}")
    template = cv2.imread(str(template_path))
    if template is None:
        print("Error: Could not load template image.")
        return

    print("Capturing screenshot...")
    screenshot = game.get_screenshot()

    # Target region where heroes are
    region = CropRegions(left="5%", right="5%", top="25%", bottom="30%")
    crop_result = Cropping.crop(screenshot, region)
    search_area = Color.to_grayscale(crop_result.image, ColorFormat.BGR)

    best_val = -1.0
    best_scale = 1.0

    print("Optimizing scale...")
    # Try scales from 0.5 to 1.5 with small steps
    for scale in np.linspace(0.5, 1.5, 50):
        width = int(template.shape[1] * scale)
        height = int(template.shape[0] * scale)
        if width == 0 or height == 0:
            continue

        resized_template = cv2.resize(
            template, (width, height), interpolation=cv2.INTER_AREA
        )
        gray_template = Color.to_grayscale(resized_template, ColorFormat.BGR)

        if (
            gray_template.shape[0] > search_area.shape[0]
            or gray_template.shape[1] > search_area.shape[1]
        ):
            continue

        res = cv2.matchTemplate(search_area, gray_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val > best_val:
            best_val = cast(float, max_val)
            best_scale = cast(float, scale)

    print(f"\nBest Match Found! Confidence: {best_val * 100:.2f}%")
    print(f"Optimal Scale: {best_scale:.4f}")

    threshold = 0.6
    if best_val > threshold:
        width = int(template.shape[1] * best_scale)
        height = int(template.shape[0] * best_scale)
        optimized_image = cv2.resize(
            template, (width, height), interpolation=cv2.INTER_AREA
        )

        cv2.imwrite(str(template_path), optimized_image)
        print(f"Successfully updated {template_path.name} with the optimized scale.")
    else:
        print("Could not find a good match.")


if __name__ == "__main__":
    optimize_template()
