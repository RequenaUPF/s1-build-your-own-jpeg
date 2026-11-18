"""Unit tests (exercise 10). Run:  pytest -q"""
import numpy as np
import pytest
from scipy.fft import dctn

from first_seminar import (QTABLE, ZIGZAG, ColorTranslator, DCTCodec,
                           DWTCodec, MiniJPEG, psnr)

RNG = np.random.default_rng(0)


# ---- psnr
def test_psnr_identical_is_inf():
    a = RNG.integers(0, 256, (8, 8), dtype=np.uint8)
    assert psnr(a, a) == float("inf")


def test_psnr_known_value():
    a = np.zeros((4, 4), dtype=np.uint8)
    b = np.full((4, 4), 255, dtype=np.uint8)
    assert psnr(a, b) == pytest.approx(0.0)


# ---- ColorTranslator
def test_yuv_roundtrip_error_is_small():
    ct = ColorTranslator()
    img = RNG.integers(0, 256, (16, 16, 3), dtype=np.uint8)
    back = ct.yuv_to_rgb(ct.rgb_to_yuv(img))
    assert back.dtype == np.uint8 and back.shape == img.shape
    assert np.abs(back.astype(int) - img).max() <= 2


def test_gray_has_neutral_chroma():
    yuv = ColorTranslator().rgb_to_yuv(np.full((1, 1, 3), 100, np.uint8))
    assert tuple(yuv[0, 0]) == (100, 128, 128)


def test_white_and_black():
    ct = ColorTranslator()
    assert tuple(ct.rgb_to_yuv(np.full((1, 1, 3), 255, np.uint8))[0, 0]) == (255, 128, 128)
    assert tuple(ct.rgb_to_yuv(np.zeros((1, 1, 3), np.uint8))[0, 0]) == (0, 128, 128)


def test_blur_keeps_shape():
    ct = ColorTranslator()
    img = RNG.integers(0, 256, (16, 16, 3), dtype=np.uint8)
    assert ct.blur_chroma(img, 2).shape == img.shape
    assert ct.blur_luma(img, 2).shape == img.shape


def test_zigzag_table_is_a_permutation_with_known_start():
    assert sorted(ZIGZAG) == list(range(64))
    assert ZIGZAG[:6] == [0, 1, 8, 16, 9, 2]


def test_zigzag_roundtrip():
    ct = ColorTranslator()
    m = np.arange(64).reshape(8, 8)
    seq = ct.zigzag(m)
    assert len(seq) == 64
    assert np.array_equal(ct.inverse_zigzag(seq), m)


@pytest.mark.parametrize("seq", [[], [5], [1, 2, 3], [0] * 63,
                                 [7, 0, 0, 0, 3, 3, 0], [1] * 100])
def test_rle_roundtrip(seq):
    ct = ColorTranslator()
    assert ct.rle_decode(ct.rle_encode(seq)) == seq


def test_rle_groups_runs():
    assert ColorTranslator().rle_encode([0, 0, 0, 4, 4]) == [(0, 3), (4, 2)]


# ---- DCTCodec
def test_quant_table_extremes():
    assert np.array_equal(DCTCodec(50).qtable, QTABLE)
    assert (DCTCodec(100).qtable == 1).all()
    assert DCTCodec(10).qtable.mean() > DCTCodec(90).qtable.mean()


@pytest.mark.parametrize("bad", [0, -5, 101])
def test_quality_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError):
        DCTCodec(bad)


def test_block_roundtrip_high_quality():
    c = DCTCodec(100)
    b = RNG.integers(0, 256, (8, 8), dtype=np.uint8)
    assert np.abs(c.decode_block(c.encode_block(b)).astype(int) - b).max() <= 2


def test_dc_of_flat_block():
    q = DCTCodec(100).encode_block(np.full((8, 8), 200, np.uint8))
    assert q[0, 0] == round(dctn(np.full((8, 8), 72.0), norm="ortho")[0, 0])
    assert np.count_nonzero(q) == 1


def test_lower_quality_zeroes_more_coefficients():
    b = RNG.integers(0, 256, (8, 8), dtype=np.uint8)
    assert np.count_nonzero(DCTCodec(10).encode_block(b)) < \
        np.count_nonzero(DCTCodec(90).encode_block(b))


# ---- MiniJPEG
def test_minijpeg_shape_not_multiple_of_8():
    img = RNG.integers(0, 256, (70, 90), dtype=np.uint8)
    mj = MiniJPEG(50)
    payload, shape = mj.encode(img)
    out = mj.decode(payload, shape)
    assert out.shape == img.shape and out.dtype == np.uint8


def test_minijpeg_quality_vs_psnr_and_size():
    yy, xx = np.mgrid[0:64, 0:64]
    img = (128 + 60 * np.sin(xx / 7) + 40 * np.cos(yy / 5)).astype(np.uint8)
    res = {}
    for q in (10, 50, 90):
        mj = MiniJPEG(q)
        p, s = mj.encode(img)
        res[q] = (psnr(img, mj.decode(p, s)), mj.n_pairs(p))
    assert res[10][0] < res[50][0] < res[90][0]
    assert res[10][1] < res[90][1]


# ---- DWTCodec
def test_dwt_perfect_reconstruction():
    img = RNG.integers(0, 256, (32, 32)).astype(float)
    d = DWTCodec()
    assert np.allclose(d.reconstruct(d.decompose(img)), img)


def test_dwt_subbands_shape():
    sb = DWTCodec().subbands(np.zeros((32, 32)))
    assert set(sb) == {"LL", "LH", "HL", "HH"}
    assert all(v.shape == (16, 16) for v in sb.values())
