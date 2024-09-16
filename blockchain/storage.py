from .mpt.hash import keccak_hash
from .mpt.mpt import MerklePatriciaTrie


class Storage:
    def __init__(self, storage_root=None, in_memory=False, db_path="DB/"):
        """
        Initialise le stockage avec une instance de MerklePatriciaTrie.

        Parameters:
        ----------
        storage_root : bytes, optional
            Racine actuelle du trie.
        in_memory : bool, optional
            Si True, utilise uniquement le stockage en mémoire.
        db_path : str, optional
            Chemin vers la base de données LevelDB.
        """
        self.current_root = storage_root
        self._in_memory = in_memory
        self.db_path = db_path
        self.trie = MerklePatriciaTrie(
            db_path=self.db_path,
            in_memory=self._in_memory,
            root=self.current_root
        )

    def set_root(self, root, save_previous=False):
        """Définit la racine actuelle du trie."""
        self.current_root = root
        if save_previous:
            self.trie.commit()
        self.trie = MerklePatriciaTrie(
            db_path=self.db_path,
            in_memory=self._in_memory,
            root=self.current_root
        )

    def save(self, data={}):
        """
        Sauvegarde des données dans le trie.

        Parameters:
        ----------
        data : dict
            Paires clé-valeur à sauvegarder.
        """
        self._in_memory = False
        self.current_root = None
        for k, v in data.items():
            self[k] = v
        self.trie.commit()

    def __getitem__(self, key):
        """
        Récupère une valeur associée à une clé.

        Parameters:
        ----------
        key : bytes
            Clé.

        Returns:
        -------
        bytes or None
            Valeur associée à la clé ou None si inexistante.
        """
        return self.trie.get(keccak_hash(key))

    def __setitem__(self, key, value):
        """
        Définit une valeur pour une clé.

        Parameters:
        ----------
        key : bytes
            Clé.
        value : bytes
            Valeur.
        """
        self.trie.update(keccak_hash(key), value)
        self.current_root = self.trie.root_hash()

    def copy(self):
        """
        Crée une copie du stockage.

        Returns:
        -------
        Storage
            Nouvelle instance de Storage avec la même racine.
        """
        new_storage = Storage(
            storage_root=self.current_root,
            in_memory=self._in_memory,
            db_path=self.db_path
        )
        return new_storage

    def commit(self):
        """Commit les changements dans le trie."""
        self.trie.commit()

    def close(self):
        """Ferme proprement le trie."""
        self.trie.close()

    def __repr__(self):
        return f"<{self.__class__.__name__} root={self.current_root}>"