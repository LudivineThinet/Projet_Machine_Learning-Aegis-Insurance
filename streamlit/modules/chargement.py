from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# Chemins calculés à partir de l'emplacement de ce fichier :
# chargement.py -> modules/ -> streamlit/ -> racine du repo
DOSSIER_STREAMLIT = Path(__file__).resolve().parents[1]
RACINE = DOSSIER_STREAMLIT.parent

CHEMIN_DONNEES = RACINE / "data" / "insurance-data.csv"
CHEMIN_MODELE = DOSSIER_STREAMLIT / "model" / "modele_random_forest.joblib"
CHEMIN_COLONNES = DOSSIER_STREAMLIT / "model" / "colonnes_modele.joblib"


@st.cache_data
def charger_donnees():
    """Charge le dataset une seule fois (doublon retiré, comme dans le notebook)."""
    df_insurance = pd.read_csv(CHEMIN_DONNEES).drop_duplicates()
    return df_insurance


@st.cache_resource
def charger_modele():
    """Charge le Random Forest entraîné et l'ordre des colonnes attendu."""
    modele = joblib.load(CHEMIN_MODELE)
    colonnes = joblib.load(CHEMIN_COLONNES)
    return modele, colonnes