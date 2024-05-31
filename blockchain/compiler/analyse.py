

class Analyse:

    def __init__(self):
        self.files = {}
        self.analyse()

    def analyse(self, logs=""):
        for line in logs.split("\n"):
            if "File" in line:
                self.files[line.split(" ")[1].strip()] = line.split(" : ")[2].strip()

    def get_files(self):
        return self.files

    def __repr__(self):
        return f"<{self.__class__.__name__} files={len(self.files)}>"
