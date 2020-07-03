# 使用 pyInstaller 打包

### 打包时添加同目录的其他文件
1. 在脚本目录执行 `pyi-makespec -F setup.py` 命令生成 spec 文件
2. 编辑 spec 文件，在 datas 的方括号中填入二维元组，如 `datas = [('src', 'src')]`，表示把当前目录中的 `src` 文件夹打包，执行时再释放到临时文件夹的根目录的 `src` 文件夹中
3. 执行 `pyinstaller -F setup.spec` 打包


### 代码中可能需要改动内容
1. 对于代码中使用的绝对路径 ([Reference](https://www.zhihu.com/question/268105244/answer/771295481))：

    ```Python
    from os import path
    import sys
    bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
    path_to_dat = path.join(bundle_dir, 'other-file.dat')
    ```
2. 提升用户权限 ([Reference](https://stackoverflow.com/a/11746382))：

    ```Python
    import ctypes, sys

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
    # Code of your program here
    else:
    # If converted python script into an executable file, use `sys.argv[1:]` in the following line instead of `sys.argv`
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    ```