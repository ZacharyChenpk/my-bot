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
from nonebot.adapters.cqhttp import MessageSegment

# scheduler = require("plugin-apscheduler-master.nonebot_plugin_apscheduler").scheduler
from datetime import datetime
import os
import pickle
import pytz
from collections import Counter

#--------------------------
# Author: Zachary Chen
#--------------------------

print('----------- dessert -----------')

class one_dessert_item:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def __str__(self):
        return self.name + '   ' + str(self.price)

class dessert_menu:
    def __init__(self, name):
        self.name = name
        self.item_list = []

    def add_item(self, name, price):
        for it in self.item_list:
            if it.name == name:
                it.price = float(price)
                return 
        new_item = one_dessert_item(name, float(price))
        self.item_list.append(new_item)

    def __str__(self):
        ret = self.name + '\n'
        for i, it in enumerate(self.item_list):
            ret = ret + str(i+1) + '. ' + str(it) + '\n'
        if len(self.item_list) == 0:
            ret = ret + '[无选项]\n'
        return ret

menus = []

def print_all_menus():
    with open('cur_menus_dump', 'wb') as f:
        pickle.dump(menus, f)
    menus_str = "现在的菜单有：\n"
    if len(menus) == 0:
        return menus_str + "[无]"
    for i, menu in enumerate(menus):
        menus_str += str(i+1)+'. ' + menu.name+'\n'
    return menus_str

def find_menu_by_name(name):
    if name.isdigit():
        ind = int(name) - 1
        if ind < 0 or ind >= len(menus):
            return False
        return ind, menus[ind]

    for ind, i in enumerate(menus):
        if i.name == name:
            return ind, i
    return False

def find_dessert_by_name(name, menu):
    if name.isdigit():
        ind = int(name) - 1
        if ind < 0 or ind >= len(menu.item_list):
            return False
        return ind, menu.item_list[ind]

    for ind, i in enumerate(menu.item_list):
        if len(name) <= len(i.name) and i.name[:len(name)] == name:
            return ind, i

    l = []
    for ind, i in enumerate(menu.item_list):
        if len(name) <= len(i.name) and i.name.find(name) > 0:
            l.append((ind, i))
    if len(l) == 1:
        return l[0]

    return False

class dessert_bucket:
    def __init__(self, owner, menu_name):
        self.owner = owner
        # self.picked = []
        self.picked = {}
        self.menu_name = menu_name
        self.note = '[无]'

    def change_item(self, dessert_name, howmany):
        the_menu = find_menu_by_name(self.menu_name)[1]
        print(dessert_name)
        d = find_dessert_by_name(dessert_name, the_menu)
        if not d:
            return False
        # self.picked.append(d)
        if howmany == 0:
            if dessert_name in self.picked:
                del self.picked[dessert_name]
            return True
        self.picked[dessert_name] = howmany
        return True

    def total_price(self):
        # return sum([a.price for a in self.picked])
        the_menu = find_menu_by_name(self.menu_name)[1]
        print([find_dessert_by_name(a, the_menu)[1].price * b for a,b in self.picked.items()])
        return sum([find_dessert_by_name(a, the_menu)[1].price * b for a,b in self.picked.items()], 0)

    def __str__(self):
        ret = self.owner + ' 备注: '+ self.note +' 总价: ' + str(self.total_price()) +'\n'
        # cnter = Counter([a.name for a in self.picked])
        for name, n in self.picked.items():
            ret += '  '+name+' * '+str(n)+'\n'
        return ret

class dessert_truck:
    def __init__(self, menu_name, driver, time):
        self.menu_name = menu_name
        self.driver = driver
        # self.driver_qq = driver_qq
        self.bucket_list = []
        self.time = time

    def get_bucket_and_index(self, who):
        index = -1
        if who.isdigit():
            the_bucket = self.bucket_list[int(who)]
            index = int(who)
        else:
            the_bucket = False
            for ind, i in enumerate(self.bucket_list):
                if i.owner == who:
                    the_bucket = i
                    index = ind
                    break
            if not the_bucket:
                self.bucket_list.append(dessert_bucket(who, self.menu_name))
                the_bucket = self.bucket_list[-1]
        return the_bucket, index

    def change_item(self, who, dessert_name, howmany):
        the_bucket, index = self.get_bucket_and_index(who)
        ret = the_bucket.change_item(dessert_name, howmany)
        if ret and len(the_bucket.picked) == 0:
            self.bucket_list.pop(index)
        return ret
    
    def change_note(self, who, note):
        the_bucket, index = self.get_bucket_and_index(who)
        the_bucket.note = note

    def __str__(self):
        ret = '司机:'+self.driver + ' 菜单:'+ self.menu_name + ' 预计送达时间:' + self.time + ' 总价:'+ str(sum([b.total_price() for b in self.bucket_list])) + '\n'
        for i, b in enumerate(self.bucket_list):
            ret += str(i+1)+'. '+str(b)
        return ret

