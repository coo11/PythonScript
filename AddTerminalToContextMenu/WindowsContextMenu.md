## 关于右键上下文菜单的 PowerShell 和命令提示符

### 权限问题
- [资料来源](https://jingyan.baidu.com/article/3aed632ec4b9257010809183.html)

1. 右击项，点开权限→高级→审核；
2. 更改上方的所有者为 Administrators；
3. 在审核→添加中重复上一条并授予完全控制权限；
4. 返回权限对话框，组或用户名中对 Administrators 勾选完全控制即可。
5. 对于子项权限修改，仅需重复 1，2，4 条即可。

### 需要修改的注册表分支

- 实测仅修改分支 `HKEY_CLASSES_ROOT\Directory\` 下的 `Background` 影响桌面或 Explorer。

- 「文件夹上下文菜单」的修改在分支 `HKEY_CLASSES_ROOT\Directory\shell` 下进行。

### 需要修改的键值对
1. `ShowBasedOnVelocityId` 和 `HideBasedOnVelocityId`，通过修改键名决定隐藏与否。
2. `Position: Bottom`，修改显示于菜单的哪个层级。
3. `Extended` 决定是否需要按下 {Shift}。
4. `Icon` 修改图标。

### 配置记录

对于 CMD：
- 以管理员权限运行：修改子项 `command` 的默认值为
    ```
    mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/s /k pushd %V","","runas")(close)
    ```
- 图标路径： `C:\Windows\SystemResources\imageres.dll.mun,-5323`

### 关于图标问题
- Icons no longer in imageres.dll in Windows 10 1903 - 4kb file
 [StackExchange](https://superuser.com/questions/1480268/)
- 资源路径
    - `C:\Windows\SystemResources\shell32.dll.mun`
    - `C:\Windows\SystemResources\imageres.dll.mun`