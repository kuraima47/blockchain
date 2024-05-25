import docker

from blockchain.VM.code import Code


class VM:

    def __init__(self, code: Code):
        self.code = code
        self.client = docker.from_env()
        self.tag = "smart_contract"
        self.build_image("./", buildargs={"PYTHON_VERSION": self.code.version})

    def build_image(self, path, buildargs=None):
        response = [line for line in self.client.images.build(fileobj=self.code.module, path=path, tag=self.tag, buildargs=buildargs, rm=True)]
        return response

    def execute(self):
        container = self.client.containers.run(self.tag, detach=True, network="none")
        response = container.wait()
        logs = container.logs().decode("utf-8")

        if response["StatusCode"] == 0:
            print("Execution successful")
            print(logs)
        else:
            print("Execution failed")
            print(logs)

