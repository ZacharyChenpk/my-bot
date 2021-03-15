import nonebot
from nonebot.adapters.mirai import WebsocketBot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from os import path

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)
nonebot.load_builtin_plugins()
nonebot.load_plugin("pot.plugins.pot")
nonebot.load_plugin("pot.plugins.dessert")

app = nonebot.get_asgi()

if __name__ == "__main__":
    nonebot.run()