"""X プロフィール画像生成（アイコン + ヘッダー）"""

from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/home/taka5/.fonts/NotoSansJP-Bold.ttf"
FONT_MEDIUM = "/home/taka5/.fonts/NotoSansJP-Medium.ttf"
OUTPUT_DIR = "/home/taka5/稼げるツール/auto-blog/scripts"


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def generate_icon():
    """400x400 プロフィールアイコン"""
    size = 400
    img = Image.new("RGB", (size, size), "#0f172a")
    draw = ImageDraw.Draw(img)

    # グラデーション風の背景（濃紺→青紫）
    for y in range(size):
        r = int(15 + (40 - 15) * y / size)
        g = int(23 + (20 - 23) * y / size)
        b = int(42 + (120 - 42) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # 中央の装飾: 回路風のドットパターン
    for i in range(8):
        angle = i * math.pi / 4
        for r in [80, 120, 160]:
            x = int(size / 2 + r * math.cos(angle))
            y = int(size / 2 + r * math.sin(angle))
            dot_size = 4 if r == 160 else 3
            draw.ellipse([x - dot_size, y - dot_size, x + dot_size, y + dot_size],
                         fill="#38bdf8")
            # 接続線
            if r < 160:
                x2 = int(size / 2 + (r + 40) * math.cos(angle))
                y2 = int(size / 2 + (r + 40) * math.sin(angle))
                draw.line([(x, y), (x2, y2)], fill="#38bdf844", width=1)

    # 中央円
    cx, cy = size // 2, size // 2
    draw.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill="#1e3a5f", outline="#38bdf8", width=3)

    # "AI" テキスト
    font_ai = ImageFont.truetype(FONT_BOLD, 52)
    bbox = draw.textbbox((0, 0), "AI", font=font_ai)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 5), "AI", fill="#38bdf8", font=font_ai)

    # 下部の「TOOLS LAB」
    font_sub = ImageFont.truetype(FONT_BOLD, 28)
    text = "TOOLS LAB"
    bbox = draw.textbbox((0, 0), text, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + 65), text, fill="#94a3b8", font=font_sub)

    # アクセントライン
    draw.line([(cx - 60, cy + 60), (cx + 60, cy + 60)], fill="#38bdf8", width=2)

    path = f"{OUTPUT_DIR}/x_icon.png"
    img.save(path, "PNG")
    print(f"アイコン生成: {path}")


def generate_header():
    """1500x500 ヘッダー画像"""
    w, h = 1500, 500
    img = Image.new("RGB", (w, h), "#0f172a")
    draw = ImageDraw.Draw(img)

    # グラデーション背景
    for y in range(h):
        r = int(15 + (20 - 15) * y / h)
        g = int(23 + (15 - 23) * y / h)
        b = int(42 + (80 - 42) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # グリッドパターン（テック感）
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(56, 189, 248, 15), width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(56, 189, 248, 15), width=1)

    # グリッド交点にドット
    for x in range(0, w, 60):
        for y in range(0, h, 60):
            # 中央に近いほど明るく
            dist = abs(x - w // 2) / (w // 2)
            if dist < 0.6:
                alpha = int(80 * (1 - dist))
                draw.ellipse([x - 2, y - 2, x + 2, y + 2],
                             fill=(56, 189, 248))

    # メインタイトル
    font_title = ImageFont.truetype(FONT_BOLD, 72)
    title = "AI Tools Lab"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    ty = 140
    draw.text((tx, ty), title, fill="#f1f5f9", font=font_title)

    # アクセントライン
    line_w = 300
    draw.line([(w // 2 - line_w // 2, ty + 90), (w // 2 + line_w // 2, ty + 90)],
              fill="#38bdf8", width=3)

    # サブタイトル
    font_sub = ImageFont.truetype(FONT_BOLD, 32)
    subtitle = "AIツール比較 & 活用ガイド"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, ty + 110), subtitle, fill="#94a3b8", font=font_sub)

    # ツール名を散りばめる
    font_tag = ImageFont.truetype(FONT_MEDIUM, 22)
    tags = ["ChatGPT", "Claude", "Gemini", "Midjourney", "Copilot",
            "Perplexity", "Stable Diffusion", "DALL-E", "Cursor", "DeepL"]
    positions = [
        (80, 380), (280, 400), (480, 370), (680, 410), (880, 380),
        (1080, 400), (1250, 370), (120, 50), (900, 60), (1300, 50)
    ]
    for tag, (tx, ty) in zip(tags, positions):
        bbox = draw.textbbox((0, 0), tag, font=font_tag)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 12
        draw_rounded_rect(draw,
                          (tx - pad, ty - pad // 2, tx + tw + pad, ty + th + pad // 2),
                          8, fill="#1e293b")
        draw.text((tx, ty), tag, fill="#64748b", font=font_tag)

    # 毎日更新バッジ
    font_badge = ImageFont.truetype(FONT_BOLD, 24)
    badge_text = "📝 毎日更新中"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = w - bw - 60, 20
    draw_rounded_rect(draw, (bx - 16, by - 8, bx + bw + 16, by + bh + 8), 12, fill="#1e40af")
    draw.text((bx, by), badge_text, fill="#e0f2fe", font=font_badge)

    path = f"{OUTPUT_DIR}/x_header.png"
    img.save(path, "PNG")
    print(f"ヘッダー生成: {path}")


if __name__ == "__main__":
    generate_icon()
    generate_header()
    print("完了!")
