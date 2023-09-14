def calculer_imc(poids_kg, taille_m):
    """
    Calcule l'Indice de Masse Corporelle (IMC).

    :param poids_kg: Poids en kilogrammes
    :param taille_m: Taille en mètres
    :return: IMC
    """
    if taille_m == 0:
        return "La taille ne peut pas être zéro."

    imc = poids_kg / (taille_m**2)
    return imc


# Exemple d'utilisation
poids = 80  # en kg
taille = 1.79  # en mètres

imc = calculer_imc(poids, taille)
print(f"Votre IMC est : {imc}")
