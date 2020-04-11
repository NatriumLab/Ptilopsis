from mirai import (
  Mirai, GroupMessage, Depend, FriendMessage, MessageChain
)
from mirai.entities.builtins import ExecutorProtocol
from mirai.event.builtins import InternalEvent
from typing import (
  List, Dict
)
from mirai.logger import Session as SessionLogger
from .command import CommandEntity
from ptilopsis import (
  string as btp,
  objective as oit
)
from mirai.misc import printer, argument_signature
import asyncio
import re
import functools
import copy
from typing import Union

class Ptilopsis(object):
  """python-mirai 的指令系统支持库

  "请使用控制台输入指令以继续操作."
  """
  # TODO: ParametersChecker for Ptilopsis Command.
  application: Mirai
  listen_events: List[str]

  command_prefix: List[str]
  commands: List[CommandEntity] = []

  global_dependencies: List[Depend]
  global_middlewares: List

  def __init__(self,
    app: Mirai,
    listen_events: List[str] = [
      "FriendMessage",
      "GroupMessage"
    ],
    command_prefix: List[str] = [">"],
    global_dependencies: List[Depend] = [],
    global_middlewares: List = []
  ):
    self.application = app
    self.listen_events = listen_events
    self.command_prefix = [re.escape(i) for i in command_prefix]

    self.global_dependencies = global_dependencies
    self.global_middlewares = global_middlewares
    if "^/" in self.command_prefix:
      SessionLogger.warn("you shouldn't use '/' as a prefix, because it's used by mirai-console...")
      SessionLogger.warn("ok, we will support '/' as a prefix in the future..")
    
    if "GroupMessage" in listen_events:
      app.receiver("GroupMessage")(self.GroupMessageListener)
    if "FriendMessage" in listen_events:
      app.receiver("FriendMessage")(self.FriendMessageListener)

  def register(self, 
      command_signature: str,
      aliases: List[str] = [],
      priority: int = 0,
      dependencies: List[Depend] = [],
      middlewares: List = [],
      allow_events: List[str] = ["GroupMessage", "FriendMessage"]
    ):
    def warpper(func):
      self.commands.append(CommandEntity(
        func, btp.compile(command_signature), [btp.compile(i) for i in aliases], priority,
        dependencies, middlewares, allow_events
      ))
      self.commands = sorted(self.commands, key=lambda x: x.priority)
      return func
    return warpper

  def message_handler(self, message: Union[FriendMessage, GroupMessage]):
    "一句话只能触发一个指令."
    after_prefix = None
    for prefix_pattern in self.command_prefix:
      after_prefix = \
        oit.chain_regex_match_headpop(
          copy.copy(message.messageChain),
          prefix_pattern
        )
      if after_prefix:
        break
    else:
      return
    
    # 如果到了这里, 就说明这句话试图触发一个指令
    matched_command_entity = None
    matched_command_params = None
    special_handle_for_raw_string = None
    matched_result = None
    for command in self.commands:
      matched_command_entity = command
      for command_match in [command.match, *command.aliases]:
        matched_info = oit.chain_match(command_match, 
          MessageChain(__root__=after_prefix.__root__[1:])
        )
        if matched_info: # 匹配到了.
          matched_result, special_handle_for_raw_string = matched_info
          break
      else: # 没匹配到
        return
      
    # 处理 matched_command_params
    optional_params = {
      param.name: param.default \
        for param in \
          argument_signature(matched_command_entity.execator)
    }
    return {
      "command": matched_command_entity,
      "parameters": {
        **({
          # 因为蜜汁原因, 导致我们还得判断一步...但这应该在外部执行(要获取 execator 的 default...)
          # 多出来的这一步是因为 python-mirai 内部逻辑的缺点...我们必须克服它.
          k: special_handle_for_raw_string(v) if isinstance(v, str) else 
            (v if v != None else optional_params.get(k))
          for k, v in matched_result.items()
        })
      }
    }

  async def GroupMessageListener(self, app: Mirai, message: GroupMessage):
    handle_result = self.message_handler(message)
    if not handle_result:
      return
    if "GroupMessage" not in handle_result['command'].allow_events:
      return

    await app.executor(ExecutorProtocol(
      callable=handle_result['command'].execator,
      dependencies=[
        *handle_result['command'].dependencies,
        *self.global_dependencies,
        *app.global_dependencies
      ],
      middlewares=[
        *handle_result['command'].middlewares,
        *self.global_middlewares,
        *app.global_middlewares
      ]
    ), InternalEvent(
      name="GroupMessage",
      body=message
    ), handle_result['parameters'])

  async def FriendMessageListener(self, app: Mirai, message: FriendMessage):
    handle_result = self.message_handler(message)
    if not handle_result:
      return
    if "FriendMessage" not in handle_result['command'].allow_events:
      return

    await app.executor(ExecutorProtocol(
      callable=handle_result['command'].execator,
      dependencies=[
        *handle_result['command'].dependencies,
        *self.global_dependencies,
        *app.global_dependencies
      ],
      middlewares=[
        *handle_result['command'].middlewares,
        *self.global_middlewares,
        *app.global_middlewares
      ]
    ), InternalEvent(
      name="FriendMessage",
      body=message
    ), handle_result['parameters'])