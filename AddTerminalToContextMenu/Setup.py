# -*- coding: utf-8 -*-

from winreg import *
import ctypes, json, sys, os, re

TREE = 'SOFTWARE\Classes\Directory'
CACHE = f'{os.environ["LOCALAPPDATA"]}\Microsoft\WindowsApps\Cache'

def setup():
    includePreview = ask('Do you want to add context menu if preview version detected?')
    config = f'{os.environ["LOCALAPPDATA"]}\Packages\Microsoft.WindowsTerminal{["","Preview"][includePreview]}_8wekyb3d8bbwe\LocalState\settings.json'
    if includePreview and not os.path.exists(config):
        config = config.replace('WindowsTerminalPreview', 'WindowsTerminal', 1)
    if not os.path.exists(config):
        raise Exception('Windows Terminal configuration file not detected.')
    terminalList = loadJson(config)['profiles']['list']
    # terminalList = [i for i in terminalList if not i["hidden"] or not 'hidden' in i]
    terminalList = [i for i in terminalList if not 'hidden' in i or not i["hidden"]]
    isNeedAdmin = isAdmin()
    if isNeedAdmin:
        isNeedAdmin = ask('Do you want to add context menu which can run as administrator?')
    setupSrcDir(isNeedAdmin)
    info = setSubmenuItems(terminalList)
    setRegistry(info, isNeedAdmin)

def isScriptInstalled():
    try:
        handle = OpenKey(HKEY_CURRENT_USER, f'{TREE}\Background\shell\WTerminal')
        CloseKey(handle)
        return True
    except:
        return False

def uninstall():
    deleteSubkey(OpenKey(HKEY_CURRENT_USER, f'{TREE}\Background\shell\WTerminal'))
    deleteSubkey(OpenKey(HKEY_CURRENT_USER, f'{TREE}\ContextMenus\WTerminal'))
    if os.path.exists(f'{CACHE}\helper.vbs'):
        os.remove(f'{CACHE}\helper.vbs')
    wt_src = f'{CACHE}\wt_src'
    if os.path.exists(wt_src):
        for i in os.listdir(wt_src):
            os.remove(os.path.join(wt_src, i))
        os.rmdir(wt_src)

# https://stackoverflow.com/a/40183836
# Use winreg delete registry key with its subkeys
def deleteSubkey(key):
    info = QueryInfoKey(key)
    for i in range(0, info[0]):
        # CAUTION: MUST BE 0 ↓
        subkey = EnumKey(key, 0)
        try:
            DeleteKey(key, subkey)
        except:
            deleteSubkey(OpenKey(key, subkey))
    DeleteKey(key, '')
    key.Close()

def setRegistry(info, isNeedAdmin):
    with CreateKey(HKEY_CURRENT_USER, f'{TREE}\Background\shell\WTerminal') as key:
        SetValueEx(key,'ExtendedSubCommandsKey', 0, REG_SZ, r'Directory\ContextMenus\WTerminal')
        SetValueEx(key,'Icon', 0, REG_SZ, rf'{CACHE}\wt_src\wt.ico')
        SetValueEx(key,'MUIVerb', 0, REG_SZ, r'在此处打开 Windows Terminal(&W)')
        # comment out next line if [Shift] to display not used↓
        SetValueEx(key,'Extended', 0, REG_SZ, '')
        SetValueEx(key,'Position', 0, REG_SZ, 'Bottom')
    for i in info:
        with CreateKey(HKEY_CURRENT_USER, f'{TREE}\ContextMenus\WTerminal\shell\{i["name"]}') as key:
            # Show little shield ↓
            if isNeedAdmin: SetValueEx(key,'HasLUAShield', 0, REG_SZ, '')
            SetValueEx(key,'MUIVerb', 0, REG_SZ, i['name'])
            SetValueEx(key,'Icon', 0, REG_SZ, rf'{CACHE}\wt_src\{i["name"]}.ico')
            with CreateKey(key, 'command') as cmd:
                if isNeedAdmin:
                    value = rf'wscript.exe "{CACHE}\helper.vbs" "{os.environ["LOCALAPPDATA"]}\Microsoft\WindowsApps\wt.exe" "%V." "{i["name"]}"'
                else:
                    value = rf'"{os.environ["LOCALAPPDATA"]}\Microsoft\WindowsApps\wt.exe" -p "{i["name"]}" -d "%V."'
                SetValue(cmd, '', REG_SZ, value)

