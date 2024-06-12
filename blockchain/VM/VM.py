import docker
import os
import io
import tarfile


class VM:
    def __init__(self, code):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            raise docker.errors.DockerException(f"Failed to connect to Docker daemon: {e}.")

        self.tag = f"smart_contract_{code.version}"
        self.code = code
        dockerfile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Docker"))
        if not os.path.isdir(dockerfile_path):
            raise FileNotFoundError(f"The directory {dockerfile_path} does not exist.")
        self.build_image(dockerfile_path, buildargs={"PYTHON_VERSION": self.code.version})

    def build_image(self, path, buildargs=None):
        try:
            image, build_logs = self.client.images.build(
                path=path,
                dockerfile="Dockerfile",
                tag=self.tag,
                buildargs=buildargs,
                rm=True,
            )
        except docker.errors.BuildError as e:
            print(f"Build log: {e.build_log}")
            raise docker.errors.BuildError(e.msg, e.build_log)
        except docker.errors.APIError as e:
            raise docker.errors.APIError(f"Docker API error occurred: {e}.")

    def execute(self):
        container = self.client.containers.run(self.tag, detach=True, tty=True, stream=True, stdout=True, stderr=True)
        for filepath, filecontent in self.code.module.items():
            self._add_file_to_container(container, f"contract/{filepath}", filecontent)
        self._add_file_to_container(container, "smart_contract.py")
        try:
            container.exec_run("pip3 install --no-cache-dir --no-compile -r /contract/requirements.txt", stream=True, stdout=True, stderr=True)
            result = container.exec_run("python3 smart_contract.py")
            print(result.output.decode("utf-8"))
            container.stop()
            container.remove()
        except docker.errors.APIError as e:
            print(f"Error during container execution: {e}")

    def _add_file_to_container(self, container, filepath, filecontent=None):
        module = io.BytesIO()
        with tarfile.open(fileobj=module, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=f"/app/{filepath}")
            if filecontent is None:
                with open(os.path.join(os.path.dirname(__file__), filepath), "rb") as f:
                    data = f.read()
            else:
                data = filecontent.encode('utf-8')
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data))
        container.put_archive("/", module.getvalue())
