import pandas as pd
import streamlit as st

from modules.chargement import charger_donnees, charger_modele

st.set_page_config(page_title="Simulateur | Aegis", page_icon="🩺", layout="wide")

df_insurance = charger_donnees()
modele, colonnes_modele = charger_modele()

# Erreur absolue moyenne (MAE) du Random Forest sur le jeu de test
# (valeur issue du notebook, Étape 8)
MAE_MODELE = 2562

REGIONS = {
    "northeast": "Nord-Est",
    "northwest": "Nord-Ouest",
    "southeast": "Sud-Est",
    "southwest": "Sud-Ouest",
}

# Limites observées dans le dataset : en dehors, le modèle n'a jamais vu de cas
IMC_MIN, IMC_MAX = df_insurance["bmi"].min(), df_insurance["bmi"].max()


def format_nombre(valeur, decimales=0):
    """Nombre au format français : espace pour les milliers, virgule décimale."""
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


def categorie_imc(imc):
    if imc < 18.5:
        return "insuffisance pondérale"
    if imc < 25:
        return "corpulence normale"
    if imc < 30:
        return "surpoids"
    return "obésité"


def construire_profil(age, sexe, imc, enfants, fumeur, region):
    """Transforme la saisie en une ligne identique aux données d'entraînement :
    même encodage que le notebook et colonnes dans le même ordre."""
    profil = {
        "age": age,
        "sex": 1 if sexe == "Homme" else 0,          # LabelEncoder : female = 0, male = 1
        "bmi": imc,
        "children": enfants,
        "smoker": 1 if fumeur == "Oui" else 0,       # LabelEncoder : no = 0, yes = 1
    }
    for code_region in REGIONS:                       # One-Hot : une colonne 0/1 par région
        profil[f"region_{code_region}"] = 1 if region == code_region else 0

    return pd.DataFrame([profil])[colonnes_modele]


