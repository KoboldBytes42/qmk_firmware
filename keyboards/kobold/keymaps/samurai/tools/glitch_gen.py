#!/usr/bin/env python3
"""Generate glitch frames for the Arasaka OLED logo (128x32, SSD1306 page layout).

Byte layout (matches oled.c): 512 bytes = 4 pages x 128 columns, page-major.
Each byte is 8 vertical pixels, LSB = top row of that page.

A glitch is a set of "bands": a run of columns inside one page that is copied
from the clean logo with a small horizontal offset. Bands drift, live for a few
frames and fade, so the output looks like a tear rather than static.
Severity (0..1) scales band count, shift range, bit damage and band inversion.

Usage:
  python3 glitch_gen.py logo.png --frames 8 --severity 0.4 --seed 1 \
      --out-c glitch_frames.h --preview preview.png
"""
import argparse
import math
import random

from PIL import Image

W, H, PAGES = 128, 32, 4
FRAME_SIZE = W * PAGES  # 512


def to_display(img, portrait):
    """Buffer (128x32) -> what the rotated OLED shows (32x128) when portrait."""
    return img.rotate(90, expand=True) if portrait else img


def from_display(img, portrait):
    """What the rotated OLED shows (32x128) -> buffer (128x32) when portrait."""
    return img.rotate(-90, expand=True) if portrait else img


def load_clean(path, threshold=128, invert=False, portrait=False):
    """Load an image and pack it into a 512-byte firmware frame."""
    img = Image.open(path)
    if img.mode in ("RGBA", "LA") or "transparency" in img.info:
        # Composite onto black so transparent areas become unlit pixels.
        rgba = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", rgba.size, (0, 0, 0, 255)), rgba)
    img = img.convert("L")
    if portrait:
        img = from_display(img.resize((H, W), Image.LANCZOS), True)
    else:
        img = img.resize((W, H), Image.LANCZOS)
    px = img.load()
    rows = [[1 if (px[x, y] >= threshold) != invert else 0 for x in range(W)] for y in range(H)]
    return pack_rows(rows)


def rotl8(value, n=1):
    return ((value << n) | (value >> (8 - n))) & 0xFF


class Band:
    __slots__ = ("page", "col", "width", "shift", "ttl", "invert")

    def __init__(self, page, col, width, shift, ttl, invert):
        self.page = page
        self.col = col
        self.width = width
        self.shift = shift
        self.ttl = ttl
        self.invert = invert


class GlitchGenerator:
    def __init__(self, clean, severity=0.5, seed=None):
        self.clean = clean
        self.sev = max(0.0, min(1.0, severity))
        self.rng = random.Random(seed)
        self.bands = []
        self.max_shift = 2 + round(6 * self.sev)
        self.max_width = 16 + round(60 * self.sev)
        self.max_ttl = 2 + round(4 * self.sev)
        self.bit_prob = 0.02 + 0.15 * self.sev
        self.invert_prob = 0.15 * self.sev * self.sev

    def _new_band(self):
        rng = self.rng
        width = rng.randint(8, self.max_width)
        col = rng.randrange(0, W - width + 1)
        shift = rng.choice([s for s in range(-self.max_shift, self.max_shift + 1) if s])
        return Band(
            page=rng.randrange(PAGES),
            col=col,
            width=width,
            shift=shift,
            ttl=rng.randint(1, self.max_ttl),
            invert=rng.random() < self.invert_prob,
        )

    def _update_bands(self):
        rng = self.rng
        alive = []
        for band in self.bands:
            band.ttl -= 1
            if band.ttl <= 0:
                continue
            if rng.random() < 0.3:  # drift by one column
                step = rng.choice((-1, 1))
                band.shift = max(-self.max_shift, min(self.max_shift, band.shift + step))
                if band.shift == 0:
                    band.shift = step
            alive.append(band)
        self.bands = alive

        if not self.bands or rng.random() < 0.25 + 0.6 * self.sev:
            for _ in range(rng.randint(1, 1 + round(2 * self.sev))):
                self.bands.append(self._new_band())

    def _render(self):
        frame = list(self.clean)
        rng = self.rng
        for band in self.bands:
            base = band.page * W
            for col in range(band.col, band.col + band.width):
                src = col + band.shift
                frame[base + col] = self.clean[base + src] if 0 <= src < W else 0
                if rng.random() < self.bit_prob:
                    frame[base + col] = rotl8(frame[base + col], rng.randint(1, 7))
                if band.invert:
                    frame[base + col] ^= 0xFF
        return frame

    def next_frame(self):
        """Return the next glitch frame. Each frame is guaranteed to differ from clean."""
        for _ in range(100):
            self._update_bands()
            frame = self._render()
            if frame != self.clean:
                return frame
        return frame  # unreachable in practice

    def sequence(self, count):
        return [self.next_frame() for _ in range(count)]