def setSubmenuItems(terminalList):
    info = []
    cpath = os.path.split(os.path.realpath(__file__))[0]
    # For just excuting script ↑
    # For using pyInstaller package to exe ↓
    # https://www.zhihu.com/question/268105244/answer/771295481
    # cpath = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    os.system(rf'copy /y "{cpath}\src\wt.ico" "{CACHE}\wt_src\wt.ico"')
    def execute(i, path):
        print(i)
        print(rf'copy /y "{cpath}\{path}" "{CACHE}\wt_src\{i["name"]}.ico"')
        os.system(rf'copy /y "{cpath}\{path}" "{CACHE}\wt_src\{i["name"]}.ico"')
        info.append({'name': i['name']})
    for i in terminalList:
        if 'python' in i['name'].lower():
            execute(i, 'src\py.ico')
        elif '命令提示符' in i['name'].lower() or 'command' in i['name'].lower():
            execute(i, 'src\cmd.ico')
        elif 'powershell' in i['name'].lower():
            execute(i, 'src\ps.ico')
        elif 'git' in i['name'].lower():
            execute(i, 'src\git.ico')
        elif 'node' in i['name'].lower():
            execute(i, r'src\nodejs.ico')
        elif 'icon' in i and i['icon'].endswith('.ico'):
            execute(i, i['icon'])
    return info

def setupSrcDir(needAdmin):
    if not os.path.exists(f'{CACHE}\wt_src'): os.makedirs(f'{CACHE}\wt_src')
    if needAdmin:
    # mshta vbscript:CreateObject("Shell.Application").ShellExecute("some program.exe","some parameters with spaces","dir","runas",0)(close)
        with open(f'{CACHE}\helper.vbs', 'w') as f:
            f.write(r'''Set shell = WScript.CreateObject("Shell.Application")
executable = WSCript.Arguments(0)
folder = WScript.Arguments(1)
If Wscript.Arguments.Count > 2 Then
    profile = WScript.Arguments(2)
    ' 0 at the end means to run this command silently
    shell.ShellExecute "powershell", "Start-Process \""" & executable & "\"" -ArgumentList \""-p \""\""" & profile & "\""\"" -d \""\""" & folder & "\""\"" \"" ", "", "runas", 0
Else
    ' 0 at the end means to run this command silently
    shell.ShellExecute "powershell", "Start-Process \""" & executable & "\"" -ArgumentList \""-d \""\""" & folder & "\""\"" \"" ", "", "runas", 0
End If''')


def ask(question, isChoice = True):
    A = 'Entered any key to continue or {Ctrl + C} to cancel.'
    B = 'Entered "y" to accept or any other key to deny.'
    try:
        entered = input(f'{question}\n{(A, B)[isChoice]}')
    except:
        print('Installation Cancelled.')
        os.system('pause')
        quit()
    if isChoice:
        if entered.lower() == 'y': return True
        else: return False

def getProgramFilesPath(includePreview):
    folders = f'{os.environ["ProgramFiles"]}\WindowsApps'
    wtDirs = [ name for name in os.listdir(folders) if name[0:25] == 'Microsoft.WindowsTerminal']
    wtFolderName = None
    ver = '0.0.0.0'
    for wtDir in wtDirs:
        matched = re.match(rf'Microsoft\.WindowsTerminal(Preview)?_(\d+\.\d+\.\d+\.\d+).+__', wtDir, re.I)
        if matched:
            if matched.group(1) and not includePreview:
                continue
            else:
                foundVer = matched.group(2)
                print(f'Found Windows Terminal version {foundVer}.')
            if isFoundNew(foundVer, ver):
                ver = foundVer
                wtFolderName = wtDir
        else: print(f'Found Windows Terminal unsupported version in {wtDir}.')
    if not isFoundNew(foundVer, '0.11.0.0'):
        raise Exception('The latest version found is less than 0.11, which is not tested. The install script might fail in certain way.')
    if not wtFolderName:
        raise Exception("Failed to find Windows Terminal actual folder. The install script might fail in certain way.")
    return f'{os.environ["ProgramFiles"]}\WindowsApps\{wtFolderName}'

