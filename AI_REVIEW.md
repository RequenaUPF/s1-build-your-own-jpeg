# AI review (exercise 10)

## Prompts used
1. "Review `first_seminar.py` (a mini JPEG encoder: given the slides): correctness bugs, edge cases, readability and PEP8. List each suggestion."
2. "Write pytest unit tests for each class and method of `first_seminar.py`."

## Suggestions
| # | Suggestion | Decision | Why |
|---|---|---|---|
| 1 | `DCTCodec` does not validate `quality`: 0 crashes with ZeroDivisionError, 101 and negatives give silently wrong tables | Accepted | Real bug, found by the tests (3 failures). Fixed: `ValueError` if not 1-100 |
| 2 | Lines longer than 79 chars (PEP8) | Partly accepted | Wrapped everything over 100 and set `max-line-length = 100` in `setup.cfg` (PEP8 allows a team limit); 79 not enforced |
| 3 | Temporary files of the size search written into `output/` | Accepted | Moved to the system temp folder |
| 4 | The reported size of mini-JPEG (3 bytes per pair) is arbitrary | Accepted (docs only) | Kept the code, README says it is an estimate and the number of RLE pairs is the real measure |
| 5 | Split `main()` into one function per exercise | Rejected | Each printed block already maps 1:1 to an exercise; more functions = more indirection for a lab script |
| 6 | Binary search instead of looping over all qualities / compression levels (about 230 ffmpeg calls, 30 s) | Rejected | File size is not guaranteed monotonic in the quality parameter, and 30 s is fine |
| 7 | Code DC coefficients differentially (as real JPEG does) | Rejected | Out of scope: the statement stops at RLE |
| 8 | JPEG-style RLE (zero run, value) instead of (value, count) | Rejected | The statement asks for generic RLE of a series; it round-trips and is simpler to explain |
| 9 | Add Huffman coding | Rejected | Bonus only |
| 10 | Support colour in mini-JPEG (Cb/Cr, 4:2:0) | Rejected | Statement: grayscale or Y channel |
| 11 | Compute the zigzag order instead of hardcoding the table | Rejected | The table is the standard (T.81); the test checks it is a permutation and its first values |
| 12 | Add type hints and docstrings everywhere | Partly rejected | Docstrings only where the contract is not obvious |
| 13 | PSNR/SSIM of JPEG vs JPEG2000 forced both files to `yuv444p`; the result changed between two ffmpeg versions (JPEG 33.59 dB vs 32.32 dB) | Accepted | Found when running on a second machine. Now both files are decoded to PNG (RGB) and compared with the same pixel format |

## Tests (`test_first_seminar.py`, `pytest -q`)
26 tests. First run: 23 passed, 3 failed (`quality` 0, -5, 101). **Whose fault?** The code's:
the tests were right and the validation was missing (suggestion 1). After the fix: 26 passed.
