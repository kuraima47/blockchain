import json

from VM.code import Code
from VM.VM import VM
from compiler.analyse import Analyse

files = Analyse("./compiler/test").get_files()
version = json.loads(files["contract.json"])["py_version"]
code = Code.construct(files, version)
vm = VM(code)
vm.execute()
