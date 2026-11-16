"""Exercise 8 - Mini-JPEG: gray image -> 8x8 -> DCT -> quant -> zigzag -> RLE."""
from __future__ import annotations

import numpy as np

from dct_codec import DCTCodec
from first_seminar import ColorTranslator
from utils import (IMAGES, OUTPUT, crop, file_size, load_gray,  # noqa: F401
                   merge_blocks, pad_to_multiple, run_ffmpeg, save_image,
                   show_images, split_blocks)


class MiniJPEG:
    """Glue of exercises 5, 6 and 7."""

    def __init__(self, quality: int = 50) -> None:
        self.quality = quality
        self.dct = DCTCodec(quality)
        self.tools = ColorTranslator()

    def encode(self, gray: np.ndarray):
        """uint8 (H, W) -> (payload, (H, W)). Payload = your RLE output."""
        raise NotImplementedError("TODO ex 8")

    def decode(self, payload, shape) -> np.ndarray:
        """Inverse of encode -> uint8 (H, W)."""
        raise NotImplementedError("TODO ex 8")

    @staticmethod
    def psnr(original: np.ndarray, decoded: np.ndarray) -> float:
        """PSNR in dB between two 8-bit images."""
        raise NotImplementedError("TODO ex 8")

    @staticmethod
    def payload_size(payload) -> int:
        """'Compressed' size: number of RLE symbols or bytes (state which)."""
        raise NotImplementedError("TODO ex 8")


def main() -> None:
    gray = load_gray(IMAGES / "test_image.png")
    # TODO ex 8: 3 quality factors -> size + PSNR vs original.
    # TODO ex 8: same with ffmpeg (-q:v N out.jpg) + hardest b/w compression.
    print(gray.shape)


if __name__ == "__main__":
    main()
