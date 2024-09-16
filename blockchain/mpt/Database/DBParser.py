import json
import os

class DBParser(dict):
    def __init__(self, db_path="DB/", on_dump=False):
        """
        Initialise le parser de base de données avec JSON.

        Parameters:
        ----------
        db_path : str
            Chemin vers le répertoire contenant les fichiers JSON.
        on_dump : bool
            Si True, les changements sont écrits immédiatement.
        """
        # get absolute path to the database
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        self.cache = {}
        self.on_dump = on_dump
        self.root = None
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        self.load()

        super().__init__()

    def __setitem__(self, key, value):
        """
        Définit une valeur dans la base de données.

        Parameters:
        ----------
        key : str ou bytes
            La clé sous forme de chaîne ou de bytes.
        value : str, bytes ou tout type sérialisable en JSON
            La valeur associée à la clé.
        """
        # Convertir les bytes en hexadécimal pour le stockage
        if isinstance(key, bytes):
            key = key.hex()
        if isinstance(value, bytes):
            value = value.hex()
        super(DBParser, self).__setitem__(key, value)
        self.cache[key] = value

    def __getitem__(self, key):
        """
        Récupère une valeur de la base de données.

        Parameters:
        ----------
        key : str ou bytes
            La clé sous forme de chaîne ou de bytes.

        Returns:
        -------
        tout type sérialisable en JSON
            La valeur associée à la clé.

        Raises:
        ------
        KeyError
            Si la clé n'existe pas.
        """
        if isinstance(key, bytes):
            key = key.hex()
        if key in self.cache:
            value = self.cache[key]
            return bytes.fromhex(value)
        if key in self:
            value = super(DBParser, self).__getitem__(key)
            return bytes.fromhex(value)
        raise KeyError(f"Key {key} not found.")

    def load(self):
        """
        Charge les données de tous les fichiers JSON dans le répertoire spécifié.
        """
        for file in os.listdir(self.db_path):
            if file.endswith('.json'):
                with open(os.path.join(self.db_path, file), 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        # Décoder les clés et valeurs hexadécimales en bytes
                        try:
                            k = bytes.fromhex(k)
                        except ValueError:
                            pass
                        try:
                            v = bytes.fromhex(v)
                        except ValueError:
                            pass
                        self[k] = v

    def dump(self):
        """
        Sauvegarde les changements du cache dans des fichiers JSON.
        """
        data = {key: value for key, value in self.cache.items()}
        file_path = os.path.join(self.db_path, f"{self.root.hex()}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        self.cache.clear()

    def commit(self):
        if self.on_dump:
            self.dump()

    def close(self):
        """
        Méthode de fermeture (placeholder pour la compatibilité).
        """
        pass
