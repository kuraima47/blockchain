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

    def save(self):
        pass

    def add_storage(self, storage):
        self.storage = storage
        self.module["storage.pkg"] = storage

    @classmethod
    def construct(cls, module_files, python_version, storage=b''):
        return cls(module_files, storage, "contract", python_version)
