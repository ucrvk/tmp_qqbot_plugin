from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent,GroupMessageEvent, Message
from nonebot.params import RegexGroup,CommandArg
from requests import get
import json
import re

__zx_plugin_name__ = "tmp查询"
__plugin_usage__ = """
usage：
    p
    指令：
        tmp查询[id]
""".strip()
__plugin_des__ = "l"
__plugin_cmd__ = ["[城市]天气/天气[城市]"]
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.1
__plugin_author__ = "wenwen12305"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["tmp查询"],
}


tmp = on_command("tmp查询", priority=5, block=True)

def search_city(string,city,start_sign,end_sign):
    rec=str(start_sign)+'(.|\n)+'+str(end_sign)
    string=re.search(rec,string).group()
    city=city+r'.+</span> \(\d+\)'
    string=re.search(city,string).group()
    cars=re.search(r'\(\d+\)',string).group()
    cars=cars.replace('(','')
    cars=cars.replace(')','')
    if re.search('Moderate',string):
        status='中等'
    elif re.search('Low',string):
        status='畅通'
    elif re.search('Congested',string):
        status='不怕封你就去'
    elif re.search('Heavy',string):
        status='拥堵'
    return str(cars)+' '+status

def if_ban(a:bool,b:str):
        if a:
            return ("是\n解禁时间:"+b)
        return "否"

def null_check(str:str):
    if str:
        return str
    return "无"

def Detail(server,check_id,detail,output_id):
    if server['id']==check_id:
        detail[output_id]=[server['players'],server['queue'],server['maxplayers']]


@tmp.handle()
async def handle_function(event: MessageEvent,args: Message = CommandArg()):
    id=args.extract_plain_text()
    if not(id):
        response=get('https://api.truckersmp.com/v2/servers')
        detail=[[0]]
        for server in response.json()['response']:
            if server['id']==4:
                detail_s1=[server['players'],server['queue'],server['maxplayers']]
            if server['id']==41:
                detail_s2=[server['players'],server['queue'],server['maxplayers']]
            if server['id']==8:
                detail_a=[server['players'],server['queue'],server['maxplayers']]
            if server['id']==31:
                detail_p=[server['players'],server['queue'],server['maxplayers']]
        ans=["服务器当前状况:\nS1服:",detail_s1[0],'+',detail_s1[1],'/',detail_s1[2],'\nS2服:',detail_s2[0],'+',detail_s2[1],'/',detail_s2[2],'\nA服:',detail_a[0],'+',detail_a[1],'/',detail_a[2],'\nP服:',detail_p[0],'+',detail_p[1],'/',detail_p[2]]
        ans=[str(i) for i in ans]
        await tmp.finish(''.join(ans))
    if re.match('s1(服)?',str(id),re.I):
        response=get('https://traffic.krashnz.com/')
        response=response.text
        ans=['查询完成:\n加来小道:',search_city(response,r'Calais - Duisburg \(Road\)','Simulation 1','View traffic for Simulation 1'),'\n加来城区:',search_city(response,r'Calais \(City\)','Simulation 1','View traffic for Simulation 1'),'\n杜伊斯堡',search_city(response,r'Duisburg \(City\)','Simulation 1','View traffic for Simulation 1')]
        await tmp.finish(''.join(ans))
        
    if re.match('p(服)?',str(id),re.I):
        response=get('https://traffic.krashnz.com/')
        response=response.text
        ans=['查询完成:\n矿山:',search_city(response,r'Kirkenes Quarry \(Road\)','ProMods','View traffic for ProMods')]
        await tmp.finish(''.join(ans))
    if not(str(id).isdigit()):
        await tmp.finish("id输入错误！")
    url="https://api.truckersmp.com/v2/player/"+str(id)
    response=get(url)
    if response.status_code==404 or response.json()['error']:
        await tmp.finish("查询失败，请联系管理员")
    ans=["查询完成\nTMPid:",str(response.json()['response']['id']),"\n名称:",response.json()['response']['name'],"\n所属车队:",null_check(response.json()['response']['vtc']['name']),"\nSteamid:",str(response.json()['response']['steamID']),"\n加入日期",response.json()['response']['joinDate'],"\n是否封禁:",if_ban(response.json()['response']['banned'],response.json()['response']['bannedUntil'])]
    await tmp.finish(''.join(ans))
        
