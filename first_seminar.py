"""Seminar1"""

import os
import re
import subprocess
import tempfile

import numpy as np
import pywt
from PIL import Image
from scipy.fft import dctn, idctn
from scipy.ndimage import gaussian_filter

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "images", "test_image.png")
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)


def out(name):
    return os.path.join(OUT, name)


def ffmpeg(args):
    """Run ffmpeg and return its stderr (filters like psnr print there)."""
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner"] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stderr


def psnr(a, b):
    """PSNR (dB) between two 8-bit images."""
    mse = np.mean((a.astype(float) - b.astype(float)) ** 2)
    if mse == 0:
        return float("inf")
    return 10 * np.log10(255 ** 2 / mse)


# Standard JPEG zigzag order, as flat indices of the 8x8 matrix.
ZIGZAG = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
          12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
          35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
          58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]

# Standard JPEG luminance quantization table.
QTABLE = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]], dtype=float)


# ------------------------------------------------- ex 2, 3, 4, 5, 7
class ColorTranslator:

    def rgb_to_yuv(self, rgb):
        """BT.601 full range, U and V centred on 128. uint8 in, uint8 out."""
        rgb = rgb.astype(float)
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.168736 * r - 0.331264 * g + 0.5 * b + 128
        v = 0.5 * r - 0.418688 * g - 0.081312 * b + 128
        yuv = np.stack([y, u, v], axis=-1)
        return np.clip(np.rint(yuv), 0, 255).astype(np.uint8)

    def yuv_to_rgb(self, yuv):
        yuv = yuv.astype(float)
        y, u, v = yuv[..., 0], yuv[..., 1] - 128, yuv[..., 2] - 128
        r = y + 1.402 * v
        g = y - 0.344136 * u - 0.714136 * v
        b = y + 1.772 * u
        rgb = np.stack([r, g, b], axis=-1)
        return np.clip(np.rint(rgb), 0, 255).astype(np.uint8)

    # ex 3: lossless codec (ffv1) so the file size shows only the subsampling
    def export_pix_fmt(self, src, dst, pix_fmt):
        ffmpeg(["-i", src, "-pix_fmt", pix_fmt, "-c:v", "ffv1", dst])

    def blur_chroma(self, rgb, sigma):
        yuv = self.rgb_to_yuv(rgb).astype(float)
        yuv[..., 1] = gaussian_filter(yuv[..., 1], sigma)
        yuv[..., 2] = gaussian_filter(yuv[..., 2], sigma)
        return self.yuv_to_rgb(yuv)

    def blur_luma(self, rgb, sigma):
        yuv = self.rgb_to_yuv(rgb).astype(float)
        yuv[..., 0] = gaussian_filter(yuv[..., 0], sigma)
        return self.yuv_to_rgb(yuv)

    # ex 4
    def resize(self, src, dst, factor, sws_flags=None):
        vf = "scale=iw/%d:ih/%d" % (factor, factor)
        if sws_flags:
            vf += ":flags=" + sws_flags
        ffmpeg(["-i", src, "-vf", vf, dst])

    # ex 5
    def zigzag(self, block):
        flat = np.asarray(block).flatten()
        return [flat[i] for i in ZIGZAG]

    def inverse_zigzag(self, seq):
        flat = np.zeros(64, dtype=np.asarray(seq).dtype)
        flat[ZIGZAG] = seq
        return flat.reshape(8, 8)

    # ex 7: list of (value, run length)
    def rle_encode(self, seq):
        pairs = []
        for v in seq:
            if pairs and pairs[-1][0] == v:
                pairs[-1][1] += 1
            else:
                pairs.append([v, 1])
        return [(v, n) for v, n in pairs]

    def rle_decode(self, pairs):
        seq = []
        for v, n in pairs:
            seq += [v] * n
        return seq


# ------------------------------------------------------------- ex 6
class DCTCodec:

    def __init__(self, quality=50):
        self.quality = quality
        self.qtable = self.quant_table(quality)

    def quant_table(self, quality):
        if not 1 <= quality <= 100:
            raise ValueError("quality must be between 1 and 100")
        if quality < 50:
            scale = 5000 / quality
        else:
            scale = 200 - 2 * quality
        return np.clip(np.floor((QTABLE * scale + 50) / 100), 1, 255)

    def encode_block(self, block):
        """uint8 8x8 -> quantized int 8x8 (level shift of -128 included)."""
        coeffs = dctn(block.astype(float) - 128, type=2, norm="ortho")
        return np.rint(coeffs / self.qtable).astype(int)

    def decode_block(self, q):
        coeffs = q * self.qtable
        block = idctn(coeffs, type=2, norm="ortho") + 128
        return np.clip(np.rint(block), 0, 255).astype(np.uint8)


