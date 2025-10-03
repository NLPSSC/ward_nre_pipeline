

Create a DOS .bat file, `scripts\setup_quickumls`, which does the following:
- clone https://github.com/Georgetown-IR-Lab/QuickUMLS.git to %TEMP%/quickumls
- run python %TEMP%/quickumls/setup.py install
- delete %TEMP%/quickumls
