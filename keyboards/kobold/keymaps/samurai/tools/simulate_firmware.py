#!/usr/bin/env python3
"""Simulate the Arasaka OLED state machine from oled.c and render it as a GIF.

Follows arasaka_draw() in oled.c:
  - logo and text swap every 10 s
  - glitch windows at 0-250 ms and 9750-10000 ms of each cycle
  - random glitch starts: 1-in-60 per tick, length 1-4 or 1-10 ticks
  - a glitch frame is picked at random from the glitch pool

Logo glitches come from the generator (--style, --severity). Text frames and
text glitches come from oled.c. The logo 'dirty' frames are not used.

--tick-ms is the time between OLED updates. It is not known exactly, so set it
to the real refresh interval of the firmware.

Usage:
  tools/logo.sh simulate source/TTC_Logo_1bit.bmp --style line --no-flash \
      --gif preview/firmware_sim.gif --sim-seconds 25 --tick-ms 50
"""
import argparse
import math
import os
import random
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glitch_gen as g  # noqa: E402
import convert_logo as c  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OLED_C = os.path.join(HERE, "..", "oled.c")


def read_frames(path, name):
    """All frames of a PROGMEM [count][frame_size] array in oled.c."""
    src = open(path).read()
    m = re.search(name + r"\[[^\]]*\]\[frame_size\] = \{(.*?)\n\};", src, re.S)
    if not m:
        raise SystemExit("array %s not found in %s" % (name, path))
    parts = re.split(r"// frame \d+", m.group(1))[1:]
    return [[int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]{2})", p)] for p in parts]


def make_dirty(logo_frame, text_frame, rng):
    """Logo with large sections split into 6-12 px wide blocks.

    Each block is moved up or down by its own random offset (black gap where
    it leaves), so whole pieces of the logo jump vertically.
    """
    src = g.unpack_rows(logo_frame)
    out = [row[:] for row in src]
    for _ in range(rng.randint(1, 3)):
        w = rng.randint(40, 96)
        x0 = rng.randrange(0, g.W - w + 1)
        x = x0
        while x < x0 + w:
            seg = min(rng.randint(6, 12), x0 + w - x)
            dy = rng.choice([v for v in range(-4, 5) if v])
            for xx in range(x, x + seg):
                for y in range(g.H):
                    sy = y - dy
                    out[y][xx] = src[sy][xx] if 0 <= sy < g.H else 0
            x += seg
    return g.pack_rows(out)


def simulate(logo_clean, text_clean, logo_pool, text_pool, ticks, tick_ms, rng, logo_dirty=None):
    """Return a list of (frame, phase) tuples, one per OLED update.

    As in arasaka_draw(): glitch frames for the logo come from the glitch pool
    plus the dirty pool; dirty phases use only the dirty pool.
    """
    glitch = True
    frame_count = 15
    show_text = True
    start = 0
    out = []
    logo_dirty = list(logo_dirty or [])
    logo_mixed = list(logo_pool) + logo_dirty

    def pick(pool):
        return pool[rng.randrange(len(pool))]

    def glitch_frame():
        return pick(text_pool) if show_text else pick(logo_mixed)

    def dirty_frame():
        if show_text:
            return pick(text_pool)
        return pick(logo_dirty) if logo_dirty else pick(logo_pool)

    for i in range(ticks):
        now = i * tick_ms
        timer = now - start

        if timer < 150:
            out.append((dirty_frame(), "dirty"))
            continue
        if timer < 250:
            out.append((glitch_frame(), "glitch"))
            continue
        if 9750 < timer < 9850:
            out.append((glitch_frame(), "glitch"))
            continue
        if 9850 < timer < 10000:
            out.append((dirty_frame(), "dirty"))
            continue
        if timer > 10000:
            show_text = not show_text
            start = now

        if glitch and frame_count != 0:
            frame_count -= 1
            out.append((glitch_frame(), "glitch"))
            continue

        glitch = False
        out.append((text_clean if show_text else logo_clean, "clean"))

        if rng.randrange(60) == 0:
            glitch = True
            frame_count = 1 + rng.randrange(4)
            continue
        if rng.randrange(60) == 0:
            glitch = True
            frame_count = 1 + rng.randrange(10)
    return out


