import docker

from blockchain.VM.code import Code
from blockchain.compiler.analyse import Analyse


class VM:

    def __init__(self, version):
        self.client = docker.from_env()
        self.tag = "smart_contract"
        self.build_image("./", buildargs={"PYTHON_VERSION": version})
        self.analyser = Analyse()

    def build_image(self, path, code: Code, buildargs=None):
        response = [line for line in self.client.images.build(fileobj=code.module, path=path, tag=self.tag, buildargs=buildargs, rm=True)]
        return response

    def execute(self):
        container = self.client.containers.run(self.tag, detach=True, network="none")
        response = container.wait()
        logs = container.logs().decode("utf-8")
        if response["StatusCode"] == 0:
            self.analyser.analyse(logs)
        else:
            print("Execution failed")
            print(logs)

