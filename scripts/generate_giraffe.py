#!/usr/bin/env python3
"""
GitHub Giraffe Generator
Generates an animated GIF of a giraffe whose neck grows taller with contributions,
and whose spots are dynamically colored by your GitHub programming languages!
"""

import math
import os
import random
import re
import sys
from PIL import Image, ImageDraw

def fetch_github_data(username="Nightkilller"):
    """Fetch public contribution count and top languages."""
    stats = {
        "contributions": 929,
        "languages": {
            "JavaScript": "#F7DF1E",
            "TypeScript": "#3178C6",
            "Python": "#3572A5",
            "C++": "#F34B7D",
            "Java": "#B07219",
            "Dart": "#00B4AB",
        }
    }
    try:
        import requests
        # Fetch contributions
        c_url = f"https://github.com/users/{username}/contributions"
        r = requests.get(c_url, timeout=5)
        if r.status_code == 200:
            m = re.findall(r"([0-9,]+)\s+contributions", r.text)
            if m:
                count_str = m[0].replace(",", "")
                if count_str.isdigit() and int(count_str) > 0:
                    stats["contributions"] = int(count_str)

        # Fetch repos for language distribution
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        headers = {}
        gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if gh_token:
            headers["Authorization"] = f"Bearer {gh_token}"
        rr = requests.get(repos_url, headers=headers, timeout=5)
        if rr.status_code == 200:
            repos = rr.json()
            lang_counts = {}
            for repo in repos:
                if isinstance(repo, dict) and not repo.get("fork"):
                    l = repo.get("language")
                    if l:
                        lang_counts[l] = lang_counts.get(l, 0) + 1
            if lang_counts:
                # GitHub official language color mapping
                color_map = {
                    "JavaScript": "#F7DF1E",
                    "TypeScript": "#3178C6",
                    "Python": "#3572A5",
                    "C++": "#F34B7D",
                    "Java": "#B07219",
                    "HTML": "#E34F26",
                    "CSS": "#563D7C",
                    "Dart": "#00B4AB",
                    "Swift": "#F05138",
                    "Shell": "#89E051",
                    "C": "#555555",
                }
                top_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:6]
                stats["languages"] = {
                    name: color_map.get(name, "#888888")
                    for name, _ in top_langs
                }
    except Exception as e:
        print(f"Notice: using cached/fallback stats ({e})", file=sys.stderr)

    return stats


