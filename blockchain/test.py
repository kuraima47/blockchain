import json

from VM.code import Code
from VM.VM import VM
from compiler.analysecontract import AnalyseContract

files = AnalyseContract("./compiler/test").get_files()
version = json.loads(files["contract.json"])["py_version"]
code = Code.construct(files, version)
vm = VM(code, "main", [1, 2, 3])
vm.execute()
