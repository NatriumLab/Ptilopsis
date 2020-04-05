from mirai import (
  Mirai, GroupMessage, Depend
)
from typing import (
  List, Dict
)
from .exceptions import (
  StatsTransferError,
  ValueCheckError
)
from .command import CommandEntity
import re

class Ptilopsis(object):
  application: Mirai
  listen_events: List[str]

  command_prefix: List[str]
  commands: List[CommandEntity]

  def __init__(self,
    app: Mirai,
    listen_events: List[str] = [
      "FriendMessage",
      "GroupMessage"
    ],
    command_prefix: List[str] = [">"],
    dependencies: List[Depend] = [],
    middlewares: List = []
  ):
    self.application = app
    self.listen_events = listen_events
    self.command_prefix = [self.string_as_string(i) for i in command_prefix]

  @staticmethod
  def string_as_string(string):
    return f"\\{string}"

  @staticmethod
  def signature_spliter(signature_string: str):
    return re.split("([<>\[\]\:\,])", signature_string)[:-1] # 最后一个元素是空的, 推断为 "$"(正则表达式中用于表示字符串结尾)

  @staticmethod
  def signature_split_whole(signature_string: str):
    return re.split(r"([<\[].*?[>\]])", signature_string)[:-1]

  @staticmethod
  def signature_parser(signature_string: str):
    splited: List[str] = Ptilopsis.signature_spliter(signature_string)
    
    normal = [] # index
    require = [] # index
    optional = []
    flags = {} # index: flags

    stats = "normal"
    for index, string in enumerate(splited):
      string = string.strip()
      if all([
        stats == "normal",
        string not in ("<", ">", "[", "]", ":"),
        stats not in [
          "require", "optional",
          "require:warp",
          "require:wait-flags",
          "optional:warp",
          "optional:wait-flags"
        ]
      ]):
        normal.append(index)
      elif stats == "normal" and string == "<":
        stats = "require"
      elif stats == "require":
        if string not in ("<", ">", "[", "]"):
          if re.match(r"^[_a-zA-Z][a-zA-Z0-9_]*$", string):
            require.append(index)
            stats = "require:warp"
          else:
            if string != ":":
              raise ValueCheckError(f"cannot parse '{string}' as a vaild warp.")
        elif string == ">":
          stats = "normal"
          continue
        else:
          raise StatsTransferError(f"cannot transfer from 'require' to 'require': {string}")
      elif stats == "require:warp":
        if string in [":", ">"]:
          if string == ":": 
            stats = "require:wait-flags"
          elif string == ">":
            # 退出 require 状态
            stats = "normal"
          else:
            raise StatsTransferError("cannot transfer from 'require:warp' to others expect 'require:wait_flags' or 'normal'.")
        else:
          raise ValueCheckError("cannot parse '", string, "' as a vaild point.")
      elif stats == "require:wait-flags": # 听说你在等? 我来了!
        # 定义了flags(用,分割.)
        if string == ",":
          continue
        if string == ">":
          # 退出了.
          stats = "normal"
        if re.match(r"^[_a-zA-Z][a-zA-Z0-9_]*$", string):
          flags.setdefault(require[-1], [])
          flags[require[-1]].append(index)
          # 这里stats不需要改变.
      # Optional 来了.
      elif stats == "normal" and string == "[":
        stats = "optional"
      elif stats == "optional":
        if string not in ("<", ">", "[", "]"):
          if re.match(r"^[_a-zA-Z][a-zA-Z0-9_]*$", string):
            optional.append(index)
            stats = "optional:warp"
          else:
            if string != ":":
              raise ValueCheckError(f"cannot parse '{string}' as a vaild warp.")
        elif string == "]":
          stats = "normal"
          continue
        else:
          raise StatsTransferError(f"cannot transfer from 'optional' to 'optional': {string}")
      elif stats == "optional:warp":
        if string in [":", "]"]:
          if string == ":":
            stats = "optional:wait-flags"
          elif string == "]":
            # 退出 optional 状态
            stats = "normal"
          else:
            raise StatsTransferError("cannot transfer from 'optional:warp' to others expect 'optional:wait_flags' or 'normal'.")
        else:
          raise ValueCheckError(f"cannot parse '{string}' as a vaild point.")
      elif stats == "optional:wait-flags": # 听说你在等? 我来了!
        # 定义了flags(用,分割.)
        if string == ",":
          continue
        if string == "]":
          # 退出了.
          stats = "normal"
        if re.match(r"^[_a-zA-Z][a-zA-Z0-9_]*$", string):
          flags.setdefault(optional[-1], [])
          flags[optional[-1]].append(index)
          # 这里stats不需要改变.
      else:
        # 这里大多都是跳到了不该跳的地方, 要报错.
        print(splited)
        raise StatsTransferError(f"cannot transfer from '{stats}' with '{string}', it happened in {index}")
    return {
      "normal": normal,
      "require": require,
      "optional": optional,
      "flags": flags
    }

  @staticmethod
  def union_handle(signature_string: str, index: int) -> int:
    "处理 splited 和 whole 关系, 给出 splited 中的 index, 返回 whole 中的 index."
    splited = Ptilopsis.signature_spliter(signature_string)
    whole = Ptilopsis.signature_split_whole(signature_string)
    #print(splited, whole)

    current_string = ''
    current_start = 0
    current_whole_index = 0
    ranges = []
    for l_index, value in enumerate(splited):
      current_string += value
      if current_string == whole[current_whole_index]:
        current_whole_index += 1
        ranges.append(range(current_start, l_index + 1))
        current_start = l_index + 1
        current_string = ''

    for l_index, value in enumerate(ranges):
      if index in value:
        return whole[l_index]

  @staticmethod
  def signature_sorter(signature_string: str):
    splited = Ptilopsis.signature_spliter(signature_string)
    result = Ptilopsis.signature_parser(signature_string)
    return {
      "normal": {i: splited[i] for i in result['normal']},
      "require": {i: splited[i] for i in result['require']},
      "optional": {i: splited[i] for i in result['optional']},
      "flags": {splited[k].strip(): [splited[i].strip() for i in v] for k, v in result['flags'].items()}
    }

  async def GroupMessageListener(self, app: Mirai, message: GroupMessage):
    pass
