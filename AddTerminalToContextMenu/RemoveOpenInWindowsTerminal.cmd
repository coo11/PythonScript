@echo off&color 02

@title 移除文件夹右键菜单「Open in Windows Terminal」
mode con: cols=68 lines=24

set P=HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions\Blocked

::显示界面
:start
cls
echo.
echo.       
echo       移除文件夹右键菜单「Open in Windows Terminal」 20200726
:: 解决方案：
:: https://github.com/microsoft/terminal/issues/7008#issuecomment-662621638
:: Stuff 无打算提供删除该菜单的功能。
:: https://github.com/microsoft/terminal/issues/7008#issuecomment-662582609
echo.  
echo.
echo    *************************************************************
echo.
echo                            ① 删除
echo.
echo                            ② 复原
echo.
echo                            ③ 退出
echo.
echo    *************************************************************
echo.

::选择菜单
set /p choice=★ 请输入 1-3 数字选择你要进行的操作：
cls
echo.
set choice=%choice:~0,1%
if /i "%choice%"=="1" goto Remove
if /i "%choice%"=="2" goto recover
if /i "%choice%"=="3" exit
goto start

:Remove
REG add "%P%" /ve /f >nul 2>nul
REG add "%P%" /v "{9F156763-7844-4DC4-B2B1-901F640F5155}" /t REG_SZ /d "WindowsTerminal" /f >nul 2>nul
taskkill /f /im explorer.exe
start explorer
cls
echo.
echo.           
echo                           移除完毕!
echo.  
echo                          按任意键退出         
echo.  
echo.
pause>nul
exit

::恢复
:recover
@echo off
REG delete "%P%" /v "{9F156763-7844-4DC4-B2B1-901F640F5155}" /f >nul 2>nul
taskkill /f /im explorer.exe
start explorer
cls
echo.
echo.           
echo                           恢复完毕!
echo.  
echo                          按任意键退出         
echo.  
echo.
pause>nul
exit