from ptilopsis import Ptilopsis
from devtools import debug

splited = Ptilopsis.signature_spliter("test <xxx:sss,fa> [xx:ss]")
data = Ptilopsis.signature_sorter("test <xxx:sss,fa> [xx:ss]")
print(Ptilopsis.union_handle("test <xxx:sss,fa> [xx:ss]", 9))
print(splited)
debug(data)