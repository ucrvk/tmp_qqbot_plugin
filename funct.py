from httpx import get
import re
from bs4 import BeautifulSoup
from json import load, dump

tmpid_table: dict = {}
with open("tmpid_table.json", "r") as fi:
    tmpid_table = load(fi)


def search_city(html, id):
    exp = BeautifulSoup(html, "html.parser")
    cars = exp.find("span", id="traffic_players_" + str(id)).contents
    status = exp.find("span", id="traffic_status_" + str(id)).contents
    if status == ["Moderate"]:
        status = "正常"
    elif status == ["Low"] or status == ["Empty"]:
        status = "通畅"
    elif status == ["Congested"]:
        status = "爆满"
    elif status == ["Heavy"]:
        status = "拥堵"
    return " ".join(["路况:", status, "| 玩家:"] + cars)


def if_ban(a: bool):
    if a:
        return "是\n"
    return "否"


def null_check(str: str):
    if str:
        return str
    return "无"


def Detail(server, check_id, detail, output_id):
    if server["id"] == check_id:
        detail[output_id] = [server["players"], server["queue"], server["maxplayers"]]


def to_string_if_on(a: bool):
    if a:
        return "在线"
    return "离线"


def insert_or_replace_qq_id_tmp_id(qq_id, tmp_id):
    tmpid_table[str(qq_id)] = tmp_id
    with open("tmpid_table.json","w") as fi:
        dump(tmpid_table)


def find_tmp_id(qq_id):
    return tmpid_table.get(str(qq_id),-1)


def succesfullySearchReturn(response):
    ans = [
        "查询完成\nTMPID:",
        str(response.json()["response"]["id"]),
        "\n玩家名称:",
        response.json()["response"]["name"],
        "\n玩家类别:",
        response.json()["response"]["groupName"],
        "\n注册时间:",
        response.json()["response"]["joinDate"],
        "\n是否封禁:",
        if_ban(response.json()["response"]["banned"]),
        "\n年内封禁:",
        str(response.json()["response"]["bansCount"]),
        "\n所属车队:",
        null_check(response.json()["response"]["vtc"]["name"]),
    ]
    """, '\nTMP链接:https://truckersmp.com/user/', str(id), '\nSteam链接:https://steamcommunity.com/profiles/', response.json()['response']['steamID']""",
    return "".join(ans)
