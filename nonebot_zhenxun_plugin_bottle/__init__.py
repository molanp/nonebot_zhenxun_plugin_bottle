from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message)
from configs.config import NICKNAME
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import CommandArg
from models.group_member_info import GroupInfoUser
from ._model import Sea
import html as ht


__zx_plugin_name__ = "漂流瓶"
__plugin_usage__ = """
usage：
    群与群互通的漂流瓶插件
指令：
    扔漂流瓶(throw) [文本/图片]
    捡漂流瓶(pick/寄漂流瓶/捡漂流瓶)
""".strip()
__plugin_superuser_usage__ = """
SUPERUSER指令：
    清空漂流瓶
    删除漂流瓶 [漂流瓶编号]
    查看漂流瓶 [漂流瓶编号]
    添加漂流瓶黑名单 [user / group] [QQ号 / 群号]
    移出漂流瓶黑名单 [user / group] [QQ号 / 群号]
    查看漂流瓶黑名单
""".strip()
__plugin_des__ = '漂流瓶插件'
__plugin_type__ = ("群内小游戏",)
__plugin_cmd__ = ["pick", "throw", "查看漂流瓶", "扔漂流瓶",
                 "捡漂流瓶", "寄漂流瓶", "丢漂流瓶", "漂流瓶列表", "删除漂流瓶", "清空漂流瓶",
                 "添加漂流瓶黑名单", "移出漂流瓶黑名单", "漂流瓶黑名单",
                 "清空漂流瓶黑名单", "banbottle", "漂流瓶封禁"]
__plugin_version__ = 0.3
__plugin_author__ = "molanp"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": __plugin_cmd__,
}

__plugin_cd_limit__ = {
    "cd": 5,
    "check_type": "all",
    "limit_type": "user",
    "rst": "正在冷却喵~",
    "status": True
}

throw = on_command("扔漂流瓶", aliases={
                   "寄漂流瓶", "丢漂流瓶", "throw"}, permission=GROUP, priority=5, block=True)
pick = on_command("捡漂流瓶", aliases={"pick"},
                  permission=GROUP, priority=5, block=True)
check_bottle = on_command(
    "查看漂流瓶", permission=SUPERUSER, priority=5, block=True)
remove = on_command("删除漂流瓶", permission=SUPERUSER, priority=5, block=True)

clear = on_command("清空漂流瓶", permission=SUPERUSER, priority=5, block=True)
ban = on_command(
    "添加漂流瓶黑名单",
    aliases={"banbottle", "漂流瓶封禁"},
    permission=SUPERUSER,
    priority=5,
    block=True,
)
clear_ban = on_command("清空漂流瓶黑名单", permission=SUPERUSER,
                       priority=5, block=True)
check_ban = on_command("漂流瓶黑名单", permission=SUPERUSER,
                       priority=5, block=True)
remove_ban = on_command(
    "移出漂流瓶黑名单", permission=SUPERUSER, priority=5, block=True)


@throw.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = ht.unescape(str(args))
    name = await get_name(event.user_id, event.group_id)
    await throw.finish(Message(Sea(event).throw(msg, name)), at_sender=True)


async def get_name(user_id: str, group_id: str) -> str:
    if user := await GroupInfoUser.get_or_none(user_id=user_id, group_id=group_id):
        return user.user_name
    else:
        return "该群员不在列表中，请更新群成员信息"


@pick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    bottle = Sea(event).pick()
    if bottle:
        try:
            id_str = bottle.id
            qq_str = bottle.user
            grp_str = bottle.grp
        except BaseException:
            await pick.finish(Message(bottle), at_sender=True)
        msg_list = []
        msg = f"{NICKNAME}试着帮你捞出来了这个~\nID: {id_str}\n投递人: {bottle.name}({qq_str})\n群号: {grp_str}\n时间: {bottle.time}\n内容: \n{bottle.msg}"
        msg_list.append({
            "type": "node",
            "data": {
                "name": f"{NICKNAME}",
                "uin": f"{bot.self_id}",
                "content": msg,
            },
        })
        if isinstance(event, GroupMessageEvent):
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
        else:
            for msg in msg_list:
                await bot.send_private_msg(user_id=event.user_id, message=msg)
    else:
        await pick.finish(Message("没有漂流瓶喵~"), at_sender=True)


@check_bottle.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    bottle = Sea(event).pick(id)
    if bottle:
        try:
            id_str = bottle.id
            qq_str = bottle.user
            grp_str = bottle.grp
        except BaseException:
            await pick.finish(Message(bottle), at_sender=True)
        msg_list = []
        msg = f"{NICKNAME}试着帮你捞出来了这个~\nID: {id_str}\n投递人: {bottle.name}({qq_str})\n群号: {grp_str}\n时间: {bottle.time}\n内容: \n{bottle.msg}"
        msg_list.append({
            "type": "node",
            "data": {
                "name": f"{NICKNAME}",
                "uin": f"{bot.self_id}",
                "content": msg,
            },
        })
        if isinstance(event, GroupMessageEvent):
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
        else:
            for msg in msg_list:
                await bot.send_private_msg(user_id=event.user_id, message=msg)
    else:
        await check_bottle.finish("漂流瓶不存在", at_sender=True)


@remove.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    if not id:
        await remove.finish("请输入要删除的漂流瓶id")
    else:
        await remove.finish(Message(Sea(event).remove(id)), at_sender=True)


@clear.handle()
async def _(event: GroupMessageEvent):
    await clear.finish(Message(Sea(event).clear()), at_sender=True)


@ban.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if not msg or len(msg.split()) != 2 or not str(msg).isdigit():
        await ban.finish("请输入要拉黑的类型和QQ/群号", at_sender=True)
    else:
        await ban.finish(Message(Sea(event).ban(msg)), at_sender=True)


@clear_ban.handle()
async def _(event: GroupMessageEvent):
    await clear_ban.finish(Message(Sea(event).clear_ban()), at_sender=True)


@check_ban.handle()
async def _(event: GroupMessageEvent):
    await check_ban.finish(Message(Sea(event).ban_list()), at_sender=True)


@remove_ban.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    await remove_ban.finish(Message(Sea(event).remove_ban(msg)), at_sender=True)
