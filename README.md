# S1 - Build your own JPEG

## documentation and explanations improved with claude.
## Prompt: "I'm giving you the following zip with a JPEG code execution. I want you to explore it, analize and check how it works and how would you improve it. Give recomendations and you can provide another file "test" to check how would been the results. Add also more required docs if needed to optimise the repository."


## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python first_seminar.py     # prints every result, files go to output/ (not versioned)
pytest -q
```
Needs `ffmpeg` in the PATH (build 9.0.2 Gyan full, with libx264, libx265, libaom, libsvtav1
and libopenjpeg; downloaded, not compiled by us).

## Answers (numbers from `python first_seminar.py`, 512x512 synthetic test image)

**Ex 2.** Round trip RGB->YUV->RGB: max error 1, about 80 % of the pixels change by 1. Cause:
YUV is rounded to uint8 and clipped to 0-255. Using BT.709 or limited range (16-235) in one
direction and BT.601/full range in the other would give larger errors.

**Ex 3.** Lossless ffv1 file size: 4:4:4 108092 B, 4:2:2 83438 B (-23 %), 4:2:0 74418 B (-31 %),
4:1:1 69842 B (-35 %). Blur sigma 8: only chroma 26.98 dB PSNR vs only luma 23.39 dB; the luma
blur is the obvious one (`output/blur_*.png`). The eye resolves brightness detail much better
than colour detail, so JPEG and video codecs keep full-resolution Y and subsample U/V.

**Ex 4.** FFmpeg's `scale` filter uses bicubic by default. 1/2: 139697 B, 1/4: 37208 B, 1/8: 9915 B.
At 1/4, `neighbor` gives 34550 B (blocky, aliased) and `lanczos` 37693 B (sharper).

**Ex 5.** Zigzag orders the coefficients from low to high frequency, so the zeros of the high
frequencies end up together at the end, which is what RLE needs.

**Ex 6.** Non-zero coefficients of one block: 55/64 at quality 95, 24/64 at 50, 3/64 at 10. The
DCT is (almost) lossless; the loss is in the quantization, which kills the high frequencies first.

**Ex 8.** Gray 512x512 (262144 B raw). Mini-JPEG (size = RLE pairs, no entropy coding):

| quality | RLE pairs | PSNR |
|---|---|---|
| 10 | 12610 | 27.70 dB |
| 50 | 30346 | 31.61 dB |
| 90 | 54885 | 43.43 dB |

FFmpeg `-q:v 3 / 10 / 25`: 29953 B / 15796 B / 7734 B, PSNR 42.80 / 33.40 / 28.79 dB. Hardest b/w
(`-q:v 31`): 6753 B, 28.29 dB. FFmpeg wins clearly (real Huffman coding, DC prediction, optimized
tables). Our "bytes" are only an estimate (3 B per pair); the number of pairs is the real measure.

**Ex 9.** At about 12 KB: JPEG 11940 B, PSNR 33.59 dB, SSIM 0.9298; JPEG2000 (libopenjpeg,
9/7 wavelet) 11750 B, 34.66 dB, SSIM 0.9308. JPEG2000 wins, but only by about 1 dB on this image.
Expected artifacts: blocking for JPEG, blur/ringing for JPEG2000 (`output/battle_*_decoded.png`).
Why JPEG is still everywhere: JPEG2000 is much heavier to encode/decode, had patent/licensing
doubts, almost no browser support, and JPEG already had the installed base (cameras, web,
software). JPEG2000 did win in digital cinema (DCP) and medical imaging.
