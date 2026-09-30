#!/usr/bin/env python3
"""2色のブレンドだけでできた PNG のアクセント色を差し替える。

この環境には画像変換ツール（convert / magick / rsvg-convert / inkscape）も
Pillow も無いので、zlib と struct だけで PNG を読み書きする。

対象は「アクセント色と背景色（既定は白）の2色と、その中間色だけ」でできた画像。
`assets/og-image.png` がこれに当たる（実測: 242 色すべてが #2a7ae2 と #ffffff の
ブレンドで、往復誤差は最大 1/255）。写真のような一般の画像には使えない。

    python3 .claude/scripts/recolor_png.py <入力> <出力> --from '#2a7ae2' --to '#1c6ace'

`--check` を付けると書き込まず、入力が本当に2色ブレンドなのか（各色を復元した
ときの最大誤差）だけを報告する。
"""
import argparse
import collections
import struct
import sys
import zlib

SIG = b"\x89PNG\r\n\x1a\n"


def parse_hex(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"色は #rrggbb で指定する: {s}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def read_png(path):
    data = open(path, "rb").read()
    if data[:8] != SIG:
        raise ValueError(f"PNG ではない: {path}")
    idat = b""
    header = None
    i = 8
    while i < len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        chunk_type = data[i + 4:i + 8]
        payload = data[i + 8:i + 8 + length]
        i += 12 + length
        if chunk_type == b"IHDR":
            header = struct.unpack(">IIBBBBB", payload)
        elif chunk_type == b"IDAT":
            idat += payload
    width, height, depth, color_type, _, _, interlace = header
    if depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise ValueError(
            f"8bit の truecolor（RGB/RGBA）・非インターレースのみ対応: {path}"
        )
    bpp = 3 if color_type == 2 else 4
    raw = zlib.decompress(idat)
    stride = width * bpp
    out = bytearray()
    prev = bytearray(stride)
    pos = 0
    for _ in range(height):
        filt = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if filt == 1:
                line[x] = (line[x] + a) & 0xFF
            elif filt == 2:
                line[x] = (line[x] + b) & 0xFF
            elif filt == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 0xFF
            elif filt == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pred) & 0xFF
        out += line
        prev = line
    return width, height, bpp, bytes(out)


def write_png(path, width, height, bpp, pixels):
    stride = width * bpp
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0（None）。サイズより再現性を優先する
        raw += pixels[y * stride:(y + 1) * stride]

    def chunk(kind, payload):
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    color_type = 2 if bpp == 3 else 6
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    body = (
        SIG
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    open(path, "wb").write(body)


def blend_factor(pixel, src, base):
    """pixel が src→base のどこにあるか。分離幅が最大のチャンネルで測る。"""
    channel = max(range(3), key=lambda k: abs(base[k] - src[k]))
    span = base[channel] - src[channel]
    return (pixel[channel] - src[channel]) / span


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src_path")
    ap.add_argument("dst_path", nargs="?")
    ap.add_argument("--from", dest="src_color", required=True, help="今のアクセント色")
    ap.add_argument("--to", dest="dst_color", help="新しいアクセント色")
    ap.add_argument("--base", default="#ffffff", help="ブレンド相手の色（既定は白）")
    ap.add_argument("--tolerance", type=int, default=2,
                    help="2色ブレンドとみなす最大誤差（既定 2/255）")
    ap.add_argument("--check", action="store_true", help="書き込まず検査だけ行う")
    args = ap.parse_args(argv)

    src = parse_hex(args.src_color)
    base = parse_hex(args.base)
    width, height, bpp, pixels = read_png(args.src_path)

    counts = collections.Counter(
        pixels[i:i + 3] for i in range(0, len(pixels), bpp)
    )
    worst = 0
    worst_color = None
    for color in counts:
        t = blend_factor(color, src, base)
        rebuilt = tuple(round(src[k] + t * (base[k] - src[k])) for k in range(3))
        err = max(abs(rebuilt[k] - color[k]) for k in range(3))
        if err > worst:
            worst, worst_color = err, color.hex()
    print(f"{args.src_path}: {len(counts)} 色 / 2色ブレンドからの最大誤差 {worst}"
          f"（最悪 #{worst_color}）")
    if worst > args.tolerance:
        print(f"誤差が許容 {args.tolerance} を超えたので中止する（2色ブレンドの画像ではない）",
              file=sys.stderr)
        return 1
    if args.check:
        return 0
    if not args.dst_path or not args.dst_color:
        ap.error("書き込むには出力パスと --to が要る")

    dst = parse_hex(args.dst_color)
    table = {}
    out = bytearray(pixels)
    for i in range(0, len(pixels), bpp):
        key = pixels[i:i + 3]
        mapped = table.get(key)
        if mapped is None:
            t = blend_factor(key, src, base)
            mapped = bytes(
                max(0, min(255, round(dst[k] + t * (base[k] - dst[k]))))
                for k in range(3)
            )
            table[key] = mapped
        out[i:i + 3] = mapped
    write_png(args.dst_path, width, height, bpp, bytes(out))
    print(f"{args.dst_path}: {len(table)} 色を {args.src_color} → {args.dst_color} に差し替えた")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
