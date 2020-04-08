from ptilopsis.string import signature_sorter, signature_result_list_generate
from ptilopsis.entities import Normal, Require, Optional
from devtools import debug

signature = "指令1 <arg1> <arg2>"
sorted_data = signature_sorter(signature)
regex_generater_list = signature_result_list_generate(sorted_data)

debug(regex_generater_list)
signature = "指令1 <arg1> <arg2>"
# 现在我可以通过 signature 生成如下的对象:
[
    Normal("指令1"),
    Require(name="arg1", flags=None),
    Normal(" "),
    Require(name="arg2", flags=None),
]
# 我想让这玩意匹配.
[
    {
        "type": "Plain",
        "text": "指令1 "
    },
    {
        "type": "At",
        "target": 1846913566
    },
    {
        "type": "Plain", "text": " balabala"
    },
    {
        "type": "At", "target": 208924405
    }
]
# 解析出来的结果大概是这样:
{
    "arg1": [{
        "type": "At", "target": 1846913566
    }],
    "arg2": [{
        "type": "Plain", "text": "balabala"
    }, {
        "type": "At", "target": 208924405
    }]
}