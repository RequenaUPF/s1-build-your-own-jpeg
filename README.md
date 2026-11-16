# S1 – Build your own JPEG (Lab 1 · Vídeo)

Enunciat: `../../Teoria/Lab1/01 - S1 - Build your own JPEG (2026).pptx`

## Política d'IA (slide 5)
Exercicis 1-9: **cap IA**. Només l'exercici 10 (revisió de codi + tests per IA,
amb `AI_REVIEW.md` amb prompts i taula suggeriment → acceptat/rebutjat → per què).

## Setup (Windows, PowerShell)
```powershell
cd "...\Video\Labs\Lab1"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
winget install Gyan.FFmpeg      # reobre la terminal després
ffmpeg -version
git init                        # un commit per exercici: l'historial puntua
```

## Estructura
| Fitxer | Exercicis | Què hi implementes |
|---|---|---|
| `first_seminar.py` | 2, 3, 4, 5, 7 | `ColorTranslator`: YUV, chroma, resize, zigzag, RLE |
| `dct_codec.py` | 6 | `DCTCodec`: DCT-II 8x8 + quantització amb quality |
| `mini_jpeg.py` | 8 | `MiniJPEG`: pipeline complet + PSNR + comparació FFmpeg |
| `dwt_codec.py` | 9 | `DWTCodec`: subbandes LL/LH/HL/HH + batalla JPEG vs JPEG2000 |
| `utils.py` | — | Ja fet: I/O, blocs 8x8, wrapper ffmpeg, plots |
| `images/` | — | `test_image.png` sintètica; substitueix-la per la "class image" d'Aula Global (<few MB) |
| `evidence/` | 1, 3, 9 | Captures (`ffmpeg -version`, `-codecs`, artefactes). Es puja a GitHub |
| `output/` | — | Resultats generats; ignorat per git |
| `_checks/` | — | Autocomprovacions locals; ignorat per git, NO es lliura |

Cada stub llança `NotImplementedError("TODO ex N")` i el docstring fixa el contracte
(entrades/sortides). La resta és lliure.

## Ordre de treball
1 → 2 → 5 → 7 → 6 → 8 (nucli) → 3 → 4 → 9 → 10 → bonus.
Els exercicis 2, 5, 7 i 6 són peces independents; el 8 només les enganxa.

## Autocomprovació
```powershell
python _checks\run_checks.py          # tots
python _checks\run_checks.py ex5      # un de sol
```

## Lliurament
Enllaç a GitHub a Aula Global. No pujar imatges/vídeos de més d'uns pocs MB.
