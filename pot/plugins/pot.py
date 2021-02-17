import nonebot
# from nonebot import on_command, CommandSession, get_bot
# import pytz
# from aiocqhttp.exceptions import Error as CQHttpError
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.permission import Permission
from nonebot import require

scheduler = require("plugin-apscheduler-master.nonebot_plugin_apscheduler").scheduler
from datetime import datetime
import os
import pickle
import pytz

#--------------------------
# Author: Zachary Chen
#--------------------------

print('-----------')

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

class one_pot:
    def __init__(self, who, where, when, what):
        self.where = where
        self.who = [who]
        self.when = when
        self.what = what
        self.driver_idx = -1
        self.noodle = []
        self.rice = []
        self.comment = ''

def print_all_pot():
    with open('cur_pots_dump', 'wb') as f:
        pickle.dump(cur_pots, f)
    pot_str = "现在约了的锅有："
    if len(cur_pots) == 0:
        return pot_str + "[无]"
    for i,pot in enumerate(cur_pots):
        pot_str += ("\n\n编号:" + str(i) + " 地点:" + pot.where + " 时间:" + pot.when + " 口味:" + pot.what + " 面数:" + str(sum(pot.noodle)) + " 饭数:" + str(sum(pot.rice)) + '\n乘客:')
        for j,who in enumerate(pot.who):
            pot_str += '\n' + str(j) + '.' + who
            if j == pot.driver_idx:
                pot_str += "(司机,"+str(pot.noodle[j])+'面 '+str(pot.rice[j])+'饭)'
            else:
                pot_str += "("+str(pot.noodle[j])+'面 '+str(pot.rice[j])+'饭)'
            pot_str += " "
        if pot.comment != '':
            pot_str += ("\n备注:"+pot.comment)
    return pot_str

cur_pots = []
if os.path.exists('cur_pots_dump'):
    with open('cur_pots_dump', 'rb') as f:
        cur_pots = pickle.load(f)

