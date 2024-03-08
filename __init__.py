from nonebot import on_command, matcher
from nonebot.adapters.satori import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from .funct import *


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


tmp_id = on_command("查询", priority=5, block=True)
tmp_sever = on_command("服务器", priority=5, block=True)
tmp_road = on_command("路况", priority=5, block=True)
tmp_bind = on_command("绑定", priority=5, block=True)

lot_of_parrel = "=" * 19


@tmp_id.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    if not str(id):
        id = find_tmp_id(event.get_user_id())
        if id == -1:
            await tmp_id.finish(
                '您还没有绑定您的id，请使用"/绑定+id"来绑定', at_sender=True
            )
        else:
            if not (str(id).isdigit()):
                await tmp_id.finish(
                    "数据库错误，请尝试重新绑定。若仍然无效，清联系管理"
                )
            url = "https://api.truckersmp.com/v2/player/" + str(id)
            response = get(url)
            if response.status_code == 404 or response.json()["error"]:
                await tmp_id.finish("查询失败，查询目标不存在")
            await tmp_id.finish(succesfullySearchReturn(response))
    if not (str(id).isdigit()):
        await tmp_id.finish("id输入错误！")
    url = "https://api.truckersmp.com/v2/player/" + str(id)
    response = get(url)
    if response.status_code == 404 or response.json()["error"]:
        await tmp_id.finish("查询失败，查询目标不存在")
    await tmp_id.finish(succesfullySearchReturn(response))


@tmp_bind.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    tmpId = args.extract_plain_text()
    if not (str(tmpId).isdigit()):
        await tmp_bind.finish("绑定失败，输入的不是tmpId")
    if insert_or_replace_qq_id_tmp_id(event.get_user_id(), int(tmpId)):
        await tmp_bind.finish("绑定成功", at_sender=True)
    await tmp_bind.finish("绑定失败，数据库错误")


@tmp_road.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    if re.match("s1(服)?", str(id), re.I):
        response = get("https://traffic.krashnz.com/ets2/sim1")
        response = response.text
        ans = [
            "地区:加来-杜伊斯堡道路\n",
            search_city(response, 134),
            "\n",
            lot_of_parrel,
            "\n地区:加来\n",
            search_city(response, 55),
            "\n",
            lot_of_parrel,
            "\n地区:杜伊斯堡\n",
            search_city(response, 14),
            "\n",
            lot_of_parrel,
            "\n地区:杜塞尔多夫\n",
            search_city(response, 15),
        ]
        await tmp_road.finish("".join(ans))
    if re.match("p(服)?", str(id), re.I):
        response = get("https://traffic.krashnz.com/promods/pm")
        response = response.text
        ans = [
            "地区:希尔科内斯城市\n",
            search_city(response, 615),
            "\n",
            lot_of_parrel,
            "\n地区:希尔科内斯-采石场\n",
            search_city(response, 793),
        ]
        await tmp_road.finish("".join(ans))
    tmp_road.finish("输入无效")


@tmp_sever.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    response = get("https://api.truckersmp.com/v2/servers")
    detail = [[], [], [], []]
    server_status = [[], [], [], []]
    server_max_player = [0, 0, 0, 0]
    server_player = [0, 0, 0, 0]
    total = 0
    for server in response.json()["response"]:
        if server["id"] == 4:
            server_player[0] = server["players"]
            server_max_player[0] = server["maxplayers"]
            server_status[0] = 1
        if server["id"] == 41:
            server_player[1] = server["players"]
            server_max_player[1] = server["maxplayers"]
            server_status[1] = 1
        if server["id"] == 8:
            server_player[2] = server["players"]
            server_max_player[2] = server["maxplayers"]
            server_status[2] = 1
        if server["id"] == 31:
            server_player[3] = server["players"]
            server_max_player[3] = server["maxplayers"]
            server_status[3] = 1
        total += server["players"]
    ans = "在线玩家:" + str(total) + "\n"
    servers = ["Simulation1", "Simulation2", "Arcade", "Promods"]
    for i in range(4):
        ans += (
            lot_of_parrel
            + "\n地区:"
            + servers[i]
            + "\n状态:"
            + to_string_if_on(server_status[i])
            + "\n人数:"
            + str(server_player[i])
            + "/"
            + str(server_max_player[i])
            + "\n"
        )
    await tmp_sever.finish(ans)
