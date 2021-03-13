cd /D %~dp0
pyinstaller -F --upx-exclude=vcruntime140.dll config.py
move /Y .\dist\config.exe config.exe
rd /Q /S build dist
del *.spec /Q /F