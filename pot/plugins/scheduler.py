import nonebot
from nonebot import on_command, require
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.permission import Permission
from nonebot import require

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.cqhttp.message import Message

from datetime import datetime
import os
import pickle
import pytz

#--------------------------
# Author: Zachary Chen
#--------------------------

QQGROUP = 1919810

print('-----------')
driver = nonebot.get_driver()
scheduler = require("nonebot_plugin_apscheduler").scheduler

def add_pot_scheduler(group_id, hour, minute):

    _schedule_setting_id = f'ScheduleMsg_{QQGROUP}_{hour}_{minute}_【定时呼锅】'
    async def _scheduler_handle():
        self_bot = nonebot.get_bots()[str(QQGROUP)]
        await self_bot.send_group_msg(group_id=group_id, message=Message(f'【定时消息】\n{"="*12}\n现在是{hour}时{minute}分！\n该约锅啦！'))

    try:
        scheduler.remove_job(_schedule_setting_id)
    except Exception as e:
        print(e)
    scheduler.add_job(
        _scheduler_handle,
        'cron',
        hour=hour-8,
        minute=minute,
        id=_schedule_setting_id,
        coalesce=True,
        misfire_grace_time=10
    )

add_pot_scheduler(QQGROUP, 11, 40)
add_pot_scheduler(QQGROUP, 11, 50)
add_pot_scheduler(QQGROUP, 16, 40)
add_pot_scheduler(QQGROUP, 16, 50)
add_pot_scheduler(QQGROUP, 17, 50)