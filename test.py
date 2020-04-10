from ptilopsis.string import signature_sorter, signature_result_list_generate
from ptilopsis.entities import Normal, Require, Optional
from devtools import debug

signature = "指令1 <arg1> 1[arg2]"
sorted_data = signature_sorter(signature)
regex_generater_list = signature_result_list_generate(sorted_data)

debug(regex_generater_list)