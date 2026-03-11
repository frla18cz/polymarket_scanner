from pathlib import Path

from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO_ROOT = Path(__file__).resolve().parent
STATIC_ASSETS = REPO_ROOT / "static" / "assets"
SOURCE_VIDEO = STATIC_ASSETS / "demo.mp4"
LANDING_LOOP_MP4 = STATIC_ASSETS / "landing-loop.mp4"
LANDING_LOOP_WEBM = STATIC_ASSETS / "landing-loop.webm"
LANDING_POSTER = STATIC_ASSETS / "landing-poster.png"
LANDING_OG = STATIC_ASSETS / "landing-og.png"
LANDING_SCANNER = STATIC_ASSETS / "landing-scanner-view.png"
LANDING_SMART_MONEY = STATIC_ASSETS / "landing-smart-money-view.png"
LANDING_YIELD = STATIC_ASSETS / "landing-yield-view.png"


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        ])
    candidates.extend([
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_text(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font, fill: str) -> None:
    draw.text(position, text, font=font, fill=fill)


def _build_showcase_frame(
    frame_image: Image.Image,
    target_path: Path,
    badge_text: str,
    title_text: str,
    meta_text: str,
    badge_fill: tuple[int, int, int, int],
) -> None:
    poster = frame_image.resize((1440, 900))
    poster_overlay = Image.new("RGBA", poster.size, (9, 12, 19, 0))
    overlay_draw = ImageDraw.Draw(poster_overlay)
    overlay_draw.rectangle((0, 0, poster.width, 168), fill=(9, 12, 19, 184))
    overlay_draw.rounded_rectangle((48, 40, 304, 92), radius=22, fill=badge_fill)
    overlay_draw.rounded_rectangle((48, 112, 480, 156), radius=18, fill=(17, 27, 41, 220))
    title_font = _load_font(34, bold=True)
    meta_font = _load_font(20)
    _draw_text(overlay_draw, (72, 52), badge_text, title_font, "#f4f7ff")
    _draw_text(overlay_draw, (64, 122), title_text + " | " + meta_text, meta_font, "#c9d6f4")
    poster = Image.alpha_composite(poster.convert("RGBA"), poster_overlay).convert("RGB")
    poster.save(target_path, format="PNG", optimize=True)


def build_landing_assets() -> None:
    if not SOURCE_VIDEO.exists():
        raise FileNotFoundError(f"Missing source video: {SOURCE_VIDEO}")

    clip = VideoFileClip(str(SOURCE_VIDEO))
    landing_clip = clip.subclipped(6, 16).resized(width=1440)
    landing_clip.write_videofile(
        str(LANDING_LOOP_MP4),
        codec="libx264",
        audio=False,
        bitrate="3200k",
        preset="medium",
        fps=12,
        logger=None,
    )
    landing_clip.write_videofile(
        str(LANDING_LOOP_WEBM),
        codec="libvpx-vp9",
        audio=False,
        bitrate="2200k",
        fps=12,
        logger=None,
    )

    scanner_frame = Image.fromarray(landing_clip.get_frame(4.5)).convert("RGB")
    smart_money_frame = Image.fromarray(clip.get_frame(19.5)).convert("RGB")
    yield_frame = Image.fromarray(clip.get_frame(10.5)).convert("RGB")

    _build_showcase_frame(
        scanner_frame,
        LANDING_POSTER,
        "Live scanner preview",
        "Scanner",
        "Price | Spread | APR | Liquidity",
        (25, 88, 212, 225),
    )
    _build_showcase_frame(
        scanner_frame,
        LANDING_SCANNER,
        "Scanner view",
        "Discovery",
        "Go wide, then filter hard",
        (25, 88, 212, 225),
    )
    _build_showcase_frame(
        smart_money_frame,
        LANDING_SMART_MONEY,
        "Smart Money view",
        "Holder positioning",
        "Profitable vs losing split",
        (0, 160, 116, 228),
    )
    _build_showcase_frame(
        yield_frame,
        LANDING_YIELD,
        "Yield + filters",
        "APR workflow",
        "Liquidity | expiry | cleaner setups",
        (191, 137, 31, 228),
    )

    og_bg = scanner_frame.resize((1200, 630)).filter(ImageFilter.GaussianBlur(radius=2))
    og_overlay = Image.new("RGBA", og_bg.size, (7, 10, 18, 168))
    og = Image.alpha_composite(og_bg.convert("RGBA"), og_overlay)
    draw = ImageDraw.Draw(og)
    title_font = _load_font(58, bold=True)
    body_font = _load_font(26)
    badge_font = _load_font(22, bold=True)
    draw.rounded_rectangle((72, 58, 294, 104), radius=22, fill=(22, 84, 220, 230))
    _draw_text(draw, (98, 69), "PolyLab", badge_font, "#f4f7ff")
    _draw_text(draw, (72, 156), "Find better Polymarket", title_font, "#edf2ff")
    _draw_text(draw, (72, 224), "trades in seconds", title_font, "#edf2ff")
    _draw_text(draw, (72, 324), "Scan live markets by price, spread, APR, liquidity,", body_font, "#d8e2fb")
    _draw_text(draw, (72, 364), "and smart-money behavior in one view.", body_font, "#d8e2fb")
    draw.rounded_rectangle((72, 462, 492, 520), radius=20, fill=(18, 28, 44, 215))
    _draw_text(draw, (98, 478), "16,000+ active markets tracked", badge_font, "#bfe0ff")
    og.save(LANDING_OG, format="PNG", optimize=True)

    landing_clip.close()
    clip.close()


if __name__ == "__main__":
    build_landing_assets()
