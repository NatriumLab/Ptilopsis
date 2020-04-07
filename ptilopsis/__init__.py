from mirai import (
  Mirai, GroupMessage, Depend, FriendMessage
)
from mirai.entities.builtins import ExecutorProtocol
from mirai.event.builtins import InternalEvent
from typing import (
  List, Dict
)
from mirai.logger import Session as SessionLogger
from .command import CommandEntity
from ptilopsis import string as btp
from mirai.misc import printer
import asyncio
import re
import functools

class Ptilopsis(object):
  """python-mirai 的指令系统支持库

  "请使用控制台输入指令以继续操作."
  """
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
    self.command_prefix = ["^" + re.escape(i) for i in command_prefix]

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

  async def GroupMessageListener(self, app: Mirai, message: GroupMessage):
    "一句话只能触发一个指令."
    message_string = message.toString()

    prefix = None
    prefix_result = None
    for prefix_pattern in self.command_prefix:
      prefix_result = re.match(prefix_pattern, message_string)
      if prefix_result:
        prefix = prefix_pattern
        break
    else:
      return
    
    # 如果到了这里, 就说明这句话试图触发一个指令
    matched_command_entity = None
    matched_command_params = None

    after_prefix = message_string[prefix_result.end():] # 提取出尝试执行的指令字符串
    for command in self.commands:
      matched_command_entity = command
      for command_match in [command.match, *command.aliases]:
        matched_command_params = command_match.parse(after_prefix)
        if matched_command_params == {} or matched_command_params: # 匹配到了.
          break
      else: # 没匹配到
        return

    if "GroupMessage" not in matched_command_entity.allow_events:
      return
    
    # 因为我们需要传入同一个上下文, 这里我们复用 application 机制中的 executer 方法
    # 传入 extra.

    await app.executor(ExecutorProtocol(
      callable=matched_command_entity.execator,
      dependencies=[
        *matched_command_entity.dependencies,
        *self.global_dependencies,
        *app.global_dependencies
      ],
      middlewares=[
        *matched_command_entity.middlewares,
        *self.global_middlewares,
        *app.global_middlewares
      ]
    ), InternalEvent(
      name="GroupMessage",
      body=message
    ), matched_command_params)

  async def FriendMessageListener(self, app: Mirai, message: FriendMessage):
    "一句话只能触发一个指令."
    message_string = message.toString()

    prefix = None
    prefix_result = None
    for prefix_pattern in self.command_prefix:
      prefix_result = re.match(prefix_pattern, message_string)
      if prefix_result:
        prefix = prefix_pattern
        break
    else:
      return
    
    # 如果到了这里, 就说明这句话试图触发一个指令
    matched_command_entity = None
    matched_command_params = None

    after_prefix = message_string[prefix_result.end():] # 提取出尝试执行的指令字符串
    for command in self.commands:
      matched_command_entity = command
      for command_match in [command.match, *command.aliases]:
        matched_command_params = command_match.parse(after_prefix)
        if matched_command_params: # 匹配到了.
          break
    else: # 没匹配到
      return

    if "FriendMessage" not in matched_command_entity.allow_events:
      return
    
    # 因为我们需要传入同一个上下文, 这里我们复用 application 机制中的 executer 方法
    # 传入 extra.

    await app.executor(ExecutorProtocol(
      callable=matched_command_entity.execator,
      dependencies=[
        *matched_command_entity.dependencies,
        *self.global_dependencies,
        *app.global_dependencies
      ],
      middlewares=[
        *matched_command_entity.middlewares,
        *self.global_middlewares,
        *app.global_middlewares
      ]
    ), InternalEvent(
      name="FriendMessage",
      body=message
    ), matched_command_params)