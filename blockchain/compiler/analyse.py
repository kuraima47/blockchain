import os


# le but est de construire un fichier {"relative_path": "bytes of code"} pour chaque fichier sans oublier les sous-dossiers et les fichiers dans les sous-dossiers en fonction d'un dossier racine
class Analyse:

    def __init__(self, path):
        self.path = path
        self.files = {}
        self.analyse()

    def analyse(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                with open(os.path.join(root, file), "rb") as f:
                    self.files[os.path.relpath(os.path.join(root, file), self.path)] = f.read().decode("utf-8")

    def get_files(self):
        return self.files

    def __repr__(self):
        return f"<{self.__class__.__name__} path={self.path} files={len(self.files)}>"