def unpack_rows(clean):
    """Firmware byte layout -> 32 rows of 128 pixel values (0/1).

    Each byte is 8 horizontal pixels (LSB = rightmost on screen, since the
    picture is rotated 180 degrees). Bytes run down each 32-byte strip and
    strips run from right to left.
    """
    rows = [[0] * W for _ in range(H)]
    for i, value in enumerate(clean):
        strip, y = divmod(i, 32)
        for bit in range(8):
            rows[y][W - 1 - (strip * 8 + bit)] = (value >> bit) & 1
    return rows


def pack_rows(rows):
    """32 rows of pixel values -> 512-byte firmware frame (inverse of unpack_rows)."""
    data = [0] * FRAME_SIZE
    for i in range(FRAME_SIZE):
        strip, y = divmod(i, 32)
        value = 0
        for bit in range(8):
            if rows[y][W - 1 - (strip * 8 + bit)]:
                value |= 1 << bit
        data[i] = value
    return data


class LineGenerator:
    """Sci-fi line distortion: shifted pixel rows (black gaps), a rolling fault bar
    with a sine wobble, and single rows flashed fully on for one frame."""

    def __init__(self, clean, severity=0.5, seed=None, flash=True, direction="mixed"):
        self.clean = clean
        self.flash_enabled = flash
        self.direction = direction
        self.vbands = []  # [x0, width, dy, ttl]: columns shifted vertically
        self.base = unpack_rows(clean)
        self.sev = max(0.0, min(1.0, severity))
        self.rng = random.Random(seed)
        self.offsets = [0] * H
        self.flash = [False] * H
        self.bar_top = None
        self.bar_phase = 0.0
        self.max_shift = 2 + round(4 * self.sev)  # finer shifts
        self.max_rows = 2 + round(6 * self.sev)  # more lines per event
        self.max_v = 1 + round(3 * self.sev)

    def _step(self):
        rng = self.rng
        # shifted rows settle back toward zero offset
        for y in range(H):
            if self.offsets[y] and rng.random() < 0.6:
                self.offsets[y] -= 1 if self.offsets[y] > 0 else -1
        # new line shifts, 1-3 rows thick (horizontal)
        h_scale = 1.0
        if self.direction in ("horizontal", "mixed") and rng.random() < (0.5 + 0.4 * self.sev) * h_scale:  # more often
            choices = [v for v in range(-self.max_shift, self.max_shift + 1) if v]
            for _ in range(rng.randint(1, self.max_rows)):
                y0 = rng.randrange(H)
                thick = 1 if rng.random() < 0.7 else 2  # mostly single-pixel lines
                off = rng.choice(choices)
                for y in range(y0, min(H, y0 + thick)):
                    self.offsets[y] = off
        # column bands shifted up or down (vertical artifacts)
        v_scale = 1.0 if self.direction == "vertical" else 0.5
        max_bands = 2
        if (self.direction in ("vertical", "mixed") and len(self.vbands) < max_bands
                and rng.random() < (0.3 + 0.5 * self.sev) * v_scale):
            w = rng.randint(2, 8)  # column bands: at most 8 px wide
            x0 = rng.randrange(0, W - w + 1)
            dy = rng.choice([v for v in range(-self.max_v, self.max_v + 1) if v])
            self.vbands.append([x0, w, dy, rng.randint(1, 2)])
        self.vbands = [[x0, w, dy, ttl - 1] for x0, w, dy, ttl in self.vbands if ttl - 1 > 0]
        # rolling fault bar: moves top to bottom, rows wobble with a sine
        if self.bar_top is None and rng.random() < 0.05 + 0.15 * self.sev:
            self.bar_top = -4
            self.bar_phase = rng.uniform(0, 2 * math.pi)
        if self.bar_top is not None:
            self.bar_top += 1
            self.bar_phase += 0.9
            for y in range(max(0, self.bar_top), min(H, self.bar_top + 4)):
                self.offsets[y] = round(self.max_shift * math.sin(self.bar_phase + y * 0.7))
            if self.bar_top >= H:
                self.bar_top = None
        # flash rows: forced fully on for this frame only
        flash_p = 0.03 + 0.12 * self.sev
        if self.flash_enabled:
            self.flash = [rng.random() < flash_p for _ in range(H)]
        else:
            self.flash = [False] * H

    def _render(self):
        rows = []
        for y in range(H):
            if self.flash[y]:
                rows.append([1] * W)
                continue
            d = self.offsets[y]
            src = self.base[y]
            if d == 0:
                rows.append(src[:])
            else:
                new = [0] * W  # black gap where no pixel was shifted in
                for x in range(W):
                    sx = x - d
                    if 0 <= sx < W:
                        new[x] = src[sx]
                rows.append(new)
        for x0, w, dy, _ in self.vbands:
            for x in range(x0, x0 + w):
                col = [rows[y][x] for y in range(H)]
                for y in range(H):
                    sy = y - dy
                    rows[y][x] = col[sy] if 0 <= sy < H else 0  # black gap
        return pack_rows(rows)

    def next_frame(self):
        for _ in range(100):
            self._step()
            frame = self._render()
            if frame != self.clean:
                return frame
        return frame

    def sequence(self, count):
        return [self.next_frame() for _ in range(count)]


