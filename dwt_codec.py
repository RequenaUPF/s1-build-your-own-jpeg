"""Exercise 9 - DWT (PyWavelets allowed) and JPEG vs JPEG2000 battle."""
from __future__ import annotations

import numpy as np

from utils import IMAGES, OUTPUT, load_gray, run_ffmpeg, show_images  # noqa: F401


class DWTCodec:
    """Single/multi-level 2D DWT encode and decode."""

    def __init__(self, wavelet: str = "haar", level: int = 1) -> None:
        self.wavelet = wavelet
        self.level = level

    def decompose(self, gray: np.ndarray):
        """2D DWT. Return the coefficient structure you will reuse below."""
        raise NotImplementedError("TODO ex 9")

    def reconstruct(self, coeffs) -> np.ndarray:
        """Inverse DWT."""
        raise NotImplementedError("TODO ex 9")

    def subbands(self, gray: np.ndarray) -> dict:
        """Dict with keys 'LL', 'LH', 'HL', 'HH' (first level)."""
        raise NotImplementedError("TODO ex 9")

    def show_subbands(self, gray: np.ndarray, save_as=None) -> None:
        """Plot LL, LH, HL, HH."""
        raise NotImplementedError("TODO ex 9")


def battle() -> None:
    # TODO ex 9: same file size, JPEG vs JPEG2000 (ffmpeg -c:v jpeg2000),
    # psnr/ssim filters, screenshots of artifacts.
    pass


if __name__ == "__main__":
    battle()
