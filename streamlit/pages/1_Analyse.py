import pandas as pd
import plotly.express as px
import streamlit as st

from modules.chargement import charger_donnees

st.set_page_config(page_title="Analyse | Aegis", page_icon="🩺", layout="wide")

df_insurance = charger_donnees()

# Copie pour l'affichage : valeurs traduites en français, children en texte
# (pour que Plotly le traite comme une catégorie et non comme un nombre)
df_affichage = df_insurance.copy()
df_affichage["smoker"] = df_affichage["smoker"].map({"yes": "Oui", "no": "Non"})
df_affichage["sex"] = df_affichage["sex"].map({"male": "Homme", "female": "Femme"})
df_affichage["children"] = df_affichage["children"].astype(str)

# Noms lisibles des colonnes dans les graphiques
LIBELLES = {
    "age": "Âge",
    "sex": "Sexe",
    "bmi": "IMC",
    "children": "Nombre d'enfants",
    "smoker": "Fumeur",
    "region": "Région",
    "expenses": "Frais médicaux ($)",
}

# Mêmes couleurs fumeur / non-fumeur dans tous les graphiques
COULEURS_FUMEUR = {"Oui": "#C0504D", "Non": "#4F81BD"}


def format_dollars(valeur):
    """Montant lisible, pour st.metric (pas de Markdown)."""
    return f"{valeur:,.0f} $".replace(",", " ")


def format_dollars_md(valeur):
    """Même chose pour st.markdown : le $ doit être échappé,
    sinon Markdown le prend pour le début d'une formule mathématique."""
    return format_dollars(valeur).replace("$", "\\$")


# Nom lisible d'un groupe selon la variable comparée
def nom_groupe(variable, valeur):
    if variable == "children":
        return f"les assurés avec {valeur} enfant(s)"
    if variable == "smoker":
        return "les fumeurs" if valeur == "Oui" else "les non-fumeurs"
    if variable == "sex":
        return "les hommes" if valeur == "Homme" else "les femmes"
    return f"la région {valeur}"


st.title("Analyse des frais médicaux")
st.markdown(
    "Tous les graphiques sont interactifs : survolez pour voir les valeurs, "
    "zoomez avec la souris, et cliquez sur la légende pour masquer une catégorie."
)

# =====================================================================
# 1. Distribution des frais
# =====================================================================
st.header("Comment se répartissent les frais médicaux ?")

col_fumeur, col_sexe, col_region = st.columns(3)

choix_fumeur = col_fumeur.multiselect(
    "Fumeur", options=["Oui", "Non"], default=["Oui", "Non"]
)
choix_sexe = col_sexe.multiselect(
    "Sexe", options=["Femme", "Homme"], default=["Femme", "Homme"]
)
liste_regions = sorted(df_affichage["region"].unique())
choix_region = col_region.multiselect(
    "Région", options=liste_regions, default=liste_regions
)

df_filtre = df_affichage[
    df_affichage["smoker"].isin(choix_fumeur)
    & df_affichage["sex"].isin(choix_sexe)
    & df_affichage["region"].isin(choix_region)
]

if df_filtre.empty:
    st.warning("Aucun assuré ne correspond à ces filtres. Sélectionnez au moins une valeur par filtre.")
else:
    mediane_filtre = df_filtre["expenses"].median()
    moyenne_filtre = df_filtre["expenses"].mean()

    fig_distribution = px.histogram(
        df_filtre, x="expenses", nbins=40, labels=LIBELLES
    )
    fig_distribution.update_layout(yaxis_title="Nombre d'assurés", bargap=0.05)
    fig_distribution.add_vline(
        x=mediane_filtre, line_dash="dash", annotation_text="Médiane"
    )
    st.plotly_chart(fig_distribution)

    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("Assurés sélectionnés", len(df_filtre))
    col_2.metric("Frais médians", format_dollars(mediane_filtre))
    col_3.metric("Frais moyens", format_dollars(moyenne_filtre))

mediane_totale = df_insurance["expenses"].median()
moyenne_totale = df_insurance["expenses"].mean()
st.markdown(
    f"Sur l'ensemble des assurés, la moyenne (**{format_dollars_md(moyenne_totale)}**) "
    f"est nettement au-dessus de la médiane (**{format_dollars_md(mediane_totale)}**). "
    "La distribution est donc **asymétrique** : la plupart des assurés ont des frais "
    "modérés, mais quelques profils aux frais très élevés tirent la moyenne vers le haut."
)

# =====================================================================
# 2. Frais selon une variable
# =====================================================================
st.header("Quels profils coûtent le plus cher ?")

