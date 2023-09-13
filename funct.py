from httpx import get
import re
from bs4 import BeautifulSoup
import psycopg2

databaseInfo = ("uname", "zhenxun")


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


def if_ban(a: bool, b: str):
    if a:
        return "是\n解禁时间:" + b
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
    conn = psycopg2.connect(
        database="",
        user="",
        password="",
    )
    cursor = conn.cursor()
    try:
        conn.autocommit = False
        sql = "INSERT INTO tmp_info (qq_id, tmp_id) VALUES (%s, %s) ON CONFLICT (qq_id) DO UPDATE SET tmp_id = EXCLUDED.tmp_id;"
        cursor.execute(sql, (qq_id, tmp_id))
        conn.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def find_tmp_id(qq_id):
    conn = psycopg2.connect(
        database="",
        user="",
        password="",
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT tmp_id FROM tmp_info WHERE qq_id = %s", (qq_id,))
        result = cur.fetchone()
        if result is not None:
            tmp_id = result[0]
        else:
            tmp_id = -1
        cur.close()
        return tmp_id
    finally:
        conn.close()


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
        if_ban(
            response.json()["response"]["banned"],
            response.json()["response"]["bannedUntil"],
        ),
        "\n年内封禁:",
        str(response.json()["response"]["bansCount"]),
        "\n所属车队:",
        null_check(response.json()["response"]["vtc"]["name"]),
        ]
    """, '\nTMP链接:https://truckersmp.com/user/', str(id), '\nSteam链接:https://steamcommunity.com/profiles/', response.json()['response']['steamID']""",
    return "".join(ans)