def write_c(frames, path, name="logo_glitch_gen"):
    lines = [
        "// Generated by tools/glitch_gen.py -- do not edit by hand.",
        "#define logo_glitch_gen_count %d" % len(frames),
        "static const char PROGMEM %s[logo_glitch_gen_count][frame_size] = {" % name,
    ]
    for i, frame in enumerate(frames):
        lines.append("  {")
        lines.append("    // frame %d" % (i + 1))
        for row in range(0, FRAME_SIZE, 16):
            chunk = ", ".join("0x%02x" % b for b in frame[row:row + 16])
            lines.append("    " + chunk + ("," if row + 16 < FRAME_SIZE else ""))
        lines.append("  }" + ("," if i + 1 < len(frames) else ""))
    lines.append("};")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def _frame_to_1bit(frame):
    img = Image.new("1", (W, H), 0)
    px = img.load()
    for y, row in enumerate(unpack_rows(frame)):
        for x, v in enumerate(row):
            if v:
                px[x, y] = 1
    return img


def _tile(frame, scale, portrait):
    img = to_display(_frame_to_1bit(frame), portrait)
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def write_preview(clean, frames, path, scale=4, portrait=False):
    """Clean frame then glitch frames. Portrait: side by side; landscape: stacked."""
    tiles = [_tile(f, scale, portrait) for f in [clean] + frames]
    gap = 6
    if portrait:
        canvas = Image.new("1", (sum(t.width for t in tiles) + gap * (len(tiles) - 1), tiles[0].height), 0)
        x = 0
        for t in tiles:
            canvas.paste(t, (x, 0))
            x += t.width + gap
    else:
        canvas = Image.new("1", (tiles[0].width, sum(t.height for t in tiles) + gap * (len(tiles) - 1)), 0)
        y = 0
        for t in tiles:
            canvas.paste(t, (0, y))
            y += t.height + gap
    canvas.save(path)


def write_gif(clean, frames, path, scale=4, ms=120, hold_clean=3, portrait=False):
    """Animated GIF: clean logo (held), then the glitch frames, looping."""
    seq = [_tile(clean, scale, portrait).convert("L")] * hold_clean
    seq += [_tile(f, scale, portrait).convert("L") for f in frames]
    seq[0].save(path, save_all=True, append_images=seq[1:], duration=ms, loop=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="source image (PNG/BMP/etc.)")
    parser.add_argument("--frames", type=int, default=8, help="number of glitch frames")
    parser.add_argument("--severity", type=float, default=0.5, help="0..1, higher is heavier")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible output")
    parser.add_argument("--portrait", action="store_true",
                        help="artwork and previews use the rotated 32x128 display (OLED_ROTATION_270)")
    parser.add_argument("--direction", choices=["horizontal", "vertical", "mixed"], default="mixed",
                        help="line style: row shifts, column shifts, or both in quick succession")
    parser.add_argument("--no-flash", action="store_true", help="line style only: disable the white flash rows")
    parser.add_argument("--style", choices=["block", "line"], default="block",
                        help="block: shifted 8-pixel column bands; line: sci-fi shifted pixel rows with flashes")
    parser.add_argument("--threshold", type=int, default=128, help="brightness cut-off for lit pixels")
    parser.add_argument("--invert", action="store_true", help="treat dark pixels as lit")
    parser.add_argument("--out-c", help="write frames as a C array (oled.c format)")
    parser.add_argument("--preview", help="write a PNG strip: clean frame then glitch frames")
    parser.add_argument("--name", default="logo_glitch_gen", help="C array name")
    parser.add_argument("--gif", help="write an animated GIF: clean logo, then the glitch frames")
    parser.add_argument("--gif-ms", type=int, default=120, help="milliseconds per GIF frame (default 120)")
    parser.add_argument("--gif-scale", type=int, default=4, help="GIF pixel scale (default 4)")
    args = parser.parse_args()

    clean = load_clean(args.image, args.threshold, args.invert, args.portrait)
    gen_cls = LineGenerator if args.style == "line" else GlitchGenerator
    if gen_cls is LineGenerator:
        gen = LineGenerator(clean, args.severity, args.seed, flash=not args.no_flash, direction=args.direction)
    else:
        gen = GlitchGenerator(clean, args.severity, args.seed)
    frames = gen.sequence(args.frames)

    if args.out_c:
        write_c(frames, args.out_c, args.name)
        print("wrote", args.out_c)
    if args.preview:
        write_preview(clean, frames, args.preview, portrait=args.portrait)
        print("wrote", args.preview)
    if args.gif:
        write_gif(clean, frames, args.gif, args.gif_scale, args.gif_ms, portrait=args.portrait)
        print("wrote", args.gif)
    if not args.out_c and not args.preview and not args.gif:
        print("generated %d frames (use --out-c or --preview to save)" % len(frames))


if __name__ == "__main__":
    main()
