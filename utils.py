"""Boilerplate helpers provided by the environment.

Nothing here is part of the exercises: image I/O, block (un)tiling,
plotting and a thin wrapper around the ffmpeg binary.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------- image I/O
def load_rgb(path) -> np.ndarray:
    """Load an image as uint8 array of shape (H, W, 3)."""
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def load_gray(path) -> np.ndarray:
    """Load an image as uint8 array of shape (H, W) (luma, 8 bit)."""
    return np.asarray(Image.open(path).convert("L"), dtype=np.uint8)


def save_image(arr: np.ndarray, path) -> None:
    """Save an array (clipped to 0-255, cast to uint8) as an image file."""
    Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8)).save(path)


# ------------------------------------------------------------ block helpers
def pad_to_multiple(img: np.ndarray, n: int = 8):
    """Edge-pad H and W up to a multiple of n. Returns (padded, (H, W))."""
    h, w = img.shape[:2]
    pad = ((0, (-h) % n), (0, (-w) % n)) + ((0, 0),) * (img.ndim - 2)
    return np.pad(img, pad, mode="edge"), (h, w)


def crop(img: np.ndarray, shape) -> np.ndarray:
    """Undo pad_to_multiple: crop back to the original (H, W)."""
    return img[: shape[0], : shape[1]]


def split_blocks(img: np.ndarray, n: int = 8) -> np.ndarray:
    """(H, W) -> (H/n, W/n, n, n). H and W must be multiples of n."""
    h, w = img.shape
    assert h % n == 0 and w % n == 0, "pad the image first (pad_to_multiple)"
    return img.reshape(h // n, n, w // n, n).swapaxes(1, 2)


def merge_blocks(blocks: np.ndarray) -> np.ndarray:
    """(H/n, W/n, n, n) -> (H, W). Inverse of split_blocks."""
    by, bx, n, _ = blocks.shape
    return blocks.swapaxes(1, 2).reshape(by * n, bx * n)


# ------------------------------------------------------------------- ffmpeg
def run_ffmpeg(args, check: bool = True) -> subprocess.CompletedProcess:
    """Run `ffmpeg -y -hide_banner <args>`; stdout/stderr are captured.

    Filters such as psnr/ssim print their report on stderr
    (result.stderr). Raises RuntimeError with the log if ffmpeg fails.
    """
    exe = shutil.which("ffmpeg")
    if exe is None:
        raise RuntimeError("ffmpeg not found in PATH (exercise 1)")
    cmd = [exe, "-y", "-hide_banner", *map(str, args)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(cmd)}\n{res.stderr}")
    return res


def file_size(path) -> int:
    """Size in bytes of a file."""
    return Path(path).stat().st_size


# ----------------------------------------------------------------- plotting
def show_images(images, titles=None, save_as=None, cmap=None) -> None:
    """Plot several images side by side; optionally save the figure."""
    fig, axes = plt.subplots(1, len(images), figsize=(4 * len(images), 4))
    axes = np.atleast_1d(axes)
    for i, (ax, im) in enumerate(zip(axes, images)):
        ax.imshow(im, cmap=cmap or ("gray" if np.ndim(im) == 2 else None))
        ax.axis("off")
        if titles:
            ax.set_title(titles[i])
    fig.tight_layout()
    if save_as:
        fig.savefig(save_as, dpi=150)
    plt.show()
