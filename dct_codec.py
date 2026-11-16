"""Exercise 6 - 8x8 DCT + quantization with a quality factor (1-100)."""
from __future__ import annotations

import numpy as np

# Standard JPEG luminance quantization table (ITU-T T.81, Annex K.1).
BASE_LUMA_QTABLE = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99],
], dtype=np.float64)


class DCTCodec:
    """Encode/decode one 8x8 block: DCT-II -> quantization (and back)."""

    def __init__(self, quality: int = 50) -> None:
        self.quality = quality
        self.qtable = self.quant_table(quality)

    def quant_table(self, quality: int) -> np.ndarray:
        """Scale BASE_LUMA_QTABLE by quality (1-100). Entries must be >= 1."""
        raise NotImplementedError("TODO ex 6")

    def dct2(self, block: np.ndarray) -> np.ndarray:
        """2D DCT-II of an 8x8 block (orthonormal)."""
        raise NotImplementedError("TODO ex 6")

    def idct2(self, coeffs: np.ndarray) -> np.ndarray:
        """Inverse 2D DCT."""
        raise NotImplementedError("TODO ex 6")

    def quantize(self, coeffs: np.ndarray) -> np.ndarray:
        """coeffs / qtable, rounded to integers."""
        raise NotImplementedError("TODO ex 6")

    def dequantize(self, q: np.ndarray) -> np.ndarray:
        """q * qtable."""
        raise NotImplementedError("TODO ex 6")

    def encode_block(self, block: np.ndarray) -> np.ndarray:
        """uint8 8x8 block -> quantized int 8x8 (level shift included)."""
        raise NotImplementedError("TODO ex 6")

    def decode_block(self, q: np.ndarray) -> np.ndarray:
        """Quantized 8x8 -> uint8 8x8 block (clipped to 0-255)."""
        raise NotImplementedError("TODO ex 6")


if __name__ == "__main__":
    # TODO ex 6: show how high-frequency coefficients vanish as quality drops.
    pass
