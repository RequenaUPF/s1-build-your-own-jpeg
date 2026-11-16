"""S1 - Build your own JPEG: colour, chroma, resize, zigzag, RLE.

Exercises 2, 3, 4, 5 and 7 live here (all as methods of ColorTranslator).
Exercise 6 -> dct_codec.py, 8 -> mini_jpeg.py, 9 -> dwt_codec.py.

Sources consulted (cite anything you copy, as the statement requires):
  - TODO
"""
from __future__ import annotations

import numpy as np

from utils import IMAGES, OUTPUT, load_rgb, run_ffmpeg  # noqa: F401


class ColorTranslator:
    """Colour conversion + the small JPEG building blocks."""

    # ------------------------------------------------------------- ex 2
    def rgb_to_yuv(self, rgb: np.ndarray) -> np.ndarray:
        """BT.601 RGB -> YUV. Input (..., 3) uint8; output (..., 3).

        Decide and document: full vs limited range, offsets, dtype.
        """
        raise NotImplementedError("TODO ex 2")

    def yuv_to_rgb(self, yuv: np.ndarray) -> np.ndarray:
        """Inverse of rgb_to_yuv. Output (..., 3) uint8, clipped to 0-255."""
        raise NotImplementedError("TODO ex 2")

    # ------------------------------------------------------------- ex 3
    def export_pix_fmt(self, src, dst, pix_fmt: str) -> None:
        """Use ffmpeg (-pix_fmt) to export src into dst with that format."""
        raise NotImplementedError("TODO ex 3")

    def blur_chroma(self, rgb: np.ndarray, sigma: float) -> np.ndarray:
        """Blur only U and V, keep Y. Returns RGB uint8."""
        raise NotImplementedError("TODO ex 3")

    def blur_luma(self, rgb: np.ndarray, sigma: float) -> np.ndarray:
        """Blur only Y, keep U and V. Returns RGB uint8."""
        raise NotImplementedError("TODO ex 3")

    # ------------------------------------------------------------- ex 4
    def resize(self, src, dst, factor: int, sws_flags: str | None = None):
        """Resize src to 1/factor of its size with ffmpeg (subprocess)."""
        raise NotImplementedError("TODO ex 4")

    # ------------------------------------------------------------- ex 5
    def zigzag(self, block: np.ndarray) -> list:
        """Read an 8x8 matrix in zigzag order -> list of 64 values."""
        raise NotImplementedError("TODO ex 5")

    def inverse_zigzag(self, seq) -> np.ndarray:
        """List of 64 values -> 8x8 matrix. Inverse of zigzag."""
        raise NotImplementedError("TODO ex 5")

    # ------------------------------------------------------------- ex 7
    def rle_encode(self, seq) -> list:
        """Run-length encode a series. Pair format is your design choice;
        the contract is rle_decode(rle_encode(x)) == x."""
        raise NotImplementedError("TODO ex 7")

    def rle_decode(self, pairs) -> list:
        """Inverse of rle_encode."""
        raise NotImplementedError("TODO ex 7")


def main() -> None:
    ct = ColorTranslator()
    img = load_rgb(IMAGES / "test_image.png")
    # TODO ex 2: round trip RGB -> YUV -> RGB, report max error and why.
    # TODO ex 3: file sizes for 444/422/420/411, blurred chroma vs luma.
    # TODO ex 4: resize to 1/2, 1/4, 1/8 + compare scaling algorithms.
    print(img.shape, ct)


if __name__ == "__main__":
    main()
