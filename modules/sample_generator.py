"""
Sample Image Generator for BBMP Civic Hotspot Testing.
Generates synthetic realistic test scenes with real embedded EXIF GPS tags
for Bengaluru locations (Bellandur, HSR Layout, Koramangala, and Cubbon Park).
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import cv2
import numpy as np
from PIL import Image
from modules.exif_extractor import embed_gps_to_image

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sample_images")


def generate_all_samples():
    """Generates 4 pre-bundled test images with verified GPS metadata."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    # Sample 1: Bellandur C&D Debris
    p1 = os.path.join(SAMPLES_DIR, "bellandur_debris.jpg")
    if not os.path.exists(p1):
        img1 = create_debris_scene()
        raw1 = embed_gps_to_image(img1, latitude=12.926340, longitude=77.676620, device_name="OnePlus 11 5G")
        with open(p1, "wb") as f:
            f.write(raw1)

    # Sample 2: HSR Layout Plastic Dump
    p2 = os.path.join(SAMPLES_DIR, "hsr_plastic_dump.jpg")
    if not os.path.exists(p2):
        img2 = create_plastic_dump_scene()
        raw2 = embed_gps_to_image(img2, latitude=12.912410, longitude=77.644830, device_name="Samsung Galaxy S24")
        with open(p2, "wb") as f:
            f.write(raw2)

    # Sample 3: Koramangala Organic & Mixed Waste
    p3 = os.path.join(SAMPLES_DIR, "koramangala_mixed.jpg")
    if not os.path.exists(p3):
        img3 = create_mixed_waste_scene()
        raw3 = embed_gps_to_image(img3, latitude=12.935420, longitude=77.624710, device_name="iPhone 15 Pro")
        with open(p3, "wb") as f:
            f.write(raw3)

    # Sample 4: Pristine Park (Negative Test / False Alarm Prevention)
    p4 = os.path.join(SAMPLES_DIR, "clean_cubbon_park.jpg")
    if not os.path.exists(p4):
        img4 = create_clean_park_scene()
        raw4 = embed_gps_to_image(img4, latitude=12.976300, longitude=77.592900, device_name="Google Pixel 8")
        with open(p4, "wb") as f:
            f.write(raw4)


def create_debris_scene() -> Image.Image:
    """Generates an image of concrete rubble, bricks, and dusty mounds along a road."""
    h, w = 600, 800
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Road background (gray asphalt with perspective)
    for y in range(h):
        shade = int(80 + (y / h) * 40)
        arr[y, :] = [shade, shade, shade]

    # Add concrete curb / soil patch on right half
    cv2.rectangle(arr, (int(w * 0.4), int(h * 0.3)), (w, h), (140, 130, 115), -1)

    # Add textured gravel noise
    noise = np.random.randint(-35, 35, (h, w, 3))
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Add concrete chunks & rubble blocks (irregular polygons)
    np.random.seed(42)
    for _ in range(40):
        cx = np.random.randint(int(w * 0.42), w - 30)
        cy = np.random.randint(int(h * 0.35), h - 30)
        pts = np.array([
            [cx + np.random.randint(-30, 0), cy + np.random.randint(-25, 0)],
            [cx + np.random.randint(10, 45), cy + np.random.randint(-20, 10)],
            [cx + np.random.randint(20, 50), cy + np.random.randint(20, 45)],
            [cx + np.random.randint(-25, 5), cy + np.random.randint(15, 40)]
        ], np.int32)
        # Concrete gray or red clay brick
        c_color = (190, 185, 175) if np.random.rand() > 0.4 else (80, 70, 175)
        cv2.fillPoly(arr, [pts], c_color)
        cv2.polylines(arr, [pts], True, (40, 40, 40), 1)

    return Image.fromarray(arr)