### 约锅 ###
newpot = on_command("约锅", permission=Permission(), priority=5)
@newpot.handle()
# @on_command('newpot', aliases=('约锅'), only_to_me=False)
async def handle_first_receive_newpot(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['who', 'where', 'when', 'what', 'noodle', 'rice']
    for a,b in zip(args, keys):
        state[b] = a
    
@newpot.got("who", prompt="你的id是？")
async def newpot_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')

@newpot.got("where", prompt="约哪儿的锅？")
async def newpot_got_where(bot: Bot, event: Event, state: T_State):
    if state['where'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')

@newpot.got("when", prompt="什么时候？")
async def newpot_got_when(bot: Bot, event: Event, state: T_State):
    if state['when'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')

@newpot.got("what", prompt="什么口味？")
async def newpot_got_what(bot: Bot, event: Event, state: T_State):
    if state['what'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    state['pot'] = one_pot(state['who'], state['where'], state['when'], state['what'])

@newpot.got("noodle", prompt="您几面？")
async def newpot_got_noodle(bot: Bot, event: Event, state: T_State):
    noodle = state["noodle"]
    if noodle == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if not noodle.isdigit() or int(noodle) < 0:
        await newpot.reject("？这边建议再输一遍面数呢（")
    state['pot'].noodle.append(int(state['noodle']))

@newpot.got("rice", prompt="您几饭？")
async def newpot_got_rice(bot: Bot, event: Event, state: T_State):
    rice = state["rice"]
    if rice == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if not rice.isdigit() or int(rice) < 0:
        await newpot.reject("？这边建议再输一遍饭数呢（")
    state['pot'].rice.append(int(state['rice']))
    cur_pots.append(state['pot'])
    report = print_all_pot()
    await newpot.finish('约锅成功！\n' + report)

### 删锅 ###
# @on_command('delpot', aliases=('锅没了', '锅完了'), only_to_me=False)
delpot = on_command("锅没了", permission=Permission(), priority=5)
@delpot.handle()
async def handle_first_receive_delpot(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state['pot_id'] = args

@delpot.got("pot_id", prompt="扬哪个锅？来个编号")
async def delpot_gotid(bot: Bot, event: Event, state: T_State):
    pot_id = state["pot_id"]
    if state['pot_id'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if not pot_id.isdigit():
        await delpot.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id >= 0 and pot_id < len(cur_pots):
            cur_pots.pop(pot_id)
            report = print_all_pot()
            await delpot.finish('锅没力（悲\n' + report)
        else:
            await delpot.reject("你不能扬一个不存在的锅，重新选一个吧.jpg")

### 上车 ###
# @on_command('join', aliases=('上车', '加入'), only_to_me=False)
join = on_command("上车", permission=Permission(), priority=5)
@join.handle()
async def handle_first_receive_join(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['who', 'which', 'noodle', 'rice']
    for a,b in zip(args, keys):
        state[b] = a

@join.got("who", prompt="你的id是？")
async def join_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if 'which' not in state.keys():
        report = print_all_pot()
        await join.send(report)

@join.got("which", prompt="锅编号？")
async def join_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await join.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await join.reject("你不能加入一个不存在的锅，重新选一个吧.jpg")

@join.got("noodle", prompt="您几面？")
async def join_get_noodle(bot: Bot, event: Event, state: T_State):
    if state['noodle'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    noodle = state["noodle"]
    if not noodle.isdigit() or int(noodle) < 0:
        await newpot.reject("？这边建议再输一遍面数呢（")

@join.got("rice", prompt="您几饭？")
async def join_get_rice(bot: Bot, event: Event, state: T_State):
    rice = state["rice"]
    if state['rice'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if not rice.isdigit() or int(rice) < 0:
        await newpot.reject("？这边建议再输一遍饭数呢（")
    who = state["who"]
    which = int(state["which"])
    noodle = int(state['noodle'])
    rice = int(state['rice'])
    cur_pots[which].who.append(who)
    cur_pots[which].noodle.append(noodle)
    cur_pots[which].rice.append(rice)
    report = print_all_pot()
    await join.finish('上车成功！\n' + report)

### 下车 ###
# @on_command('leave', aliases=('下车', '咕了', '鸽了'), only_to_me=False)
leave = on_command("咕了", permission=Permission(), priority=5)
@leave.handle()
async def handle_first_receive_leave(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'who']
    for a,b in zip(args, keys):
        state[b] = a

@leave.got("which", prompt="锅编号？")
async def leave_got_which(bot: Bot, event: Event, state: T_State):
    pot_id = state["which"]
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    if not pot_id.isdigit():
        await leave.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await leave.reject("你不能下一个还没上的车，重新选一个吧.jpg")

@leave.got("who", prompt="您的id/编号？")
async def leave_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    who = state["who"]
    which = int(state['which'])
    if who.isdigit():
        idx = int(who)
        if idx < 0 or idx >= len(cur_pots[which].who):
            await leave.reject("这个锅有这么多人吗？")
    else:
        if who not in cur_pots[which].who:
            await leave.reject("好像没有这个人嗷，请重新输入id")
        else:
            idx = cur_pots[which].who.index(who)
    cur_pots[which].who.pop(idx)
    cur_pots[which].noodle.pop(idx)
    cur_pots[which].rice.pop(idx)
    if cur_pots[which].driver_idx == idx:
        cur_pots[which].driver_idx = -1
    elif cur_pots[which].driver_idx > idx:
        cur_pots[which].driver_idx -= 1
    report = print_all_pot()
    await leave.finish('下车成功！\n' + report)

### 换司机 ###
# @on_command('driver', aliases=('司机', '有人点锅了'), only_to_me=False)
driver = on_command("有人点锅了", permission=Permission(), priority=5)
@driver.handle()
async def handle_first_receive_driver(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'who']
    for a,b in zip(args, keys):
        state[b] = a

@driver.got("which", prompt="锅编号？")
async def driver_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await driver.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await driver.reject("你不能下一个还没上的车，重新选一个吧.jpg")

@driver.got("who", prompt="司机的id/编号？")
async def driver_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    who = state["who"]
    which = int(state['which'])
    if who.isdigit() or (who[0]=='-' and who[1:].isdigit()):
        idx = int(who)
        if idx < -1 or idx >= len(cur_pots[which].who):
            await driver.reject("这个锅有这么多人吗？")
    else:
        if who not in cur_pots[which].who:
            await driver.reject("好像没有这个人嗷，请重新输入id")
        else:
            idx = cur_pots[which].who.index(who)
    cur_pots[which].driver_idx = idx
    report = print_all_pot()
    await driver.finish('好耶！\n' + report)

### 改锅 ###
# @on_command('change', aliases=('改锅'), only_to_me=False)
change = on_command("改锅", permission=Permission(), priority=5)
@change.handle()
async def handle_first_receive_change(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'feature', 'what']
    for a,b in zip(args, keys):
        state[b] = a

@change.got("which", prompt="锅编号？")
async def change_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await change.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await change.reject("重新选一个锅吧.jpg")

@change.got("feature", prompt="改锅的哪个属性？在【时间】【地点】【口味】【备注】中选一个吧")
async def change_got_feature(bot: Bot, event: Event, state: T_State):
    if state['feature'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    features = ['时间', '地点', '口味', '备注']
    feature = state['feature']
    if feature not in features:
        await change.reject('真的有这个属性吗？在【时间】【地点】【口味】【备注】中选一个吧')

@change.got("what", prompt="改成啥？")
async def change_got_what(bot: Bot, event: Event, state: T_State):
    if state['what'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = int(state["which"])
    feature = state['feature']
    what = state["what"]
    if feature == '时间':
        cur_pots[pot_id].when = what
    elif feature == '地点':
        cur_pots[pot_id].where = what
    elif feature == '口味':
        cur_pots[pot_id].what = what
    elif feature == '备注':
        cur_pots[pot_id].comment = what
    report = print_all_pot()
    await change.finish('操作成功！\n' + report)

### 改面 ###
# @on_command('changemian', aliases=('改面'), only_to_me=False)
changemian = on_command("改面", permission=Permission(), priority=5)
@changemian.handle()
async def handle_first_receive_changemian(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'who', 'howmany']
    for a,b in zip(args, keys):
        state[b] = a

@changemian.got("which", prompt="锅编号？")
async def changemian_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await changemian.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await changemian.reject("重新选一个锅吧.jpg")

@changemian.got("who", prompt="改谁的面？输入id/编号")
async def changemian_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    who = state["who"]
    which = int(state['which'])
    if who.isdigit():
        idx = int(who)
        if idx < 0 or idx >= len(cur_pots[which].who):
            await changemian.reject("这个锅有这么多人吗？")
        state["who"] = cur_pots[which].who[idx]
    else:
        if who not in cur_pots[which].who:
            await changemian.reject("好像没有这个人嗷，请重新输入id")

@changemian.got("howmany", prompt="改多少？")
async def changemian_got_howmany(bot: Bot, event: Event, state: T_State):
    if state['howmany'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    howmany = state["howmany"]
    which = int(state['which'])
    who = state['who']
    if not howmany.isdigit() or int(howmany) < 0:
        await changemian.reject("？这边建议再输一遍面的数量呢（")
    idx = cur_pots[which].who.index(who)
    cur_pots[which].noodle[idx] = int(howmany)
    report = print_all_pot()
    await changemian.finish('操作成功！\n' + report)

### 改饭 ###
# @on_command('changefan', aliases=('改饭'), only_to_me=False)
changefan = on_command("改饭", permission=Permission(), priority=5)
@changefan.handle()
async def handle_first_receive_changefan(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'who', 'howmany']
    for a,b in zip(args, keys):
        state[b] = a

@changefan.got("which", prompt="锅编号？")
async def changefan_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await changefan.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await changefan.reject("重新选一个锅吧.jpg")

@changefan.got("who", prompt="改谁的饭？输入id/编号")
async def changefan_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    who = state["who"]
    which = int(state['which'])
    if who.isdigit():
        idx = int(who)
        if idx < 0 or idx >= len(cur_pots[which].who):
            await changefan.reject("这个锅有这么多人吗？")
        state["who"] = cur_pots[which].who[idx]
    else:
        if who not in cur_pots[which].who:
            await changefan.reject("好像没有这个人嗷，请重新输入id")

@changefan.got("howmany", prompt="改多少？")
async def changefan_got_howmany(bot: Bot, event: Event, state: T_State):
    if state['howmany'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    howmany = state["howmany"]
    which = int(state['which'])
    who = state['who']
    if not howmany.isdigit() or int(howmany) < 0:
        await changefan.reject("？这边建议再输一遍饭的数量呢（")
    idx = cur_pots[which].who.index(who)
    cur_pots[which].rice[idx] = int(howmany)
    report = print_all_pot()
    await changefan.finish('操作成功！\n' + report)

### 加备注 ###
# @on_command('comment', aliases=('备注', '加菜', '需求'), only_to_me=False)
comment = on_command("加需求", permission=Permission(), priority=5)
@comment.handle()
async def handle_first_receive_comment(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'what']
    for a,b in zip(args, keys):
        state[b] = a

@comment.got("which", prompt="锅编号？")
async def comment_got_which(bot: Bot, event: Event, state: T_State):
    if state['which'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    pot_id = state["which"]
    if not pot_id.isdigit():
        await comment.reject("？这边建议再输一遍锅编号呢（")
    else:
        pot_id = int(pot_id)
        if pot_id < 0 or pot_id >= len(cur_pots):
            await comment.reject("重新选一个锅吧.jpg")

@comment.got("what", prompt="加什么需求？")
async def comment_got_who(bot: Bot, event: Event, state: T_State):
    if state['what'] == 'QUIT':
        await newpot.finish('溜了溜了.jpg')
    what = state["what"]
    which = int(state['which'])
    cur_pots[which].comment = cur_pots[which].comment+' '+what
    report = print_all_pot()
    await comment.finish('操作成功！\n' + report)

### 输出 ###
# @on_command('pots', aliases=('有锅吗'), only_to_me=False)
pots = on_command("有锅吗", permission=Permission(), priority=3)
@pots.handle()
async def handle_first_receive_pots(bot: Bot, event: Event, state: T_State):
    report = print_all_pot()
    await pots.finish(report)

### 清空锅 ###
# @on_command('potclear', aliases=('清空锅'), only_to_me=False)
potclear = on_command("清空锅", permission=Permission(), priority=7)
@potclear.handle()
async def handle_first_receive_potclear(bot: Bot, event: Event, state: T_State):
    cur_pots.clear()
    report = print_all_pot()
    await potclear.finish(report)

### 帮助 ###
# @on_command('pothelp', aliases=('怎么锅啊', '约锅助手', '约锅帮助', '约锅help'), only_to_me=False)
pothelp = on_command("怎么锅啊", permission=Permission(), priority=1)
@pothelp.handle()
async def handle_first_receive_pothelp(bot: Bot, event: Event, state: T_State):
    helpstr = "约锅助手指令:\n /怎么锅啊 : 输出本帮助\n /有锅吗 : 查看已有的锅\n /约锅 <地点> <时间> <口味> <发起人id> <面数> <饭数> : 约一个新锅\n /上车 <乘客id> <锅编号> <面数> <饭数> : 加入指定锅\n /有人点锅了 <锅编号> <司机id/编号> : 给指定锅选择一个司机,-1代表没人点\n /改锅 <锅编号> <[时间|地点|口味|备注] 中的一个> <新的[时间|地点|口味|备注]> : 修改锅的属性\n /改面 <锅编号> <乘客编号/id> <面数> : 修改乘客的面数\n /改饭 <锅编号> <乘客编号/id> <饭数> : 修改乘客的饭数\n /加需求 <锅编号> <内容> : 附加新的备注\n /咕了 <锅编号> <乘客编号/id> : 放群友鸽子\n /锅没了 <锅编号> : 删除一个已有的锅\n /清空锅 : 删除所有的锅\nQUIT : 结束当前命令（不然会被追问）\n以上所有参数可以分多次输入"
    await pothelp.finish(helpstr)