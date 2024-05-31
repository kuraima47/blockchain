import io
import tarfile
import dill as pickle
import os


class Code:
    def __init__(self, module, storage, name, version):
        self.module = module
        self.storage = storage
        if not self.storage == b'':
            self.add_storage(storage)
        self.name = name
        self.version = version

    def extract(self):
        self.module = io.BytesIO(pickle.loads(self.module)) if self.module else None

    def save(self):
        module_tar = io.BytesIO(self.module)
        with tarfile.open(fileobj=module_tar, mode='r') as tar:
            storage_member = tar.getmember('storage.pkl')
            storage_file = tar.extractfile(storage_member)
            self.storage = storage_file.read() if storage_file else b''

    def add_storage(self, storage):
        self.storage = storage
        module_tar = io.BytesIO(self.module)
        with tarfile.open(fileobj=module_tar, mode='a') as tar:
            storage_content = io.BytesIO(storage)
            tarinfo = tarfile.TarInfo(name="storage.pkl")
            tarinfo.size = len(storage_content.getvalue())
            tar.addfile(tarinfo, storage_content)
        module_tar.seek(0)
        self.module = module_tar.getvalue()

    @classmethod
    def construct(cls, module_files, python_version, storage=b''):
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
        return cls(module.getvalue(), storage, "contract", python_version)