def create_plastic_dump_scene() -> Image.Image:
    """Generates an image of scattered plastic shopping bags, wrappers, and PET bottles."""
    h, w = 600, 800
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Pavement footpath background
    arr[:, :] = [110, 115, 120]
    # Sidewalk curb line
    cv2.line(arr, (0, int(h * 0.4)), (w, int(h * 0.4)), (60, 60, 60), 3)

    # Add texture
    noise = np.random.randint(-25, 25, (h, w, 3))
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Discarded blue, red, yellow poly bags and bottles
    colors = [
        (220, 50, 40),    # Bright blue in BGR
        (40, 50, 230),    # Bright red
        (30, 220, 240),   # Bright yellow
        (240, 240, 240),  # White translucent poly bag
        (20, 160, 40),    # Green soda bottle
    ]

    np.random.seed(101)
    for _ in range(55):
        bx = np.random.randint(60, w - 80)
        by = np.random.randint(int(h * 0.45), h - 50)
        col = colors[np.random.randint(0, len(colors))]
        # Crumpled polybag shape
        axes = (np.random.randint(20, 55), np.random.randint(15, 40))
        angle = np.random.randint(0, 180)
        cv2.ellipse(arr, (bx, by), axes, angle, 0, 360, col, -1)
        # Crumple folds
        cv2.ellipse(arr, (bx, by), (int(axes[0]*0.7), int(axes[1]*0.6)), angle + 25, 0, 360, (255, 255, 255), 1)

    return Image.fromarray(arr)


def create_mixed_waste_scene() -> Image.Image:
    """Generates mixed decomposing market waste, cartons, and organic sludge."""
    h, w = 600, 800
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Muddy roadside shoulder background (dark earthy tone)
    arr[:, :] = [45, 55, 65]

    # Large dark organic sludge patch
    cv2.ellipse(arr, (int(w * 0.5), int(h * 0.6)), (260, 160), 15, 0, 360, (25, 35, 45), -1)

    np.random.seed(202)
    # Decomposing greens & market refuse (dark greens and decaying sludge)
    for _ in range(45):
        gx = np.random.randint(120, w - 120)
        gy = np.random.randint(220, h - 80)
        cv2.circle(arr, (gx, gy), np.random.randint(20, 45), (20, 60, 35), -1)

    # Wet cardboard cartons (brown rectangles, low saturation)
    for _ in range(7):
        cx = np.random.randint(140, w - 180)
        cy = np.random.randint(220, h - 140)
        bw, bh = np.random.randint(70, 120), np.random.randint(45, 80)
        cv2.rectangle(arr, (cx, cy), (cx + bw, cy + bh), (40, 75, 110), -1)
        cv2.rectangle(arr, (cx, cy), (cx + bw, cy + bh), (20, 45, 70), 2)

    # Small scattered trash pieces
    for _ in range(15):
        rx = np.random.randint(120, w - 120)
        ry = np.random.randint(220, h - 90)
        cv2.circle(arr, (rx, ry), np.random.randint(10, 20), (50, 90, 120), -1)

    return Image.fromarray(arr)


def create_clean_park_scene() -> Image.Image:
    """Generates a clean lawn and pathway with zero garbage (for negative control test)."""
    h, w = 600, 800
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Upper 40%: Clear blue sky & distant green trees
    arr[:int(h * 0.35), :] = [235, 200, 120] # Light blue sky in BGR
    # Treeline
    cv2.rectangle(arr, (0, int(h * 0.28)), (w, int(h * 0.42)), (40, 110, 45), -1)

    # Lower 60%: Manicured green lawn
    arr[int(h * 0.42):, :] = [45, 155, 60]

    # Smooth clean stone walkway diagonally
    pts = np.array([[int(w * 0.35), int(h * 0.42)], [int(w * 0.65), int(h * 0.42)], [int(w * 0.8), h], [int(w * 0.2), h]], np.int32)
    cv2.fillPoly(arr, [pts], (180, 185, 190))
    cv2.polylines(arr, [pts], True, (150, 155, 160), 2)

    return Image.fromarray(arr)


if __name__ == "__main__":
    generate_all_samples()
    print("Pre-bundled sample images created successfully in assets/sample_images/.")
