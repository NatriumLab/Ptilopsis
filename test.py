from ptilopsis import Ptilopsis
from mirai import Mirai
from devtools import debug

app = Mirai("mirai://192.168.31.188:8070/ws?qq=208924405&authKey=213we355gdfbaerg")
cm = Ptilopsis(app)

@cm.register("test `fa`[something]")
async def u(something=None):
    debug(something)

if __name__ == "__main__":
    app.run()