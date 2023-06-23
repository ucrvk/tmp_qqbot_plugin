import wx
from requests import get, post
import os
import winshell
from zipfile import ZipFile
from pathlib import Path
from wget import download
from shutil import rmtree
import sys
import json
import webbrowser
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                  ' x64) AppleWebKit/537.36 (KHTML, like'
                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'app-version-code': '65535',
}


def get_shortcut_target(shortcut_path):
    try:
        # 使用winshell模块打开快捷方式
        shortcut = winshell.shortcut(shortcut_path)
        # 获取目标路径
        target_path = shortcut.path
        # 检查目标路径是否存在
        if os.path.exists(target_path):
            return target_path
        else:
            return None
    except Exception as e:
        print("Error accessing shortcut:", e)
        return None


DOCUMENTS_DIR = Path(os.path.expanduser(
    r'~\Documents\Euro Truck Simulator 2\profiles'))
GAME_DIR = get_shortcut_target(os.path.expanduser(
    r'~\Documents\Euro Truck Simulator 2\readme.rtf.lnk')).rstrip("readme.rtf")


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def logIn(username: str, password: str):
    json = {"username": username, "password": password}
    ans = post('http://manage.rpgvtc.cn/api/app/login',
               json=json, headers=header)
    if not ans.status_code == 200:
        return -1
    if ans.json()["code"] == 0:
        return ans.json()["token"]
    else:
        return ans.json()["code"]


def getActivity(token):
    tempHeader = header
    tempHeader.update(token=token)
    ans = get('http://manage.rpgvtc.cn/api/app/activity/currentDay',
              headers=tempHeader)
    if not ans.status_code == 200:
        return -1
    else:
        if ans.json()["code"] == 0:
            if not ans.json()["data"]:
                return 0
            else:
                return ans.json()["data"]
        else:
            return ans.json()["code"]


def activitySign(activity: dict):
    ans = ["检测到活动：\n", "活动名称：", activity['themeName'], "\n起点：", activity['startingPoint'], "\n终点：", activity['terminalPoint'],
           "\n长度：", str(activity['distance']), "km\n服务器名称：", activity['serverName'], "\n开始时间：", activity['startTime'], "\n是否安装存档？"]
    return ''.join(ans)


def loginErrorCompose(errorCode):
    if errorCode == 500:
        return "登录失败，原因：密码错误\n如果需要token登录，请保证账号栏为空。如果忘记了密码，请联系keyang或拾柒\n错误代码：500    错误阶段：1.1"
    elif errorCode == -1:
        return "登录失败，原因：无法连接到服务器\n请检查您的网络，并尝试重新接档，当然，也可能是服务器炸了\n错误代码：-1    错误阶段：1.1"
    elif errorCode == 401:
        return "登录失败，原因：token错误或过期\n请尝试重新用密码登录，如果使用密码登录出现此问题，请联系制作者\n错误代码：401    错误阶段：1.2"
    else:
        return "登录失败，原因：我也不知道\n请将下方错误代码和阶段告知制作者以帮助优化\n错误代码"+errorCode+"    错误阶段：1"