# ---------- Style ----------
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');
.si-titre {
  font-family: 'Source Serif 4', Georgia, serif; font-weight: 700;
  font-size: clamp(1.8rem, 3.5vw, 2.5rem); color: #17324D; margin: 0.5rem 0 0.4rem;
}
.si-intro { color: #52606B; font-size: 1.02rem; max-width: 720px; margin: 0; }
.si-resultat-nom { color: #52606B; font-size: 0.98rem; margin: 0; }
.si-resultat-valeur {
  font-family: 'Source Serif 4', Georgia, serif; font-weight: 700;
  font-size: clamp(2.6rem, 5vw, 3.6rem); color: #17324D; line-height: 1.1; margin: 0.2rem 0 0.4rem;
}
.si-fourchette { color: #1E2A33; font-size: 0.98rem; margin: 0 0 1.2rem; }
.si-fourchette span { color: #52606B; }
.si-bloc { border-top: 1px solid #CBD7D0; padding-top: 1rem; margin-top: 1rem; }
.si-bloc h3 { font-size: 1.05rem; font-weight: 600; color: #17324D; margin: 0 0 0.6rem; padding: 0; }
.si-bloc p { margin: 0; color: #1E2A33; line-height: 1.55; }
.si-barres { display: grid; gap: 0.5rem; margin: 0.4rem 0 0.8rem; }
.si-ligne { display: grid; grid-template-columns: 8.5rem 1fr; align-items: center; gap: 0.6rem; }
.si-ligne-nom { font-size: 0.92rem; color: #52606B; }
.si-barre {
  height: 1.9rem; border-radius: 3px; display: flex; align-items: center; justify-content: flex-end;
  padding: 0 0.6rem; color: #fff; font-weight: 600; font-size: 0.9rem; min-width: fit-content;
}
.si-fumeur { background: #C0504D; }
.si-non-fumeur { background: #4F81BD; }
.si-note { color: #52606B; font-size: 0.85rem; margin-top: 1.4rem; }
</style>
<h1 class="si-titre">Estimer les frais médicaux d'un assuré</h1>
<p class="si-intro">Renseignez le profil : l'estimation se met à jour automatiquement.</p>
"""
)

st.write("")
col_formulaire, col_resultat = st.columns([1, 1.25], gap="large")

# =====================================================================
# Formulaire
# =====================================================================
with col_formulaire.container(border=True):
    age = st.slider("Âge", min_value=18, max_value=64, value=35)

    sexe = st.radio("Sexe", ["Femme", "Homme"], horizontal=True)

    col_taille, col_poids = st.columns(2)
    taille_cm = col_taille.number_input("Taille (cm)", min_value=140, max_value=210, value=170, step=1)
    poids_kg = col_poids.number_input("Poids (kg)", min_value=35, max_value=200, value=70, step=1)

    imc = poids_kg / (taille_cm / 100) ** 2
    st.caption(f"IMC calculé : **{format_nombre(imc, 1)}**, {categorie_imc(imc)}")

    enfants = st.selectbox("Nombre d'enfants couverts", options=[0, 1, 2, 3, 4, 5])

    fumeur = st.radio("Fumeur", ["Non", "Oui"], horizontal=True)

    region = st.selectbox(
        "Région de résidence",
        options=list(REGIONS),
        format_func=lambda code: REGIONS[code],
    )

# L'IMC saisi sort de ce que le modèle a appris : on le borne et on prévient
if not IMC_MIN <= imc <= IMC_MAX:
    imc_modele = min(max(imc, IMC_MIN), IMC_MAX)
    col_formulaire.warning(
        f"Cet IMC sort de la plage des données d'entraînement "
        f"({format_nombre(IMC_MIN, 1)} à {format_nombre(IMC_MAX, 1)}). "
        f"L'estimation utilise la valeur la plus proche ({format_nombre(imc_modele, 1)})."
    )
else:
    imc_modele = imc

# =====================================================================
# Prédictions
# =====================================================================
profil = construire_profil(age, sexe, imc_modele, enfants, fumeur, region)
frais_estimes = modele.predict(profil)[0]

# Même profil avec le statut fumeur inversé, pour mesurer l'effet du tabac
fumeur_inverse = "Non" if fumeur == "Oui" else "Oui"
profil_inverse = construire_profil(age, sexe, imc_modele, enfants, fumeur_inverse, region)
frais_inverse = modele.predict(profil_inverse)[0]

frais_fumeur = frais_estimes if fumeur == "Oui" else frais_inverse
frais_non_fumeur = frais_inverse if fumeur == "Oui" else frais_estimes
ecart_tabac = frais_fumeur - frais_non_fumeur

mediane = df_insurance["expenses"].median()
rapport_mediane = frais_estimes / mediane
if rapport_mediane >= 1:
    phrase_mediane = f"{format_nombre(rapport_mediane, 1)} fois la médiane des assurés"
else:
    phrase_mediane = f"{format_nombre((1 - rapport_mediane) * 100)} % de moins que la médiane des assurés"

if fumeur == "Oui":
    phrase_tabac = (
        f"Sans le tabac, ce même profil coûterait environ <strong>{format_nombre(frais_non_fumeur)}&nbsp;$</strong> "
        f"par an, soit {format_nombre(ecart_tabac)}&nbsp;$ de moins."
    )
else:
    phrase_tabac = (
        f"Si cette personne fumait, ses frais estimés passeraient à environ "
        f"<strong>{format_nombre(frais_fumeur)}&nbsp;$</strong> par an, soit {format_nombre(ecart_tabac)}&nbsp;$ de plus."
    )

# Largeur des barres : la plus grande valeur sert de référence (100 %)
valeur_max = max(frais_fumeur, frais_non_fumeur)
largeur_fumeur = frais_fumeur / valeur_max * 100
largeur_non_fumeur = frais_non_fumeur / valeur_max * 100

borne_basse = max(frais_estimes - MAE_MODELE, 0)
borne_haute = frais_estimes + MAE_MODELE

# =====================================================================
# Résultat
# =====================================================================
with col_resultat:
    st.html(
        f"""
<p class="si-resultat-nom">Frais médicaux estimés sur un an</p>
<div class="si-resultat-valeur">{format_nombre(frais_estimes)}&nbsp;$</div>
<p class="si-fourchette">
  Entre {format_nombre(borne_basse)}&nbsp;$ et {format_nombre(borne_haute)}&nbsp;$
  <span>(le modèle se trompe en moyenne de {format_nombre(MAE_MODELE)}&nbsp;$)</span>
</p>

<div class="si-bloc">
  <h3>Par rapport aux autres assurés</h3>
  <p>C'est {phrase_mediane} ({format_nombre(mediane)}&nbsp;$).</p>
</div>

<div class="si-bloc">
  <h3>L'effet du tabac pour ce profil</h3>
  <div class="si-barres" role="img"
       aria-label="Non-fumeur : {format_nombre(frais_non_fumeur)} dollars, fumeur : {format_nombre(frais_fumeur)} dollars">
    <div class="si-ligne">
      <span class="si-ligne-nom">En non-fumeur</span>
      <div class="si-barre si-non-fumeur" style="width: {largeur_non_fumeur:.1f}%">{format_nombre(frais_non_fumeur)}&nbsp;$</div>
    </div>
    <div class="si-ligne">
      <span class="si-ligne-nom">En fumeur</span>
      <div class="si-barre si-fumeur" style="width: {largeur_fumeur:.1f}%">{format_nombre(frais_fumeur)}&nbsp;$</div>
    </div>
  </div>
  <p>{phrase_tabac}</p>
</div>

<p class="si-note">
  Estimation indicative, calculée par un modèle Random Forest entraîné sur
  {format_nombre(len(df_insurance))} assurés américains.
</p>
"""
    )