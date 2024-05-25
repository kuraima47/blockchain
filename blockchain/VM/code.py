import io
import tarfile
import dill as pickle
import os


class Code:
    def __init__(self, module, storage, name, version):
        self.module = module
        self.storage = storage
        self.name = name
        self.version = version

    def extract(self):
        self.module = io.BytesIO(pickle.loads(self.module)) if self.module else None

    def save(self):
        self.module = pickle.dumps(self.module.getvalue())

    @classmethod
    def construct(cls, module_files, python_version):
        module = io.BytesIO()

        with tarfile.open(fileobj=module, mode='w') as tar:
            with open(os.path.join(os.path.dirname(__file__), "Dockerfile"), 'r') as f:
                dockerfile_content = f.read()
            tarinfo = tarfile.TarInfo(name="Dockerfile")
            tarinfo.size = len(dockerfile_content)
            tar.addfile(tarinfo, io.BytesIO(dockerfile_content.encode('utf-8')))

            for filepath, filecontent in module_files.items():
                tarinfo = tarfile.TarInfo(name=f"/contract/{filepath}")
                data = filecontent.encode('utf-8')
                tarinfo.size = len(data)
                tar.addfile(tarinfo, io.BytesIO(data))

        module.seek(0)
        return cls(module.getvalue(), b'', "name", python_version)

