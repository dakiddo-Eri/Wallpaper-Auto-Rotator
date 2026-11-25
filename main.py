from PIL import Image, ImageDraw, ImageFilter
import ctypes
import os 
import random 
import math

WIDTH, HEIGHT = 1920, 1080
OUTPUT_FILE = "daily_wallpaper.png"

def lerp_color(c1, c2, t):
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
    )

def get_theme():
    themes = [
        {"sky_top": (18, 22, 54),   #warm sunset
         "sky_mid": (138, 48, 92),
         "sky_bot": (245, 148, 82),
         "sun": (255, 235, 190),
         "mountain_far": (88, 44, 84),
         "mountain_near": (24, 16, 38)
         },
        {"sky_top": (8, 14, 32),    #deep auroa/midnight
         "sky_mid": (22, 68, 94),
         "sky_bot": (64, 168, 156),
         "sun": (220, 250, 245),
         "mountain_far": (24, 62, 78),
         "mountain_near": (10, 20, 32),
        },
        {"sky_top": (20, 12, 46),
         "sky_mid": (82, 42, 134),
         "sky_bot": (214, 114, 168),
         "sun": (255, 224, 240),
         "mountain_far": (58, 32, 98),
         "mountain_near": (18, 10, 34),
        },
    ]
    return random.choice(themes)

def generate_mountain_points(base_y, roughness, seed_offset):
    points = [(0, HEIGHT)]
    freq1 = random.uniform (0.002, 0.004)
    freq2 = random.uniform (0.007, 0.012)
    freq3 = random.uniform (0.02, 0.035)
    phase1, phase2, phase3 = random.uniform(0, 10), random.uniform(0,10), random.uniform(0, 10)

    for x in range(0, WIDTH + 10, 8):
        y = (
            base_y
            + math.sin(x * freq1 + phase1 +seed_offset) * roughness
            + math.sin(x * freq2 + phase2 ) * (roughness * 0.45)
            + math.cos(x * freq3 + phase3) * (roughness * 0.18)
        )
        points.append((x, int(y)))
    points.append((WIDTH, HEIGHT))
    return points

def create_wallpaper(filepath):
    theme = get_theme()
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    horizon_y = int(HEIGHT * 0.72)
    for y in range (HEIGHT):
        if y < horizon_y * 0.55:
            t = y / (horizon_y * 0.55)
            color = lerp_color(theme["sky_top"], theme["sky_mid"], t)
        elif y < horizon_y:
            t = (y - horizon_y * 0.55) / (horizon_y * 0.45)
            color = lerp_color(theme["sky_mid"], theme ["sky_bot"], t)
        else:
            color = theme["sky_bot"]
        draw.line([(0, y), (WIDTH, y)], fill = color)

    for _ in range(220):  #stars
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, int(horizon_y * 0.55))
        fade = 1 - (sy / (horizon_y * 0.55))
        if random.random() < fade:
            size = random.choice([1, 1, 2])
            brightness = int(160 + 95 * fade)
            draw.ellipse([sx, sy, sx + size, sy + size], fill = (brightness, brightness, brightness))
    #cool sun
    sun_x = random.randint(int(WIDTH * 0.2), int(WIDTH * 0.8))
    sun_y = random.randint(int(HEIGHT * 0.28), int(HEIGHT * 0.48))
    sun_r = random.randint(55, 85)
    #glow border, yay!
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_r = sun_r * 3
    glow_draw.ellipse(
        [sun_x - glow_r, sun_y - glow_r, sun_x +glow_r, sun_y + glow_r],
        fill = (*theme["sun"], 90),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius = 65))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill = theme["sun"])
    layers = 4

    for i in range(layers):
        t = i / (layers - 1)
        ridge_y = int(HEIGHT * (0.52 + i * 0.09))
        roughness = random.randint(65, 115) * (1 - t * 0.25)
        mountain_color = lerp_color(theme["mountain_far"], theme["mountain_near"], t)
        pts = generate_mountain_points(ridge_y, roughness, seed_offset = i * 3.1)
        draw.polygon(pts, fill = mountain_color)
        if i < layers -1:
            mist = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            mist_draw = ImageDraw.Draw(mist)
            mist_y = ridge_y + 40
            mist_draw.rectangle([0, mist_y, WIDTH, mist_y + 140], fill = (*theme["sky_bot"], 45))
            mist = mist.filter(ImageFilter.GaussianBlur(radius = 45))
            img = Image.alpha_composite(img.convert("RGBA"), mist).convert("RGB")
            draw = ImageDraw.Draw(img)
    img.save(filepath, "PNG")

def set_windows_wallpaper(filepath):
    abs_path = os.path.abspath(filepath)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)

if __name__ == "__main__":
    create_wallpaper(OUTPUT_FILE)
    set_windows_wallpaper(OUTPUT_FILE)
    print("New wallpaper YAYA!!")