def frame_image(frame, scale, portrait=False):
    img = g.to_display(c.frame_to_mono(frame), portrait)
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST).convert("L")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", nargs="?", help="1-bit logo image (BMP/PNG, 128x32); omit with --firmware")
    parser.add_argument("--firmware", action="store_true",
                        help="use the firmware's own logo_clean and logo_glitch frames from oled.c")
    parser.add_argument("--style", choices=["block", "line"], default="line")
    parser.add_argument("--severity", type=float, default=0.5)
    parser.add_argument("--no-flash", action="store_true")
    parser.add_argument("--direction", choices=["horizontal", "vertical", "mixed"], default="mixed")
    parser.add_argument("--pool-size", type=int, default=8, help="number of logo glitch frames in the pool")
    parser.add_argument("--gen-seed", type=int, default=4, help="seed for generating the glitch pool")
    parser.add_argument("--sim-seed", type=int, default=1, help="seed for the firmware state machine")
    parser.add_argument("--sim-seconds", type=float, default=25.0)
    parser.add_argument("--tick-ms", type=int, default=50)
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--portrait", action="store_true", help="show the rotated 32x128 display")
    parser.add_argument("--gif", required=True, help="output GIF path")
    parser.add_argument("--oled", default=OLED_C, help="path to oled.c (for text frames)")
    parser.add_argument("--dirty-count", type=int, default=0,
                        help="number of dirty frames: logo with a random block from the text image")
    parser.add_argument("--text-image", help="image for the text phase (default: firmware text from oled.c)")
    args = parser.parse_args()

    if args.firmware:
        logo_clean = c.read_c_array(args.oled, "logo_clean")
    else:
        if not args.image:
            parser.error("give a logo image or use --firmware")
        logo_clean = g.load_clean(args.image, portrait=args.portrait)

    def make_pool(clean):
        if args.style == "line":
            gen = g.LineGenerator(clean, args.severity, args.gen_seed, flash=not args.no_flash,
                                  direction=args.direction)
        else:
            gen = g.GlitchGenerator(clean, args.severity, args.gen_seed)
        return gen.sequence(args.pool_size)

    if args.firmware:
        logo_pool = read_frames(args.oled, "logo_glitch")
    else:
        logo_pool = make_pool(logo_clean)
    if args.text_image:
        text_clean = g.load_clean(args.text_image, portrait=args.portrait)
        text_pool = make_pool(text_clean)
    else:
        text_clean = c.read_c_array(args.oled, "text_clean")
        text_pool = read_frames(args.oled, "text_glitch")

    logo_dirty = []
    if args.dirty_count:
        dirty_rng = random.Random(args.gen_seed + 1)
        # dirty frames use only the logo: its own sections are moved on a wave
        logo_dirty = [make_dirty(logo_clean, logo_clean, dirty_rng) for _ in range(args.dirty_count)]

    ticks = int(args.sim_seconds * 1000 / args.tick_ms)
    rng = random.Random(args.sim_seed)
    timeline = simulate(logo_clean, text_clean, logo_pool, text_pool, ticks, args.tick_ms, rng, logo_dirty)

    counts = {}
    for _, phase in timeline:
        counts[phase] = counts.get(phase, 0) + 1
    print("ticks:", len(timeline), "phases:", counts)

    images = [frame_image(f, args.scale, args.portrait) for f, _ in timeline]
    images[0].save(args.gif, save_all=True, append_images=images[1:], duration=args.tick_ms, loop=0)
    print("wrote", args.gif, "(%d frames)" % len(images))


if __name__ == "__main__":
    main()
