import random
import re
import string as const_string
from typing import List
from typing import Optional as Optional_Typing

from devtools import debug
from mirai import MessageChain, Plain

from .entities import Normal, Optional, Require
from .string import (Signature, signature_result_list_generate,
                     signature_sorter, special_rule_regex_generate)
from mirai.misc import printer

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
  return MessageChain(__root__=result)

def chain_split(chain: MessageChain, split_str: str) -> List[MessageChain]:
  chain = fix_merge(chain) # 已经重新生成了一个 MessageChain(以list的形式)
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

def chain_headpop(chain: MessageChain, pop_with: str) -> MessageChain:
  if not chain:
    return
  else:
    if not chain.__root__:
      return
    chain = fix_merge(chain)
  
  length = len(chain)
  pop_with_length = len(pop_with)
  if length >= 1:
    if isinstance(chain[0], Plain):
      if len(chain[0].text) >= pop_with_length and \
         chain[0].text.startswith(pop_with):
        chain[0].text = chain[0].text[pop_with_length:]
        return chain

def chain_regex_match_headpop(chain: MessageChain, pop_with_regex: str) -> MessageChain:
  if not chain:
    return
  else:
    if not chain.__root__:
      return
  
  length = len(chain)
  if length >= 2:
    first_plain = chain.getFirstComponent(Plain)
    if first_plain:
      first_plain_index = chain.__root__.index(first_plain)
      match_result = re.match(pop_with_regex, first_plain.text)
      if match_result:
        chain.__root__[first_plain_index] = Plain(first_plain.text[match_result.end():])
        return chain

def chain_startswith(chain: MessageChain, with_: str) -> bool:
  if not chain:
    return
  else:
    if not chain.__root__:
      return
    chain = fix_merge(chain)
  
  length = len(chain)
  with_length = len(with_)
  if length >= 1:
    if isinstance(chain[0], Plain):
      if len(chain[0].text) >= with_length and \
         chain[0].text.startswith(with_):
        return True
  return False

def chain_contains(chain: MessageChain, string: str) -> bool:
  for component in chain:
    if isinstance(component, Plain):
      if string in Plain.text:
        return True
  else:
    return False

def chain_index(chain: MessageChain, string: str) -> int:
  for index, component in enumerate(chain):
    if isinstance(component, Plain):
      if string in Plain.text:
        return index
  else:
    raise ValueError(f"{string} is not in chain.")


def chain_match(signature: Signature, chain: MessageChain) -> Optional_Typing[dict]:
  if not chain:
    return

  signature.check() # 防止NT行为.

  # 想了想, 还是用 regex 进行匹配, 但是这种方法及其脆弱, 我得想办法加强.
  closure_sign = random.choice("`:;'<?.=") # 内容将由这些字符中的一个替换.(我还在思考该如何避免用户直接输入这些字符然后触发错误)
  replace_sign = random.choice("%&*(]-")
  special_dict = {}
  def special_save(value) -> str:
    key = "".join(random.choices(const_string.ascii_lowercase + const_string.digits, k=7))
    special_dict[key] = value
    return key

  def special_handle_for_raw_string(raw_str) -> str:
    can_replace_able = \
      re.findall(
        f"(?<={re.escape(closure_sign)})([a-z0-9]*)(?={re.escape(closure_sign)})",
        raw_str
      )
    plains = [i for i in re.split(
      f"{re.escape(closure_sign)}[a-z0-9]*?{re.escape(closure_sign)}",
      raw_str
    ) if i]
    
    return [
      (Plain(
        unbound_str\
          .replace(f"\\{replace_sign}", closure_sign)
          .replace(f"\\{closure_sign}", replace_sign)
      ) if way == "plain" else
        special_dict[unbound_str]
      )\
      for index, unbound_str, way in sorted([
        *[(raw_str.index(i), i, "special") for i in can_replace_able if i],
        *[(raw_str.index(i), i, "plain") for i in plains]
      ], key=lambda x: x[0])
    ]

  translated_string = "".join([
    # 先将原有的, 与 closure_sign 使用相同的字符附上转义, 然后把 closure_sign 转为 replace_sign.
    # 返回来就要把之前转义的 closure_sign 的转义去除, 使其字面量一致.
    re.sub(
      f"(?!\\\\){closure_sign}", replace_sign,
      component.text\
        .replace(closure_sign, f"\\{re.escape(closure_sign)}")
        .replace(replace_sign, f"\\{re.escape(replace_sign)}") # 把原有的加上转义
    )\
    if isinstance(component, Plain)\
      else f"{closure_sign}{special_save(component)}{closure_sign}" \
    for component in chain
  ])
  matched_result = signature.parse(translated_string)
  return (matched_result, special_handle_for_raw_string) if matched_result else None

if __name__ == "__main__":
  from mirai import At
  from devtools import debug
  signature = Signature("匹配魔法!<magic:toString>,向<target:assert('1846913566' in ComponentSets('at'))>发出!")
  debug(signature_result_list_generate(signature_sorter("匹配魔法!<magic:toString>,向<target:assert('1846913566' in ComponentSets('at'))>发出!")))
  chain = MessageChain(__root__=[
    Plain("匹配魔法!rm<*-rf/<,向543"), At(123), At(1846913566), Plain("发出!")
  ])
  debug(chain_match(signature, chain))