import os

#Contract Analyser can add files rules foreach file
class AnalyseContract:

    def __init__(self, path: str):
        self.path = path
        self.files = {}
        self.analyse()

    def analyse(self) -> None:
        for root, _, files in os.walk(self.path):
            for file in files:
                with open(os.path.join(root, file), "rb") as f:
                    if not "__pycache__" in os.path.relpath(os.path.join(root, file), self.path).replace("\\", "/"):
                        self.files[os.path.relpath(os.path.join(root, file), self.path).replace("\\", "/")] = f.read().decode("utf-8")

    def get_files(self) -> dict:
        return self.files

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} files={len(self.files)}>"