trucks = []

def print_all_trucks():
    with open('cur_trucks_dump', 'wb') as f:
        pickle.dump(trucks, f)
    truck_str = "现在的甜品车有：\n"
    if len(trucks) == 0:
        return truck_str + "[无]"
    for i, truck in enumerate(trucks):
        truck_str += str(i+1)+'. 司机:'+truck.driver + ' 菜单:'+ truck.menu_name + ' 预计送达时间:' + truck.time + ' 总价:'+ str(sum([b.total_price() for b in truck.bucket_list], 0)) + '\n'
        total_bucket = {}
        for b in truck.bucket_list:
            for name, n in b.picked.items():
                if name not in total_bucket:
                    total_bucket[name] = 0
                total_bucket[name] += n
        for name, n in total_bucket.items():
            truck_str += '  '+name+' * '+str(n)+'\n'
    return truck_str

if os.path.exists('cur_menus_dump'):
    with open('cur_menus_dump', 'rb') as f:
        menus = pickle.load(f)
if os.path.exists('cur_trucks_dump'):
    with open('cur_trucks_dump', 'rb') as f:
        trucks = pickle.load(f)

new_menu = on_command("新增甜品菜单", permission=Permission(), priority=5)
@new_menu.handle()
async def handle_first_receive_new_menu(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    for a,b in zip(args, ['menu_name']):
        state[b] = a

@new_menu.got("menu_name", prompt="菜单名？比如，这是哪里的甜点？")
async def new_menu_got_who(bot: Bot, event: Event, state: T_State):
    if state['menu_name'].lower() == 'quit':
        await new_menu.finish('溜了溜了.jpg')
    names = [a.name for a in menus]
    if state['menu_name'] in names:
        await new_menu.reject("已经有同名菜单了哦，再输一次菜单名罢（")
    menus.append(dessert_menu(state['menu_name']))
    await new_menu.finish('新建菜单成功！\n' + print_all_menus())

new_item = on_command("新增甜品", permission=Permission(), priority=5)
@new_item.handle()
async def handle_first_receive_new_item(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichmenu', 'name', 'price']
    for a,b in zip(args, keys):
        state[b] = a

@new_item.got("whichmenu", prompt="哪个菜单？")
async def new_item_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['whichmenu'].lower() == 'quit':
        await new_item.finish('溜了溜了.jpg')
    state['menu'] = find_menu_by_name(state['whichmenu'])
    if not state['menu']:
        await new_item.reject("？真的有这个菜单吗，再输一次菜单名罢（")

@new_item.got("name", prompt="新甜品叫啥？")
async def new_item_got_name(bot: Bot, event: Event, state: T_State):
    if state['name'].lower() == 'quit':
        await new_item.finish('溜了溜了.jpg')

@new_item.got("price", prompt="单价？")
async def new_item_got_price(bot: Bot, event: Event, state: T_State):
    if state['price'].lower() == 'quit':
        await new_item.finish('溜了溜了.jpg')
    try:
        a = float(state['price'])
        state['menu'][1].add_item(state['name'], state['price'])
        with open('cur_menus_dump', 'wb') as f:
            pickle.dump(menus, f)
        await new_menu.finish('新增甜品成功！该菜单：\n'+str(state['menu'][1]))
    except ValueError:
        await new_item.reject("？再输一次单价罢（")

del_item = on_command("删除甜品", permission=Permission(), priority=5)
@del_item.handle()
async def handle_first_receive_del_item(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichmenu', 'name']
    for a,b in zip(args, keys):
        state[b] = a

@del_item.got("whichmenu", prompt="哪个菜单？")
async def del_item_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['whichmenu'].lower() == 'quit':
        await del_item.finish('溜了溜了.jpg')
    state['menu'] = find_menu_by_name(state['whichmenu'])
    if not state['menu']:
        await del_item.reject("？真的有这个菜单吗，再输一次菜单名罢（")

@del_item.got("name", prompt="哪个甜品？")
async def del_item_got_name(bot: Bot, event: Event, state: T_State):
    if state['name'].lower() == 'quit':
        await del_item.finish('溜了溜了.jpg')
    a = find_dessert_by_name(state['name'], state['menu'][1])
    if not a:
        await del_item.reject("？真的有这个甜品吗，再输一次甜品名罢（")
    for t in trucks:
        if t.menu_name == state['whichmenu']:
            for b in t.bucket_list:
                if state['name'] in b.picked:
                    await del_item.reject("有人点了这个甜品哦，输入其他甜品吧")
    state['menu'][1].item_list.pop(a[0])
    with open('cur_menus_dump', 'wb') as f:
        pickle.dump(menus, f)
    await del_item.finish('删除甜品成功！该菜单：\n'+str(state['menu'][1]))

del_menu = on_command("删除甜品菜单", permission=Permission(), priority=5)
@del_menu.handle()
async def handle_first_receive_del_menu(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    for a,b in zip(args, ['whichmenu']):
        state[b] = a
    # state[''] = args[0]

@del_menu.got("whichmenu", prompt="菜单名？")
async def del_menu_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['whichmenu'].lower() == 'quit':
        await del_menu.finish('溜了溜了.jpg')
    ret = find_menu_by_name(state['whichmenu'])
    if not ret:
        await del_menu.reject("？真的有这个菜单吗，再输一次菜单名罢（")
    for t in trucks:
        if t.menu_name == state['whichmenu']:
            await del_menu.reject("这个菜单还有车在用呢，换一个菜单呗？")
    menus.pop(ret[0])
    with open('cur_menus_dump', 'wb') as f:
        pickle.dump(menus, f)
    await del_menu.finish('删除菜单成功！\n' + print_all_menus())

new_truck = on_command("开甜品车", permission=Permission(), priority=5)
@new_truck.handle()
async def handle_first_receive_new_truck(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichmenu', 'who', 'time']
    for a,b in zip(args, keys):
        state[b] = a

@new_truck.got("whichmenu", prompt="哪个菜单？")
async def new_truck_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['whichmenu'].lower() == 'quit':
        await new_truck.finish('溜了溜了.jpg')
    state['menu'] = find_menu_by_name(state['whichmenu'])
    if not state['menu']:
        await new_truck.reject("？真的有这个菜单吗，再输一次菜单名罢（")

@new_truck.got("who", prompt="谁开车？")
async def new_truck_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'].lower() == 'quit':
        await new_truck.finish('溜了溜了.jpg')

@new_truck.got("time", prompt="大概什么时候到？")
async def new_truck_got_time(bot: Bot, event: Event, state: T_State):
    if state['time'].lower() == 'quit':
        await new_truck.finish('溜了溜了.jpg')
    trucks.append(dessert_truck(state['whichmenu'], state['who'], state['time']))
    await new_truck.finish('开车成功！\n'+print_all_trucks())

timechange = on_command("改时间", permission=Permission(), priority=5)
@timechange.handle()
async def handle_first_receive_timechange(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'time']
    for a,b in zip(args, keys):
        state[b] = a

@timechange.got("which", prompt="哪个车？")
async def timechange_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['which'].lower() == 'quit':
        await timechange.finish('溜了溜了.jpg')
    if not state['which'].isdigit() or int(state['which']) < 1 or int(state['which']) > len(trucks):
        await timechange.reject("车的编号不太对吧？再输入一次吧")

@timechange.got("time", prompt="谁开的？")
async def timechange_got_who(bot: Bot, event: Event, state: T_State):
    if state['time'].lower() == 'quit':
        await timechange.finish('溜了溜了.jpg')
    which = int(state['which'])-1
    trucks[which].time = state['time']
    await timechange.finish('修改成功！\n'+print_all_trucks())

del_truck = on_command("取消甜品车", permission=Permission(), priority=5)
@del_truck.handle()
async def handle_first_receive_del_truck(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['which', 'who']
    for a,b in zip(args, keys):
        state[b] = a

@del_truck.got("which", prompt="哪个车？")
async def del_truck_got_whichmenu(bot: Bot, event: Event, state: T_State):
    if state['which'].lower() == 'quit':
        await del_truck.finish('溜了溜了.jpg')
    if not state['which'].isdigit() or int(state['which']) < 1 or int(state['which']) > len(trucks):
        await del_truck.reject("车的编号不太对吧？再输入一次吧")

@del_truck.got("who", prompt="谁开的？")
async def del_truck_got_who(bot: Bot, event: Event, state: T_State):
    if state['who'].lower() == 'quit':
        await del_truck.finish('溜了溜了.jpg')
    which = int(state['which'])-1
    if state['who'] != trucks[which].driver:
        await del_truck.reject("这车不是ta开的吧？是不是输错了？再输入一次司机名吧")
    trucks.pop(which)
    await del_truck.finish('取消成功！\n'+print_all_trucks())

change_item = on_command("上甜品车", permission=Permission(), priority=5)
@change_item.handle()
async def handle_first_receive_change_item(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    # keys = ['whichtruck', 'name', 'dessert', 'howmany']
    if len(args) > 0:
        state['whichtruck'] = args[0]
    if len(args) > 1:
        state['name'] = args[1]
    if len(args) > 2:
        state['dessert'] = args[2:-1]
    if len(args) > 3:
        n = False
        try:
            n = float(args[-1])
        except:
            pass
        if n:
            state['howmany'] = args[-1]
        else:
            state['dessert'].append(args[-1])
            state['howmany'] = '1'
    # for a,b in zip(args, keys):
    #     state[b] = a

@change_item.got("whichtruck", prompt="车编号？")
async def change_item_got_whichtruck(bot: Bot, event: Event, state: T_State):
    if state['whichtruck'].lower() == 'quit':
        await change_item.finish('溜了溜了.jpg')
    if not state['whichtruck'].isdigit() or int(state['whichtruck']) < 1 or int(state['whichtruck']) > len(trucks):
        await change_item.reject("车的编号不太对吧？再输入一次吧")
    state['truck'] = trucks[int(state['whichtruck'])-1]

@change_item.got("name", prompt="你的名字？")
async def change_item_got_name(bot: Bot, event: Event, state: T_State):
    if state['name'].lower() == 'quit':
        await change_item.finish('溜了溜了.jpg')
    if 'dessert' not in state.keys():
        the_menu = str(find_menu_by_name(state['truck'].menu_name)[1])
        await change_item.send(the_menu)

@change_item.got("dessert", prompt="甜品名字/编号？")
async def change_item_got_dessert(bot: Bot, event: Event, state: T_State):
    if isinstance(state['dessert'], str) and state['dessert'].lower() == 'quit':
        await change_item.finish('溜了溜了.jpg')
    if isinstance(state['dessert'], str):
        state['dessert'] = state['dessert'].strip().split()
    # state['dessert_item'] = find_dessert_by_name(state['dessert'], find_menu_by_name(state['truck'].menu_name)[1])
    state['dessert_item'] = [find_dessert_by_name(d, find_menu_by_name(state['truck'].menu_name)[1]) for d in state['dessert']]
    # if not state['dessert_item']:
    if False in state['dessert_item']:
        idx = state['dessert_item'].index(False)
        await change_item.reject(state['dessert'][idx]+"？真的有这个甜品吗？再输一次罢")

@change_item.got("howmany", prompt="多少份？（可以是0）")
async def change_item_got_dessert(bot: Bot, event: Event, state: T_State):
    if state['howmany'].lower() == 'quit':
        await change_item.finish('溜了溜了.jpg')
    n = False
    try:
        n = float(state['howmany'])
    except:
        pass
    if not n or n < 0:
        await change_item.reject("？多少份？")
    ret = [state['truck'].change_item(state['name'], d[1].name, n) for d in state['dessert_item']]
    if False in ret:
        idx = ret.index(False)
        await change_item.reject(state['dessert_item'][idx][1].name+"？真的有这个甜品吗？重新输入命令罢")
    with open('cur_trucks_dump', 'wb') as f:
        pickle.dump(trucks, f)
    await change_item.finish('修改成功！该车：\n'+str(state['truck']))

change_note = on_command("修改甜品备注", permission=Permission(), priority=5)
@change_note.handle()
async def handle_first_receive_change_note(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichtruck', 'name', 'note']
    for a,b in zip(args, keys):
        state[b] = a

@change_note.got("whichtruck", prompt="车编号？")
async def change_note_got_whichtruck(bot: Bot, event: Event, state: T_State):
    if state['whichtruck'].lower() == 'quit':
        await change_note.finish('溜了溜了.jpg')
    if not state['whichtruck'].isdigit() or int(state['whichtruck']) < 1 or int(state['whichtruck']) > len(trucks):
        await change_note.reject("车的编号不太对吧？再输入一次吧")
    state['truck'] = trucks[int(state['whichtruck'])-1]

@change_note.got("name", prompt="你的名字？")
async def change_note_got_name(bot: Bot, event: Event, state: T_State):
    if state['name'].lower() == 'quit':
        await change_note.finish('溜了溜了.jpg')
    flag = False
    for ind, i in enumerate(state['truck'].bucket_list):
        if i.owner == state['name']:
            flag = True
            break
    if not flag:
        await change_note.reject("真的有这个人吗？重新输入名字吧")

@change_note.got("note", prompt="新的备注？")
async def change_note_got_note(bot: Bot, event: Event, state: T_State):
    if state['note'].lower() == 'quit':
        await change_note.finish('溜了溜了.jpg')
    state['truck'].change_note(state['name'], state['note'])
    with open('cur_trucks_dump', 'wb') as f:
        pickle.dump(trucks, f)
    await del_truck.finish('修改成功！该车：\n'+str(state['truck']))

dessert_ask = on_command("有甜品吗", permission=Permission(), priority=3)
@dessert_ask.handle()
async def handle_first_receive_dessert_ask(bot: Bot, event: Event, state: T_State):
    report = print_all_trucks()
    await dessert_ask.finish(report)

menu_ask = on_command("查看菜单列表", permission=Permission(), priority=3)
@menu_ask.handle()
async def handle_first_receive_menu_ask(bot: Bot, event: Event, state: T_State):
    report = print_all_menus()
    await menu_ask.finish(report)

menu_see = on_command("查看菜单", permission=Permission(), priority=3)
@menu_see.handle()
async def handle_first_receive_menu_see(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichmenu']
    for a,b in zip(args, keys):
        state[b] = a

@menu_see.got("whichmenu", prompt="菜单名？")
async def menu_see_got_who(bot: Bot, event: Event, state: T_State):
    if state['whichmenu'].lower() == 'quit':
        await menu_see.finish('溜了溜了.jpg')
    ret = find_menu_by_name(state['whichmenu'])
    if not ret:
        await menu_see.reject("？真的有这个菜单吗，再输一次菜单名罢（")
    await menu_see.finish(str(ret[1]))

truck_see = on_command("查看甜品车", permission=Permission(), priority=5)
@truck_see.handle()
async def handle_first_receive_truck_see(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split()
    keys = ['whichtruck']
    for a,b in zip(args, keys):
        state[b] = a

@truck_see.got("whichtruck", prompt="车编号？")
async def truck_see_got_whichtruck(bot: Bot, event: Event, state: T_State):
    if state['whichtruck'].lower() == 'quit':
        await truck_see.finish('溜了溜了.jpg')
    if not state['whichtruck'].isdigit() or int(state['whichtruck']) < 1 or int(state['whichtruck']) > len(trucks):
        await truck_see.reject("车的编号不太对吧？再输入一次吧")
    await truck_see.finish(str(trucks[int(state['whichtruck'])-1]))

dessert_help = on_command("甜品", permission=Permission(), priority=1)
@dessert_help.handle()
async def handle_first_receive_dessert_help(bot: Bot, event: Event, state: T_State):
    helpstr = "甜品助手指令:\n /甜品 : 输出本帮助\n /新增甜品菜单 <菜单名>\n /新增甜品 <菜单名/编号> <甜品名> <单价> : 为指定菜单增加甜品\n /删除甜品 <菜单名/编号> <甜品名/编号> : 为指定菜单删除甜品\n /删除甜品菜单 <菜单名/编号> : 删除一个没有对应甜品车的菜单\n /开甜品车 <菜单名/编号> <司机名> <抵达时间地点> : 根据给定菜单开一个甜品车\n /改时间 <车编号> <抵达时间地点> : 修改甜品车的抵达时间/地点\n /取消甜品车 <车编号> <司机名> : 取消一个甜品车 \n /上甜品车 <车编号> <你的ID> <甜品名/编号> <数量> : 修改对应车中你点的该甜品数量（从无到有则新增，设为0则删除，多个以空格连接）\n /修改甜品备注 <车编号> <你的ID> <新备注> : 在对应车中修改你的备注\n /查看菜单列表 : 看看有哪些菜单\n /查看菜单 <菜单名/编号> : 查看对应菜单的详细内容\n /有甜品吗 : 看看有哪些车\n /查看甜品车 <车编号> : 查看对应车的详细内容\n QUIT 或 quit: 结束当前命令（不然会被追问）\n以上所有参数可以分多次输入"
    await dessert_help.finish(helpstr)