def delDisabled(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".disabled"):
                file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file[:-9])
                if os.path.exists(new_file_path):
                    os.remove(file_path)
                else:
                    os.rename(file_path, new_file_path)


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="简易接档器", size=(500, 300),
                         style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.SetSizeHints(500, 300, 500, 300)
        self.SetMaxSize((500, 300))
        icon = wx.Icon(get_resource_path('fengmian.ico'),
                       wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        self.accountText = wx.TextCtrl(self.panel)
        self.accountText.SetSize((200, -1))
        self.accountText.SetPosition((50, 10))
        self.accountText.SetHint("账号，留空为token登录")
        self.passwdText = wx.TextCtrl(
            self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.passwdText.SetSize((200, -1))
        self.passwdText.SetPosition((50, 40))
        self.passwdText.SetHint("密码或token")
        self.passwdText.Bind(wx.EVT_TEXT_ENTER, self.onLoadButtonClicked)
        loadButton = wx.Button(self.panel, label="安装")
        loadButton.SetPosition((60, 70))
        loadButton.Bind(wx.EVT_BUTTON, self.onLoadButtonClicked)
        unloadButton = wx.Button(self.panel, label="卸载")
        unloadButton.SetPosition((150, 70))
        unloadButton.Bind(wx.EVT_BUTTON, self.onUnloadButtonClicked)
        cleanButton = wx.Button(self.panel, label='清理')
        cleanButton.SetPosition((240, 70))
        cleanButton.Bind(wx.EVT_BUTTON, self.onCleanButtonClicked)
        authorText = wx.StaticText(self.panel, label="作者：wenwen12\n我是神里绫华的狗")
        authorText.SetForegroundColour(wx.Colour(102, 209, 255))
        authorText.SetPosition((380, 220))

    def onLoadButtonClicked(self, event):
        if self.accountText.GetValue():
            token = logIn(self.accountText.GetValue(),
                          self.passwdText.GetValue())
            if type(token) == int:
                wx.MessageBox(loginErrorCompose(token),
                              "发生错误", wx.OK | wx.ICON_ERROR)
        else:
            token = self.passwdText.GetValue()
        if type(token) == str:
            activity = getActivity(token)
            if not activity:
                wx.MessageBox("登录成功，但现在暂时没有活动，请等等再来吧",
                              "暂时没有活动", wx.OK | wx.ICON_INFORMATION)
            elif type(activity) == int:
                wx.MessageBox(loginErrorCompose(activity),
                              "发生错误", wx.OK | wx.ICON_ERROR)
            else:
                dlg = wx.MessageDialog(
                    None,
                    activitySign(activity),
                    "检测到活动",
                    wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE
                )
                result = dlg.ShowModal()
                dlg.Destroy()

                if result == wx.ID_YES:
                    processBar = wx.Gauge(self.panel)
                    processBar.SetPosition((50, 100))
                    processContent = wx.StaticText(self.panel)
                    processContent.SetPosition((50, 120))
                    processContent.SetLabel("正在下载存档文件")
                    url = activity['profileFile']
                    File = download(url)
                    processBar.SetValue(25)
                    processContent.SetLabel("正在解压")
                    with ZipFile('File', 'r') as zip_ref:
                        zip_ref.extractall(DOCUMENTS_DIR)
                    processBar.SetValue(50)
                    processContent.SetLabel("正在隐藏dlc")
                    sig = {'savingPosition': File.rstrip(".zip")}
                    changedDLC = []
                    for dlc in activity["unloadDlcList"]:
                        os.rename(GAME_DIR+dlc, GAME_DIR+dlc+'.disabled')
                        changedDLC.append(GAME_DIR+dlc+'.disabled')
                    sig.update(changedDLC=changedDLC)
                    with open(GAME_DIR+'changed.json', 'w') as cre:
                        json.dump(sig, cre)
                    processBar.SetValue(100)
                    processContent.SetLabel("安装完成")
                else:
                    pass

    def onUnloadButtonClicked(self, event):
        if os.path.exists(GAME_DIR+'changed.json'):
            with open(GAME_DIR+'changed.json') as sigFile:
                sig = json.load(sigFile)
            rmtree(sig['savingPosition'])
            for DLC in sig['unloadDlcList']:
                os.rename(DLC, DLC.rstrip('.disabled'))
            os.remove(GAME_DIR+'changed.json')
            wx.MessageBox("已完成卸载",
                          "卸载成功", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("发生错误，未找到卸载指示文件\n可能是因为你没有安装就卸载\n请检查游戏目录下是否存在changed.json\n若实在无法解决，请删除游戏文件夹中所有.disabled的文件，并检查完整性",
                          "未找到文件", wx.OK | wx.ICON_ERROR)
            webbrowser.open('https://www.bilibili.com')

    def onCleanButtonClicked(self, event):
        dlg = wx.MessageDialog(
            None,
            "执行清理操作后，将删除本程序对游戏的全部更改\n请注意，在清理完成后，您可能需要检查完整性才能继续使用",
            "清理提示",
            wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            dlg = wx.MessageDialog(None, "这是最后一次提示，您确定要清理吗?", "清理提示",
                                   wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE
                                   )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                delDisabled(GAME_DIR)
            wx.MessageBox("清理完成",
                          "清理完成", wx.OK | wx.ICON_INFORMATION)


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