# ------------------------------------------------------------- ex 8
class MiniJPEG:

    def __init__(self, quality=50):
        self.dct = DCTCodec(quality)
        self.tools = ColorTranslator()

    def encode(self, gray):
        h, w = gray.shape
        padded = np.pad(gray, ((0, (-h) % 8), (0, (-w) % 8)), mode="edge")
        payload = []
        for i in range(0, padded.shape[0], 8):
            for j in range(0, padded.shape[1], 8):
                q = self.dct.encode_block(padded[i:i + 8, j:j + 8])
                payload.append(self.tools.rle_encode(self.tools.zigzag(q)))
        return payload, (h, w)

    def decode(self, payload, shape):
        h, w = shape
        img = np.zeros((h + (-h) % 8, w + (-w) % 8), dtype=np.uint8)
        k = 0
        for i in range(0, img.shape[0], 8):
            for j in range(0, img.shape[1], 8):
                q = self.tools.inverse_zigzag(self.tools.rle_decode(payload[k]))
                img[i:i + 8, j:j + 8] = self.dct.decode_block(q)
                k += 1
        return img[:h, :w]

    def n_pairs(self, payload):
        return sum(len(block) for block in payload)


# ------------------------------------------------------------- ex 9
class DWTCodec:

    def __init__(self, wavelet="haar"):
        self.wavelet = wavelet

    def decompose(self, gray):
        return pywt.dwt2(gray.astype(float), self.wavelet)

    def reconstruct(self, coeffs):
        return pywt.idwt2(coeffs, self.wavelet)

    def subbands(self, gray):
        ll, (lh, hl, hh) = self.decompose(gray)   # pywt: cH, cV, cD
        return {"LL": ll, "LH": lh, "HL": hl, "HH": hh}

    def save_subbands(self, gray, path):
        s = self.subbands(gray)
        ll = np.clip(s["LL"] / 2, 0, 255)           # haar LL has gain 2
        det = [np.clip(128 + 4 * s[k], 0, 255) for k in ("LH", "HL", "HH")]
        top = np.hstack([ll, det[0]])
        bottom = np.hstack([det[1], det[2]])
        Image.fromarray(np.vstack([top, bottom]).astype(np.uint8)).save(path)


def quality_report(orig, comp):
    """PSNR and SSIM from ffmpeg filters. Both files must be RGB images (PNG):
    comparing different pixel formats depends on the ffmpeg version."""
    log = ffmpeg(["-i", orig, "-i", comp, "-lavfi", "[0:v][1:v]psnr", "-f", "null", "-"])
    p = float(re.search(r"average:([\d.]+)", log).group(1))
    log = ffmpeg(["-i", orig, "-i", comp, "-lavfi", "[0:v][1:v]ssim", "-f", "null", "-"])
    s = float(re.search(r"All:([\d.]+)", log).group(1))
    return p, s