def generate_giraffe_gif(
    username="Nightkilller",
    output_path="giraffe/giraffe.gif",
    frame_count=20
):
    data = fetch_github_data(username)
    commits = data["contributions"]
    languages = data["languages"]
    print(f"Generating Giraffe for {username}: {commits} commits, languages: {list(languages.keys())}")

    # Color palette
    body_color = (245, 196, 90, 255)
    body_shadow = (220, 168, 65, 255)
    hoof_color = (55, 40, 30, 255)
    mane_color = (130, 75, 40, 255)
    muzzle_color = (250, 220, 185, 255)
    eye_color = (35, 25, 20, 255)
    leaf_green = (76, 175, 80, 255)
    stem_color = (139, 90, 43, 255)
    cloud_color = (255, 255, 255, 180)

    # Convert hex language colors to RGBA
    lang_colors = [
        tuple(int(c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (240,)
        for c in languages.values()
    ]
    if not lang_colors:
        lang_colors = [(180, 100, 50, 240)]

    # Dynamic neck scaling: logarithmic growth
    # 50 commits = ~65px, 500 commits = ~110px, 1000 commits = ~128px, 5000+ = 150px
    neck_length = min(150, max(55, int(42 + 12.5 * math.log(max(1, commits)))))

    canvas_w = 260
    canvas_h = int(175 + neck_length)
    ground_y = canvas_h - 22

    body_center_x = 90
    body_center_y = ground_y - 45
    shoulder_x = body_center_x + 35
    shoulder_y = body_center_y - 12
    hip_x = body_center_x - 35
    hip_y = body_center_y + 5

    # Deterministic spots layout seeded by username
    rng = random.Random(sum(ord(c) for c in username))
    body_spots = []
    for _ in range(15):
        sx = rng.randint(body_center_x - 32, body_center_x + 26)
        sy = rng.randint(body_center_y - 12, body_center_y + 14)
        sr = rng.randint(5, 8)
        sc = rng.choice(lang_colors)
        body_spots.append((sx, sy, sr, sc))

    # Neck spot vertical distribution along the height
    neck_spots_dist = []
    num_neck_spots = max(6, int(neck_length / 14))
    for i in range(num_neck_spots):
        t_val = 0.12 + (i / num_neck_spots) * 0.78
        side = -4 if i % 2 == 0 else 3
        sc = rng.choice(lang_colors)
        neck_spots_dist.append((t_val, side, rng.randint(4, 6), sc))

    frames = []

    for frame_idx in range(frame_count):
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        phase = (frame_idx / frame_count) * 2 * math.pi
        sway = math.sin(phase) * 6.5           # gentle neck breeze sway
        tail_sway = math.sin(phase * 2) * 8.5  # tail swish
        chew = math.sin(phase * 4) * 2.0       # chewing mouth movement

        # Optional cloud background if neck reaches high heights (commits > 500)
        if neck_length > 100:
            cloud_x = 210 + math.sin(phase * 0.5) * 4
            cloud_y = 35
            draw.ellipse([cloud_x - 20, cloud_y - 8, cloud_x + 20, cloud_y + 8], fill=cloud_color)
            draw.ellipse([cloud_x - 10, cloud_y - 14, cloud_x + 10, cloud_y + 6], fill=cloud_color)

        # 1. Back Legs (shadow)
        draw.rectangle([hip_x - 8, hip_y, hip_x - 2, ground_y], fill=body_shadow)
        draw.rectangle([hip_x - 8, ground_y - 6, hip_x - 2, ground_y], fill=hoof_color)

        draw.rectangle([shoulder_x - 14, shoulder_y + 5, shoulder_x - 8, ground_y], fill=body_shadow)
        draw.rectangle([shoulder_x - 14, ground_y - 6, shoulder_x - 8, ground_y], fill=hoof_color)

        # 2. Tail with brush tuft
        tail_start = (hip_x - 25, hip_y - 2)
        tail_end = (hip_x - 35 + tail_sway, hip_y + 28)
        draw.line([tail_start, tail_end], fill=body_shadow, width=3)
        draw.ellipse([tail_end[0] - 4, tail_end[1] - 4, tail_end[0] + 4, tail_end[1] + 4], fill=mane_color)

        # 3. Main Torso
        torso_poly = [
            (shoulder_x, shoulder_y - 12),
            (shoulder_x + 8, shoulder_y + 12),
            (hip_x, hip_y + 16),
            (hip_x - 24, hip_y - 4),
            (shoulder_x - 15, shoulder_y - 15),
        ]
        draw.polygon(torso_poly, fill=body_color)
        draw.chord([body_center_x - 35, body_center_y - 15, body_center_x + 35, body_center_y + 20], 0, 360, fill=body_color)

        # Body language spots with subtle darker outline
        for sx, sy, sr, sc in body_spots:
            draw.ellipse([sx - sr, sy - sr * 0.8, sx + sr, sy + sr * 0.8], fill=sc, outline=body_shadow)

        # 4. Front Legs
        draw.rectangle([hip_x + 4, hip_y + 2, hip_x + 10, ground_y], fill=body_color)
        draw.rectangle([hip_x + 4, ground_y - 6, hip_x + 10, ground_y], fill=hoof_color)

        draw.rectangle([shoulder_x - 2, shoulder_y + 6, shoulder_x + 4, ground_y], fill=body_color)
        draw.rectangle([shoulder_x - 2, ground_y - 6, shoulder_x + 4, ground_y], fill=hoof_color)

        # 5. Neck Kinematic Spline
        neck_points_front = []
        neck_points_back = []
        neck_pts_spine = []

        neck_segs = 18
        for i in range(neck_segs + 1):
            t = i / neck_segs
            dx = (t ** 1.3) * sway
            seg_x = shoulder_x + (t * 22) + dx
            seg_y = shoulder_y - (t * neck_length)
            neck_pts_spine.append((seg_x, seg_y, t))

            half_w = 9.5 - (t * 3.5)
            neck_points_front.append((seg_x + half_w, seg_y))
            neck_points_back.append((seg_x - half_w, seg_y))

        # Mane along the back of the neck
        for i in range(len(neck_points_back) - 1):
            bx, by = neck_points_back[i]
            draw.rectangle([bx - 4, by - 2, bx, by + 4], fill=mane_color)

        # Draw Neck
        neck_poly = neck_points_front + list(reversed(neck_points_back))
        draw.polygon(neck_poly, fill=body_color)

        # Draw Neck language spots
        for t_val, lateral_offset, spot_r, spot_col in neck_spots_dist:
            idx = int(t_val * neck_segs)
            if 0 <= idx < len(neck_pts_spine):
                cx, cy, _ = neck_pts_spine[idx]
                nx = cx + lateral_offset
                ny = cy
                draw.ellipse([nx - spot_r, ny - spot_r, nx + spot_r, ny + spot_r], fill=spot_col, outline=body_shadow)

        # 6. Head
        head_x, head_y, _ = neck_pts_spine[-1]

        # Ears
        ear_sway = math.sin(phase - 0.5) * 2
        draw.polygon([(head_x - 6, head_y - 2), (head_x - 14, head_y - 6 + ear_sway), (head_x - 8, head_y + 3)], fill=body_shadow)
        draw.polygon([(head_x - 2, head_y - 3), (head_x - 10, head_y - 8 + ear_sway), (head_x - 4, head_y + 2)], fill=body_color)

        # Ossicones (Horns)
        draw.line([(head_x + 1, head_y - 6), (head_x + 3, head_y - 15)], fill=body_shadow, width=2)
        draw.ellipse([head_x + 1, head_y - 18, head_x + 5, head_y - 13], fill=mane_color)

        draw.line([(head_x + 6, head_y - 6), (head_x + 9, head_y - 15)], fill=body_color, width=2)
        draw.ellipse([head_x + 7, head_y - 18, head_x + 11, head_y - 13], fill=mane_color)

        # Skull
        draw.ellipse([head_x - 4, head_y - 8, head_x + 16, head_y + 8], fill=body_color)

        # Muzzle / Snout
        muzzle_x = head_x + 14
        muzzle_y = head_y + 1 + chew
        draw.rounded_rectangle([muzzle_x - 4, muzzle_y - 4, muzzle_x + 10, muzzle_y + 7], radius=4, fill=muzzle_color)
        draw.ellipse([muzzle_x + 6, muzzle_y - 1, muzzle_x + 8, muzzle_y + 1], fill=eye_color)

        # Cute eye with glint
        draw.ellipse([head_x + 7, head_y - 3, head_x + 11, head_y + 2], fill=eye_color)
        draw.point((head_x + 8, head_y - 2), fill=(255, 255, 255, 255))

        # Chewing branch with fresh leaves
        twig_x = muzzle_x + 4
        twig_y = muzzle_y + 3
        draw.line([(twig_x, twig_y), (twig_x + 13, twig_y + 4)], fill=stem_color, width=2)
        draw.ellipse([twig_x + 10, twig_y + 1, twig_x + 16, twig_y + 5], fill=leaf_green)
        draw.ellipse([twig_x + 12, twig_y + 4, twig_x + 18, twig_y + 8], fill=leaf_green)

        frames.append(img)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=65,
        loop=0,
        disposal=2
    )
    print(f"Generated {output_path} ({len(frames)} frames, canvas: {canvas_w}x{canvas_h})")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "giraffe/giraffe.gif"
    generate_giraffe_gif("Nightkilller", out)
