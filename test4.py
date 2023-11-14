from blockchain.storage import Storage


def test_storage():
    # Créer une instance de la classe Storage
    storage = Storage()

    # Test d'ajout et de récupération
    key, value = b"cle", b"valeur"
    storage[key] = value  # Ajout d'une valeur
    retrieved_value = storage[key]  # Récupération de la valeur
    assert retrieved_value == value, "Erreur lors de la récupération de la valeur après l'ajout."

    # Test de mise à jour
    new_value = b"nouvelle valeur"
    storage[key] = new_value  # Mise à jour de la valeur
    updated_value = storage[key]  # Récupération de la valeur mise à jour

    assert updated_value == new_value, "Erreur lors de la récupération de la valeur après la mise à jour."

    # Test de récupération avec un mauvais clé
    non_existing_key = b'pas une cle'
    non_existing_value = storage[non_existing_key]

    assert non_existing_value is None, "La récupération d'une clé non existante devrait retourner None."

    print("Tous les tests ont réussi !")


def test_storage_with_previous_hash():
    # Créer une instance de la classe Storage
    storage = Storage()

    # Ajouter une valeur et sauvegarder le root hash actuel
    key1, value1 = b"cle1", b"valeur1"
    storage[key1] = value1
    previous_root_hash = storage.current_root

    # Ajouter une autre valeur
    key2, value2 = b"cle2", b"valeur2"
    storage[key2] = value2

    # Récupérer la valeur précédente en utilisant le previous root hash
    retrieved_value_previous = storage[key1, previous_root_hash]
    assert retrieved_value_previous == value1, "Erreur lors de la récupération de la valeur avec le previous root hash."

    # Récupérer la valeur actuelle (devrait échouer avec le previous root hash)
    retrieved_value_current = storage[key2, previous_root_hash]
    assert retrieved_value_current is None, "La récupération avec le previous root hash ne devrait pas trouver de nouvelles clés."


if __name__ == "__main__":
    # Exécuter la fonction de test
    test_storage()
    test_storage_with_previous_hash()
