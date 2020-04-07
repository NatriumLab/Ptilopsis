from mirai import Mirai, Group
from ptilopsis import Ptilopsis

app = Mirai("mirai://192.168.31.188:8070/ws?qq=208924405&authKey=213we355gdfbaerg")
ptilopsis = Ptilopsis(app, command_prefix=[""])

@ptilopsis.register(r"release\: \<\<magic>\>", allow_events=["GroupMessage"])
async def p(app: Mirai, group: Group, magic):
    await app.sendGroupMessage(group, f"*你发动了{magic}*")

if __name__ == "__main__":
    app.run()