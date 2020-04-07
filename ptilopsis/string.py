import re
import functools
from .exceptions import (
  StatsTransferError,
  ValueCheckError,
  FlagConflictError,
  ArgumentParseError
)
from .entities import (
    Normal, Require, Optional
)
from collections import Counter
from functools import lru_cache
from typing import List

# 这些规则都是互斥的, 并且是由转译层完成, 属于高级设定
default_handlers = {
  "int": lambda x: int(x),
  "float": lambda x: float(x),
  "LongParams": lambda x: x.split(" ")
}

def string_as_string(string):
  return f"\\{string}"

def signature_spliter(signature_string: str):
  return re.split(r"((?!\\)[<>\[\]\:\,])", signature_string)[:-1] # 最后一个元素是空的, 推断为 "$"(正则表达式中用于表示字符串结尾)

def signature_split_whole(signature_string: str):
  return re.split(r"((?!\\)[<\[].*?[>\]])", signature_string)

@lru_cache()
def signature_parser(signature_string: str):
  splited: List[str] = signature_spliter(signature_string)
  
  normal = [] # index
  require = [] # index
  optional = []
  flags = {} # index: flags
  stats = "normal"
  for index, string in enumerate(splited):
    string = string.strip()
    if (index - 1 >= 0 and splited[index-1] and splited[index-1][-1] == "\\") or all([
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
      if (index - 1 >= 0 and splited[index-1] and splited[index-1][-1] == "\\"):
        splited[index - 1] = splited[index - 1][:-1]
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
    "splited": splited,
    "normal": normal,
    "require": require,
    "optional": optional,
    "flags": flags
  }

def union_handle(signature_string: str, index: int) -> int:
  "处理 splited 和 whole 关系, 给出 splited 中的 index, 返回 whole 中的 index."
  splited = signature_spliter(signature_string)
  whole = signature_split_whole(signature_string)
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
      return l_index

@lru_cache()
def signature_sorter(signature_string: str):
  result = signature_parser(signature_string)
  splited = result['splited']
  whole = signature_split_whole(signature_string)
  indexer = functools.partial(union_handle, signature_string)
  
  # 因为推导式没法满足需求了...
  normal = {}
  for i in result['normal']:
    index = indexer(i)
    if index not in normal:
      normal[index] = splited[i]
    else:
      normal[index] += splited[i]
  return {
    "normal": normal,
    "require": {indexer(i): splited[i] for i in result['require']},
    "optional": {indexer(i): splited[i] for i in result['optional']},
    "flags": {splited[k].strip(): [splited[i].strip() for i in v] for k, v in result['flags'].items()}
  }

def list_without(seq, *args):
  return [i for i in seq if i not in args]

def signature_result_list_generate(in_result: dict):
  result = []
  for index, string in in_result['normal'].items():
    result.append(Normal(string, index))
  for index, param_name in in_result['require'].items():
    result.append(Require(param_name, index, in_result['flags'].get(param_name)))
  for index, optional_name in in_result['optional'].items():
    result.append(Optional(optional_name, index, in_result['flags'].get(optional_name)))
  return sorted(result, key=lambda x: x.index)

def special_rule_regex_generate(in_result: List):
  length = len(in_result)
  result_regex = ""
  continue_stats = False
  for index, value in enumerate(in_result):
    if isinstance(value, (Require, Optional)) and value.flags and "LongParams" in value.flags: # 包容万物.
      if index - 1 >= 0:
        last_component = in_result[index - 1]
        if type(last_component) == Normal:
          result_regex += last_component.regex_generater()
      result_regex += f"(?P<{value.name}>.*)"
      break
    if continue_stats:
      continue_stats = False
      continue
    if index + 1 <= length - 1:
      next_component = in_result[index + 1]
      if type(value) == Normal and type(next_component) == Optional and index != 0:
        if next_component.flags and "LongParams" in next_component.flags:
          continue
        result_regex += f"(({value.regex_generater()})?{next_component.regex_generater()})"
        continue_stats = True
      else:
        result_regex += value.regex_generater()
    else: # 直接取会 IndexError, 不需要怎么考虑了.
      result_regex += value.regex_generater()
  return result_regex

def find_flags(generater_list, name):
  for i in generater_list:
    if isinstance(i, (Require, Optional)):
      if i.name == name:
        return i.flags

def flags_find_handler(flags, extra_format={}):
  fused = {**default_handlers, **extra_format}
  checker_conflict = [i for i in flags if i in fused]
  if len(checker_conflict) > 1:
    # 要找出是哪几个冲突.
    raise FlagConflictError(", ".join(checker_conflict))
  if checker_conflict:
    return checker_conflict[0]

def parse(signature, string, extra_format={}, strict=False):
  """若返回 None, 代表转义失败, 但这只是 warning,
  不应该影响到程序主体(以此提供了一个 strict 参数, 抛出一个带有很多信息的错误).
  """
  sorted_data = signature_sorter(signature)
  regex_generater_list = signature_result_list_generate(sorted_data)
  final_regex = special_rule_regex_generate(regex_generater_list)

  regex_result = re.match(final_regex, string)
  if regex_result:
    original: dict = regex_result.groupdict()
    result = {}
    for name, value in original.items():
      flags = find_flags(regex_generater_list, name)
      if flags:
        handler_sign = flags_find_handler(flags, extra_format)
        if handler_sign:
          try:
            result[name] = {**default_handlers, **extra_format}[handler_sign](value)
          except Exception as e:
            if strict:
              raise ArgumentParseError("wrong format", name, flags, handler_sign) from e
            return None
        else:
          result[name] = value
      else:
        result[name] = value
    return result

class Signature:
  signature: str

  def __init__(self, signature):
    self.signature = signature

  def parse(self, target_string, extra_format={}, strict=False):
    return parse(self.signature, target_string, extra_format, strict)

def compile(signature):
  return Signature(signature)