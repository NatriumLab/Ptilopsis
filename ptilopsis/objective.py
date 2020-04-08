from .string import signature_sorter, signature_result_list_generate, Signature
from mirai import MessageChain, Plain
from .entities import Normal, Require, Optional
from typing import List
import re
import random

def fix_merge(chain: MessageChain):
  stats = None

  temp_plain: Plain = None
  result = []
  for i in chain:
    if stats != "merge" and isinstance(i, Plain):
      temp_plain = i
      stats = "merge"
    else:
      if not isinstance(i, Plain): # 这里保存.
        stats = None
        result.append(temp_plain)
        result.append(i)
        continue
      if stats == "merge":
        if isinstance(i, Plain):
          temp_plain.text += i.text
        else:
          stats = None
  else:
    if not result or result[-1] != temp_plain:
      result.append(temp_plain)
  return result

def chain_split(chain: MessageChain, split_str: str) -> List[MessageChain]:
  chain = fix_merge(chain)
  length = len(chain)

  result = []
  last_str = None
  for index, component in enumerate(chain):
    if isinstance(component, Plain):
      char_lists = component.toString().split(split_str)
      if len(char_lists) > 1:
        result.append(MessageChain(__root__=[
          Plain(splited_plain_string) for splited_plain_string in \
            (char_lists[:-1] if index != length - 1 else char_lists)
        ]))
        if index != length - 1:
          last_str = char_lists[-1]
        else:
          last_str = None
      else:
        last_str = component.toString()
    else:
      result.append(MessageChain(__root__=[
        *([Plain(last_str)] if last_str else []),
        component
      ]))
  return result

def chain_match(signature: Signature, chain: MessageChain) -> dict:
  signature_array = signature_result_list_generate(
    signature_sorter(signature.signature))

  if not chain:
    return
  chain.__root__ = fix_merge(chain.__root__) # 合并相邻的 Plain 项

  current_start = 0
  current_end = 1
  for index, part in enumerate(signature_array):
    slice_result = chain.__root__[index:index+1]
    if isinstance(part, Normal):
      part: Normal
      if not slice_result: # 不匹配 Normal 就退出.
        return
      if all([isinstance(i, Plain) for i in slice_result]): # 判断是否全部都是 Plain
        match_result = re.match(
          f"^{part.regex_generater()}$",
          "".join([i.toString() for i in slice_result])
        ) # 这种情况就直接判断后者是 Require 还是 Optional 就好了
        if not match_result: # 啊, 或许我们需要改变一下.
          # TODO: Mixined MessageChain create as a parameter
          if index + 1 <= len(signature_array) - 1:
            pass
        else:
          # TODO: 已匹配到的 Normal, 判断之后的是 Require 还是 Optional, 如果是 Optional
          #       那么就根据当前 index 判断当前处理的 Normal 是否需要 Optional.
          pass
      else:
        break

if __name__ == "__main__":
  from mirai import At, AtAll
  from devtools import debug
  debug(chain_split(MessageChain(__root__=[
    Plain("1*2"), At(1), Plain("22*"), AtAll(), Plain("3*2*1")
  ]), "2"))