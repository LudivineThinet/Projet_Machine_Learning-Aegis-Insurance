from pathlib import Path

import pandas as pd
import streamlit as st

# Chemin vers la racine du repo, calculé à partir de l'emplacement de ce fichier :
# chargement.py -> modules/ -> streamlit/ -> racine du repo
RACINE = Path(__file__).resolve().parents[2]
CHEMIN_DONNEES = RACINE / "data" / "insurance-data.csv"


@st.cache_data
def charger_donnees():
    """Charge le dataset brut une seule fois, puis le garde en cache."""
    df_insurance = pd.read_csv(CHEMIN_DONNEES)
    return df_insurance