def isFoundNew(foundVer, currentVer):
    for [n, m] in zip(foundVer.split('.'), currentVer.split('.')):
        n = int(n)
        m = int(m)
        if n > m: return True
        elif n == m: continue
        else: return False
    return False

# Way to solve parsing JSON with comments
# https://zhuanlan.zhihu.com/p/99682140
class xstr:
    def __init__(self, instr):
        self.instr = instr
    # 删除“//”标志后的注释
    def rmCmt(self): 
        qtCnt = cmtPos = slashPos = 0
        rearLine = self.instr
        # rearline: 前一个“//”之后的字符串，
        # 双引号里的“//”不是注释标志，所以遇到这种情况，仍需继续查找后续的“//”
        while rearLine.find('//') >= 0: # 查找“//”
            slashPos = rearLine.find('//')
            cmtPos += slashPos
            # print 'slashPos: ' + str(slashPos)
            headLine = rearLine[:slashPos]
            while headLine.find('"') >= 0: # 查找“//”前的双引号
                qtPos = headLine.find('"')
                if not self.isEscapeOpr(headLine[:qtPos]): # 如果双引号没有被转义
                    qtCnt += 1 # 双引号的数量加1
                headLine = headLine[qtPos+1:]
                # print qtCnt
            if qtCnt % 2 == 0: # 如果双引号的数量为偶数，则说明“//”是注释标志
                # print self.instr[:cmtPos]
                return self.instr[:cmtPos]
            rearLine = rearLine[slashPos+2:]
            # print rearLine
            cmtPos += 2
        # print self.instr
        return self.instr
    # 判断是否为转义字符
    def isEscapeOpr(self, instr):
        if len(instr) <= 0:
            return False
        cnt = 0
        while instr[-1] == '\\':
            cnt += 1
            instr = instr[:-1]
        if cnt % 2 == 1:
            return True
        else:
            return False

def loadJson(JsonPath, code = 'utf-8'):
    try:
        srcJson = open(JsonPath, 'r', encoding = code)
    except:
        print(f'ERROR: cannot open {JsonPath}.')
    dstJsonStr = ''
    for line in srcJson.readlines():
        if not re.match(r'\s*//', line) and not re.match(r'\s*\n', line):
            xline = xstr(line)
            dstJsonStr += xline.rmCmt()
    dstJson = {}
    try:
        dstJson = json.loads(dstJsonStr)
        return dstJson
    except:
        print(f'ERROR: {JsonPath} is not a valid json file.')

# Request elevation
# https://stackoverflow.com/a/11746382
def isAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

exeDir = f'{os.environ["LOCALAPPDATA"]}\Microsoft\WindowsApps'
if isScriptInstalled():
    isUninstall = ask('Installation detected. Uninstall it?', False)
    uninstall()
    print('Uninstall Finished.')
    os.system('pause')
elif 'wt.exe' not in os.listdir(exeDir):
    raise Exception('Windows Terminal not detected.')
else:
    tip = ask(f'''WARNING:
    You are installing this script for user \'{os.environ["USERNAME"]}\'. 
    If installing for current user which is inconsistent with the former identity, 
    maybe you should run this script directly instead of running as administrator.''', False)
    setup()
    print('Setup Finished.')
    os.system('pause')
# if isAdmin():
#     pass
# else:
#     If converted python script into an executable file, use `sys.argv[1:]` in the following line instead of `sys.argv` May not work if use non-admin account
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)