def main():
    rgb = np.asarray(Image.open(IMG).convert("RGB"))
    gray = np.asarray(Image.open(IMG).convert("L"))
    Image.fromarray(gray).save(out("gray.png"))
    ct = ColorTranslator()

    print("== ex 2: RGB -> YUV -> RGB")
    back = ct.yuv_to_rgb(ct.rgb_to_yuv(rgb))
    diff = np.abs(back.astype(int) - rgb.astype(int))
    print("max error:", diff.max(), "| pixels with error:", np.mean(diff.max(axis=-1) > 0))

    print("== ex 3: pix_fmt sizes (ffv1) and blur")
    for pf in ("yuv444p", "yuv422p", "yuv420p", "yuv411p"):
        ct.export_pix_fmt(IMG, out(pf + ".mkv"), pf)
        print(pf, os.path.getsize(out(pf + ".mkv")), "bytes")
    bc = ct.blur_chroma(rgb, 8)
    bl = ct.blur_luma(rgb, 8)
    Image.fromarray(bc).save(out("blur_chroma.png"))
    Image.fromarray(bl).save(out("blur_luma.png"))
    print("PSNR blur chroma: %.2f dB | blur luma: %.2f dB" % (psnr(rgb, bc), psnr(rgb, bl)))

    print("== ex 4: resize")
    for f in (2, 4, 8):
        ct.resize(IMG, out("resize_1_%d.png" % f), f)
    ct.resize(IMG, out("resize_1_4_neighbor.png"), 4, "neighbor")
    ct.resize(IMG, out("resize_1_4_lanczos.png"), 4, "lanczos")
    names = ("resize_1_2", "resize_1_4", "resize_1_8",
             "resize_1_4_neighbor", "resize_1_4_lanczos")
    for n in names:
        print(n, Image.open(out(n + ".png")).size, os.path.getsize(out(n + ".png")), "bytes")

    print("== ex 6: non-zero coefficients of one block vs quality")
    block = gray[304:312, 48:56]
    for q in (95, 50, 10):
        coefs = DCTCodec(q).encode_block(block)
        print("quality", q, "non-zero:", np.count_nonzero(coefs), "of 64")
        print(coefs)

    print("== ex 8: mini-JPEG vs ffmpeg (gray %dx%d, raw %d bytes)"
          % (gray.shape[1], gray.shape[0], gray.size))
    for q in (10, 50, 90):
        mj = MiniJPEG(q)
        payload, shape = mj.encode(gray)
        dec = mj.decode(payload, shape)
        Image.fromarray(dec).save(out("mini_q%d.png" % q))
        pairs = mj.n_pairs(payload)
        print("mini q=%d: %d RLE pairs (~%d bytes at 3 B/pair), PSNR %.2f dB"
              % (q, pairs, pairs * 3, psnr(gray, dec)))
    for n in (3, 10, 25):
        ffmpeg(["-i", out("gray.png"), "-q:v", n, out("ff_q%d.jpg" % n)])
        dec = np.asarray(Image.open(out("ff_q%d.jpg" % n)).convert("L"))
        size = os.path.getsize(out("ff_q%d.jpg" % n))
        print("ffmpeg -q:v %d: %d bytes, PSNR %.2f dB" % (n, size, psnr(gray, dec)))
    ffmpeg(["-i", IMG, "-vf", "format=gray", "-q:v", 31, out("ff_bw_hardest.jpg")])
    dec = np.asarray(Image.open(out("ff_bw_hardest.jpg")).convert("L"))
    size = os.path.getsize(out("ff_bw_hardest.jpg"))
    print("ffmpeg b/w hardest (-q:v 31): %d bytes, PSNR %.2f dB" % (size, psnr(gray, dec)))

    print("== ex 9: DWT and JPEG vs JPEG2000")
    d = DWTCodec()
    print("DWT reconstruction max error:", np.abs(d.reconstruct(d.decompose(gray)) - gray).max())
    d.save_subbands(gray, out("dwt_subbands.png"))

    target = 12000                      # bytes
    tmp = tempfile.gettempdir()
    best = None
    for q in range(31, 1, -1):          # biggest JPEG that fits the target
        ffmpeg(["-i", IMG, "-q:v", q, os.path.join(tmp, "tmp.jpg")])
        size = os.path.getsize(os.path.join(tmp, "tmp.jpg"))
        if size <= target and (best is None or size > best[1]):
            best = (q, size)
    ffmpeg(["-i", IMG, "-q:v", best[0], out("battle.jpg")])
    best2 = None
    for cl in range(1, 200):            # libopenjpeg: compression_level = ratio
        ffmpeg(["-i", IMG, "-c:v", "libopenjpeg", "-irreversible", 1,
                "-compression_level", cl, os.path.join(tmp, "tmp.jp2")])
        size = os.path.getsize(os.path.join(tmp, "tmp.jp2"))
        if size <= target and (best2 is None or size > best2[1]):
            best2 = (cl, size)
    ffmpeg(["-i", IMG, "-c:v", "libopenjpeg", "-irreversible", 1,
            "-compression_level", best2[0], out("battle.jp2")])
    ffmpeg(["-i", out("battle.jp2"), out("battle_jp2_decoded.png")])
    ffmpeg(["-i", out("battle.jpg"), out("battle_jpg_decoded.png")])
    for name, decoded in (("battle.jpg", "battle_jpg_decoded.png"),
                          ("battle.jp2", "battle_jp2_decoded.png")):
        p, s = quality_report(IMG, out(decoded))
        print("%s: %d bytes, PSNR %.2f dB, SSIM %.4f" % (name, os.path.getsize(out(name)), p, s))


if __name__ == "__main__":
    main()
