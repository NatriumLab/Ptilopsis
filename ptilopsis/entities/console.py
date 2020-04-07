from pydantic import BaseModel
from typing import List, Optional

class CommandTask(BaseModel):
    "处理由 mirai-console 通过 mirai-api-http 分发的指令请求."
    name: str
    friend: int
    group: int
    args: List[str]