variable_choisie = st.selectbox(
    "Variable à comparer",
    options=["smoker", "sex", "region", "children"],
    format_func=lambda colonne: LIBELLES[colonne],
)

fig_boxplot = px.box(
    df_affichage,
    x=variable_choisie,
    y="expenses",
    color=variable_choisie,
    labels=LIBELLES,
    category_orders={"children": [str(n) for n in range(6)]},
    color_discrete_map=COULEURS_FUMEUR if variable_choisie == "smoker" else None,
)
fig_boxplot.update_layout(showlegend=False)
st.plotly_chart(fig_boxplot)

medianes_par_groupe = df_affichage.groupby(variable_choisie)["expenses"].median()
groupe_max = medianes_par_groupe.idxmax()
groupe_min = medianes_par_groupe.idxmin()
ecart = medianes_par_groupe.max() / medianes_par_groupe.min()

st.markdown(
    f"Les frais médians les plus élevés concernent **{nom_groupe(variable_choisie, groupe_max)}** "
    f"({format_dollars_md(medianes_par_groupe.max())}), les plus bas "
    f"**{nom_groupe(variable_choisie, groupe_min)}** ({format_dollars_md(medianes_par_groupe.min())}), "
    f"soit un rapport de **x{ecart:.1f}** entre les deux."
)

# =====================================================================
# 3. Relations avec l'âge et l'IMC
# =====================================================================
st.header("Comment l'âge et l'IMC influencent-ils les frais ?")

variable_x = st.radio(
    "Variable en abscisse",
    options=["age", "bmi"],
    format_func=lambda colonne: LIBELLES[colonne],
    horizontal=True,
)

fig_nuage = px.scatter(
    df_affichage,
    x=variable_x,
    y="expenses",
    color="smoker",
    color_discrete_map=COULEURS_FUMEUR,
    opacity=0.7,
    labels=LIBELLES,
)
st.plotly_chart(fig_nuage)

if variable_x == "age":
    st.markdown(
        "Les frais **augmentent avec l'âge** pour tout le monde, mais les points "
        "forment des bandes séparées : les **non-fumeurs** en bas, les **fumeurs** "
        "nettement au-dessus. À âge égal, être fumeur change complètement le niveau de frais."
    )
else:
    fumeurs = df_insurance[df_insurance["smoker"] == "yes"]
    mediane_fumeurs_obeses = fumeurs.loc[fumeurs["bmi"] >= 30, "expenses"].median()
    mediane_fumeurs_non_obeses = fumeurs.loc[fumeurs["bmi"] < 30, "expenses"].median()
    st.markdown(
        "Chez les non-fumeurs, l'IMC a peu d'effet visible sur les frais. Chez les "
        "fumeurs en revanche, on voit une **cassure autour d'un IMC de 30** (seuil de "
        f"l'obésité) : la médiane passe de **{format_dollars_md(mediane_fumeurs_non_obeses)}** "
        f"sous ce seuil à **{format_dollars_md(mediane_fumeurs_obeses)}** au-dessus. "
        "C'est la **combinaison** tabac + obésité qui fait exploser les frais."
    )

# =====================================================================
# 4. Matrice de corrélation
# =====================================================================
st.header("Quelles variables sont liées entre elles ?")

# La corrélation ne se calcule que sur des nombres : on encode les variables
# catégorielles dans une copie dédiée (le dataset d'origine n'est pas modifié)
df_correlation = df_insurance.copy()
df_correlation["sex"] = df_correlation["sex"].map({"male": 1, "female": 0})
df_correlation["smoker"] = df_correlation["smoker"].map({"yes": 1, "no": 0})
df_correlation = pd.get_dummies(df_correlation, columns=["region"], dtype=int)

matrice_correlation = df_correlation.corr()

fig_correlation = px.imshow(
    matrice_correlation,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    aspect="auto",
)
fig_correlation.update_layout(height=600)
st.plotly_chart(fig_correlation)

correlations_cible = (
    matrice_correlation["expenses"].drop("expenses").sort_values(ascending=False)
)
top_1, top_2, top_3 = correlations_cible.index[:3]

st.markdown(
    "Pour pouvoir calculer les corrélations, les variables catégorielles ont été "
    "encodées : **Homme = 1**, **Fumeur = 1**, et une colonne 0/1 par région."
)
st.markdown(
    f"Les variables les plus corrélées aux frais médicaux sont **{top_1}** "
    f"({correlations_cible[top_1]:.2f}), **{top_2}** ({correlations_cible[top_2]:.2f}) "
    f"et **{top_3}** ({correlations_cible[top_3]:.2f}). Le sexe, le nombre d'enfants "
    "et la région ont un lien très faible avec les frais."
)