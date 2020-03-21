from nonebot import on_command, CommandSession

#--------------------------
# Author: Zachary Chen
#--------------------------
class one_pot:
    def __init__(self, who, where, when, what):
        self.where = where
        self.who = [who]
        self.when = when
        self.what = what
        self.driver_idx = -1

cur_pots = []

### 约锅 ###
@on_command('newpot', aliases=('约锅'))
async def newpot(session: CommandSession):
    who = session.get('who')
    where = session.get('where')
    when = session.get('when')
    what = session.get('what')
    thepot = one_pot(who, where, when, what)
    cur_pots.append(thepot)
    report = await print_all_pot()
    await session.send('约锅成功！\n' + report)

@newpot.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        args = stripped_arg.split()
        print(len(args))
        if len(args) == 4:
            session.state['where'] = args[0]
            session.state['when'] = args[1]
            session.state['what'] = args[2]
            session.state['who'] = args[3]
            return

    session.pause('约锅输入格式错误！')

### 删锅 ###
@on_command('delpot', aliases=('锅没了', '锅完了'))
async def delpot(session: CommandSession):
    who = session.get('which')
    cur_pots.pop(who)
    report = await print_all_pot()
    await session.send('操作成功！\n' + report)

@delpot.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        if type(eval(stripped_arg)) == int:
            which = int(stripped_arg)
            if which >= 0 and which < len(cur_pots):
                session.state['which'] = which
                return

    session.pause('输入格式错误！')

### 上车 ###
@on_command('join', aliases=('上车', '加入'))
async def join(session: CommandSession):
    who = session.get('who')
    which = session.get('which')
    cur_pots[which].who.append(who)
    report = await print_all_pot()
    await session.send('上车成功！\n' + report)

@join.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        args = stripped_arg.split()
        if len(args) == 2 and type(eval(args[0])) == int:
            which = int(args[0])
            if which>=0 and which<len(cur_pots):
                session.state['who'] = args[1]
                session.state['which'] = which
                return

    session.pause('输入格式错误！')

### 下车 ###
@on_command('leave', aliases=('下车', '咕了', '鸽了'))
async def leave(session: CommandSession):
    idx = session.get('idx')
    which = session.get('which')
    cur_pots[which].who.pop(idx)
    if cur_pots[which].driver_idx == idx:
        cur_pots[which].driver_idx = -1
    elif cur_pots[which].driver_idx > idx:
        cur_pots[which].driver_idx -= 1
    report = await print_all_pot()
    await session.send('下车成功！\n' + report)

@leave.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        args = stripped_arg.split()
        if len(args) == 2 and type(eval(args[0])) == int and type(eval(args[1])) == int:
            which = int(args[0])
            idx = int(args[1])
            if which>=0 and which<len(cur_pots) and idx>=0 and idx<len(cur_pots[which].who):
                session.state['idx'] = idx
                session.state['which'] = which
                return

    session.pause('输入格式错误！')

### 换司机 ###
@on_command('driver', aliases=('司机', '有人点锅了'))
async def driver(session: CommandSession):
    idx = session.get('idx')
    which = session.get('which')
    cur_pots[which].driver_idx = idx
    report = await print_all_pot()
    await session.send('操作成功！\n' + report)

@driver.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        args = stripped_arg.split()
        if len(args) == 2 and type(eval(args[0])) == int and type(eval(args[1])) == int:
            which = int(args[0])
            idx = int(args[1])
            if which>=-1 and which<len(cur_pots) and idx>=0 and idx<len(cur_pots[which].who):
                session.state['idx'] = idx
                session.state['which'] = which
                return

    session.pause('输入格式错误！')

### 改锅 ###
@on_command('change', aliases=('改锅'))
async def change(session: CommandSession):
    feature = session.get('feature')
    which = session.get('which')
    what = session.get('what')
    if feature == '时间':
        cur_pots[which].when = what
    elif feature == '地点':
        cur_pots[which].where = what
    elif feature == '口味':
        cur_pots[which].what = what
    report = await print_all_pot()
    await session.send('操作成功！\n' + report)

@change.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        args = stripped_arg.split()
        features = ['时间', '地点', '口味']
        if len(args) == 3 and type(eval(args[0])) == int and (args[1] in features):
            which = int(args[0])
            if which>=0 and which<len(cur_pots):
                session.state['which'] = which
                session.state['feature'] = args[1]
                session.state['what'] = args[2]
                return

    session.pause('输入格式错误！')

### 输出 ###
@on_command('pots', aliases=('有锅吗'))
async def pots(session: CommandSession):
    report = await print_all_pot()
    await session.send(report)

### 帮助 ###
@on_command('pothelp', aliases=('怎么锅啊', '约锅助手', '约锅帮助', '约锅help'))
async def pothelp(session: CommandSession):
    helpstr = "约锅助手指令:\n <pothelp|怎么锅啊|约锅助手|约锅帮助|约锅help> :输出本帮助\n <pots|有锅吗> : 查看已有的锅\n <newpot|约锅> <地点> <时间> <口味> <发起人id> : 约一个新锅\n <join|上车|加入> <锅编号> <乘客id> :加入指定锅\n <driver|司机|有人点锅了> <锅编号> <乘客编号> :给指定锅选择一个司机,-1代表没人点\n <change|改锅> <时间|地点|口味 中的一个> <新的时间|地点|口味> :修改锅的属性\n <leave|下车|咕了|鸽了> <锅编号> <乘客编号> :放群友鸽子\n <delpot|锅没了|锅完了> <锅编号> :删除一个已有的锅\n\n PS.把要不要面要不要饭写在乘客id里罢(恼"
    await session.send(helpstr)

async def print_all_pot():
    pot_str = "现在约了的锅有："
    if len(cur_pots) == 0:
        return pot_str + "[无]"
    for i,pot in enumerate(cur_pots):
        pot_str += ("\n编号:" + str(i) + " 地点:" + pot.where+ " 时间:" + pot.when + " 口味:" + pot.what + '\n乘客:')
        for j,who in enumerate(pot.who):
            pot_str += str(j) + '.' + who
            if j == pot.driver_idx:
                pot_str += "(司机)"
            pot_str += " "
    return pot_str
