from ptilopsis import Ptilopsis
from ptilopsis.string import parse, compile
from devtools import debug

string = "test <xxx:int> [xx:ss]"
will_to_parse = "test 123 ar$wq34"
debug(compile(string).parse(will_to_parse))