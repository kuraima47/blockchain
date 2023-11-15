from blockchain.storage import Storage


def test_storage():

    storage = Storage()
    key, value = b"cle", b"valeur"
    storage[key] = value
    retrieved_value = storage[key]

    assert retrieved_value == value, "Erreur lors de la récupération de la valeur après l'ajout."

    new_value = b"nouvelle valeur"
    storage[key] = new_value
    updated_value = storage[key]

    assert updated_value == new_value, "Erreur lors de la récupération de la valeur après la mise à jour."
    non_existing_key = b'pas une cle'
    non_existing_value = storage[non_existing_key]

    assert non_existing_value is None, "La récupération d'une clé non existante devrait retourner None."

    print("Tous les tests ont réussi !")


def test_storage_with_previous_hash():
    storage = Storage()
    key1, value1 = b"cle1", b"valeur1"
    storage[key1] = value1
    previous_root_hash = storage.current_root

    key2, value2 = b"cle2", b"valeur2"
    storage[key2] = value2
    storage.set_root(previous_root_hash)

    retrieved_value_previous = storage[key1]
    assert retrieved_value_previous == value1, "Erreur lors de la récupération de la valeur avec le previous root hash."

    retrieved_value_current = storage[key2]
    assert retrieved_value_current is None, "La récupération avec le previous root hash ne devrait pas trouver de nouvelles clés."

    print("Tous les tests ont réussi 2 !")


if __name__ == "__main__":
    test_storage()
    test_storage_with_previous_hash()
