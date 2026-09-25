# Aegis Health Coverage : prédiction des frais médicaux

**Application en ligne : [projetmachinelearning-aegis-insurance.streamlit.app](https://projetmachinelearning-aegis-insurance.streamlit.app/)**

Projet réalisé en binôme dans le cadre de la formation Data Analyst de Simplon Lyon (brief Régression).

## Contexte

NexaData Consulting accompagne **Aegis Health Coverage**, un assureur santé qui souhaite comprendre ce qui fait varier les frais médicaux de ses assurés, afin d'ajuster ses primes au profil de chaque client.

L'objectif du projet :

- analyser l'impact de l'âge, de l'IMC, du tabagisme, du nombre d'enfants et de la région sur les frais médicaux ;
- entraîner et comparer plusieurs modèles de régression pour prédire ces frais ;
- restituer les résultats dans une application Streamlit, avec un simulateur d'estimation en direct.

## Le dataset

`insurance-data.csv` : 1 338 assurés américains (1 337 après suppression d'un doublon), 7 colonnes.

| Variable | Description |
|---|---|
| `age` | Âge de l'assuré (18 à 64 ans) |
| `sex` | Sexe |
| `bmi` | Indice de masse corporelle (IMC) |
| `children` | Nombre d'enfants couverts par l'assurance |
| `smoker` | Fumeur ou non |
| `region` | Région de résidence aux États-Unis (4 régions) |
| `expenses` | **Frais médicaux annuels en dollars (variable cible)** |

## Démarche

Le notebook `notebook/Aegis_Insurance_Analyse.ipynb` suit les étapes d'un projet de Machine Learning supervisé :

1. **Exploration des données** : types, valeurs manquantes (aucune), doublons (un supprimé), statistiques descriptives, visualisations et matrice de corrélation.
2. **Prétraitement** : One-Hot Encoding pour `region` (variable sans ordre), encodage binaire pour `sex` et `smoker`.
3. **Division** des données en jeu d'entraînement (80 %) et de test (20 %).
4. **Standardisation** de `age`, `bmi` et `children`, ajustée uniquement sur le jeu d'entraînement pour éviter toute fuite de données. Pour le SVR, la cible est aussi standardisée, puis remise en dollars après la prédiction.
5. **Entraînement de 5 modèles** : régression linéaire, KNN, arbre de décision, Random Forest et SVR.
6. **Interprétation** : coefficients, importance des variables, voisins du KNN, points de support du SVR.
7. **Évaluation** avec la MSE, la MAE et le R².
8. **Sauvegarde** du modèle retenu avec `joblib` pour l'application.

## Résultats

| Modèle | MAE | R² |
|---|---|---|
| **Random Forest** | **2 562 $** | **0,88** |
| Régression linéaire | 4 177 $ | 0,81 |
| Arbre de décision | 2 961 $ | 0,78 |
| SVR | 4 606 $ | 0,68 |
| KNN | 4 737 $ | 0,61 |

Le **Random Forest** est retenu : il explique 88 % de la variance des frais et se trompe en moyenne de 2 562 $. En combinant plusieurs arbres, il capte les effets croisés entre variables, notamment le tabagisme associé à l'âge et à l'obésité.

Le **tabagisme** est de loin le facteur le plus déterminant, suivi de l'âge et de l'IMC. Le sexe, le nombre d'enfants et la région ont un impact très faible.

## L'application Streamlit

- **Accueil** : le contexte, le message clé du projet et la présentation des données.
- **Analyse** : graphiques interactifs (distribution des frais avec filtres, comparaison par variable, effet de l'âge et de l'IMC selon le statut fumeur, matrice de corrélation).
- **Simulateur** : saisie d'un profil (âge, sexe, taille et poids, enfants, fumeur, région) et estimation en direct des frais annuels, avec la marge d'erreur du modèle et l'effet du tabac pour ce profil.

## Structure du repo

```
Projet-Aegis-Insurance/
├── .streamlit/
│   └── config.toml              # thème de l'application
├── data/
│   └── insurance-data.csv
├── notebook/
│   └── Aegis_Insurance_Analyse.ipynb
├── streamlit/
│   ├── Accueil.py               # page principale
│   ├── pages/
│   │   ├── 1_Analyse.py
│   │   └── 2_Simulateur.py
│   ├── modules/
│   │   └── chargement.py        # chargement des données et du modèle
│   └── model/
│       ├── modele_random_forest.joblib
│       └── colonnes_modele.joblib
├── requirements.txt
└── README.md
```

## Technologies

Python, pandas, NumPy, scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit, joblib.

## Équipe

Ludivine Thinet et Laurie Shillingford, formation Data Analyst, Simplon Lyon. 