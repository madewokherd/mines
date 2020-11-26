# Setup instructions for Fuzzy Logic restreamers

Install Python 3.8 or later.

Install Pygame. This can be done by running the command:
```
python -m pip install pygame
```

Download and extract: https://github.com/madewokherd/mines/archive/fuzzylogic.zip

Run this command from the directory where you extracted the zip:
```
python dreamsweeper-sdl.py 30 16 99 /r /0 /mm /mc /s /dd /ac /iedgecasecollective
```

You should have a minesweeper-looking window.

Add fuzzylogic-layout.png (4:3) to the layout.

Add a window capture, scale it to 900x480, and place it as indicated in the layout. The grid should line up with the row and column labels.
