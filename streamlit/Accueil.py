import streamlit as st

from modules.chargement import charger_donnees

st.set_page_config(
    page_title="Aegis Health Coverage",
    page_icon="🩺",
    layout="wide",
)

df_insurance = charger_donnees()


def format_nombre(valeur, decimales=0):
    """Nombre au format français : espace pour les milliers, virgule décimale."""
    texte = f"{valeur:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",")


# ---------- Chiffres calculés depuis les données ----------
frais_fumeurs = df_insurance.loc[df_insurance["smoker"] == "yes", "expenses"].median()
frais_non_fumeurs = df_insurance.loc[df_insurance["smoker"] == "no", "expenses"].median()
rapport_fumeurs = frais_fumeurs / frais_non_fumeurs

nb_assures = len(df_insurance)
frais_medians = df_insurance["expenses"].median()
part_fumeurs = (df_insurance["smoker"] == "yes").mean() * 100

# Largeur des barres du hero, en % : la barre fumeurs sert de référence (100 %)
largeur_non_fumeurs = frais_non_fumeurs / frais_fumeurs * 100

# ---------- Style de la page ----------
# st.html insère du HTML/CSS tel quel (contrairement à st.markdown,
# il n'interprète pas les $ comme des formules mathématiques)
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

:root {
  --ae-encre: #17324D;
  --ae-texte: #1E2A33;
  --ae-texte-doux: #52606B;
  --ae-trait: #CBD7D0;
  --ae-fumeur: #C0504D;
  --ae-non-fumeur: #4F81BD;
}

.ae-hero { max-width: 780px; padding: 1.5rem 0 1rem; }
.ae-client { color: var(--ae-texte-doux); font-size: 1rem; margin: 0 0 0.75rem; }
.ae-titre {
  font-family: 'Source Serif 4', Georgia, serif;
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.15;
  color: var(--ae-encre);
  margin: 0 0 1.75rem;
}

.ae-barres { display: grid; gap: 0.6rem; margin-bottom: 1.75rem; }
.ae-ligne { display: grid; grid-template-columns: 7.5rem 1fr; align-items: center; gap: 0.75rem; }
.ae-ligne-nom { font-size: 0.95rem; color: var(--ae-texte-doux); }
.ae-barre {
  height: 2.1rem; border-radius: 3px;
  display: flex; align-items: center; justify-content: flex-end;
  padding: 0 0.7rem; color: #fff; font-weight: 600; font-size: 0.95rem;
  min-width: fit-content;
}
.ae-barre-fumeur { background: var(--ae-fumeur); }
.ae-barre-non-fumeur { background: var(--ae-non-fumeur); }

.ae-contexte { font-size: 1.05rem; line-height: 1.6; color: var(--ae-texte); margin: 0; }

.ae-chiffres {
  display: flex; flex-wrap: wrap;
  border-top: 1px solid var(--ae-trait); border-bottom: 1px solid var(--ae-trait);
  margin: 2rem 0 2.5rem;
}
.ae-chiffre { flex: 1 1 200px; padding: 1.1rem 1.5rem 1.1rem 0; }
.ae-chiffre + .ae-chiffre { border-left: 1px solid var(--ae-trait); padding-left: 1.5rem; }
@media (max-width: 640px) {
  .ae-chiffre + .ae-chiffre { border-left: none; padding-left: 0; border-top: 1px solid var(--ae-trait); }
}
.ae-chiffre-valeur {
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 1.9rem; font-weight: 600; color: var(--ae-encre); line-height: 1.2;
}
.ae-chiffre-nom { color: var(--ae-texte-doux); font-size: 0.95rem; }

.ae-section-titre {
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 1.6rem; font-weight: 600; color: var(--ae-encre); margin: 0 0 1rem;
}
.ae-variables { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1rem; }
.ae-groupe { border: 1px solid var(--ae-trait); border-radius: 4px; padding: 1.1rem 1.25rem; background: #fff; }
.ae-groupe-cible { background: var(--ae-encre); border-color: var(--ae-encre); }
.ae-groupe h3 { font-size: 1.05rem; font-weight: 600; color: var(--ae-encre); margin: 0 0 0.6rem; padding: 0; }
.ae-groupe.ae-groupe-cible h3, .ae-groupe.ae-groupe-cible li { color: #fff; }
.ae-groupe ul { list-style: none; margin: 0; padding: 0; }
.ae-groupe li { padding: 0.3rem 0; color: var(--ae-texte); font-size: 0.97rem; }
.ae-groupe li span { color: var(--ae-texte-doux); font-size: 0.85rem; }
.ae-groupe.ae-groupe-cible li span { color: #C9D6E2; }
</style>
"""
)

# ---------- Hero : le message clé ----------
st.html(
    f"""
<div class="ae-hero">
  <p class="ae-client">Aegis Health Coverage</p>
  <h1 class="ae-titre">En médiane, un fumeur coûte {format_nombre(rapport_fumeurs, 1)} fois plus cher en frais médicaux qu'un non-fumeur.</h1>

  <div class="ae-barres" role="img"
       aria-label="Frais médians : {format_nombre(frais_non_fumeurs)} dollars pour les non-fumeurs, {format_nombre(frais_fumeurs)} dollars pour les fumeurs">
    <div class="ae-ligne">
      <span class="ae-ligne-nom">Non-fumeurs</span>
      <div class="ae-barre ae-barre-non-fumeur" style="width: {largeur_non_fumeurs:.1f}%">{format_nombre(frais_non_fumeurs)} $</div>
    </div>
    <div class="ae-ligne">
      <span class="ae-ligne-nom">Fumeurs</span>
      <div class="ae-barre ae-barre-fumeur" style="width: 100%">{format_nombre(frais_fumeurs)} $</div>
    </div>
  </div>

  <p class="ae-contexte">
    Aegis Health Coverage veut comprendre ce qui fait varier les frais médicaux de ses assurés,
    pour ajuster ses primes au profil de chaque client. Cette application explore les données
    de {format_nombre(nb_assures)} assurés et permet d'estimer les frais d'un nouveau profil.
  </p>
</div>

<div class="ae-chiffres">
  <div class="ae-chiffre">
    <div class="ae-chiffre-valeur">{format_nombre(nb_assures)}</div>
    <div class="ae-chiffre-nom">assurés dans le dataset</div>
  </div>
  <div class="ae-chiffre">
    <div class="ae-chiffre-valeur">{format_nombre(frais_medians)} $</div>
    <div class="ae-chiffre-nom">de frais médicaux médians par an</div>
  </div>
  <div class="ae-chiffre">
    <div class="ae-chiffre-valeur">{format_nombre(part_fumeurs, 1)} %</div>
    <div class="ae-chiffre-nom">de fumeurs</div>
  </div>
</div>
"""
)

# ---------- Les données ----------
st.html(
    """
<h2 class="ae-section-titre">Les données</h2>
<div class="ae-variables">
  <div class="ae-groupe">
    <h3>Profil de l'assuré</h3>
    <ul>
      <li>Âge <span>(18 à 64 ans)</span></li>
      <li>Sexe</li>
      <li>Nombre d'enfants couverts</li>
      <li>Région de résidence <span>(4 régions des États-Unis)</span></li>
    </ul>
  </div>
  <div class="ae-groupe">
    <h3>Santé</h3>
    <ul>
      <li>Indice de masse corporelle <span>(IMC)</span></li>
      <li>Fumeur ou non</li>
    </ul>
  </div>
  <div class="ae-groupe ae-groupe-cible">
    <h3>Ce que le modèle prédit</h3>
    <ul>
      <li>Frais médicaux annuels facturés à l'assurance <span>(en dollars)</span></li>
    </ul>
  </div>
</div>
"""
)

st.write("")
with st.expander("Voir un extrait des données brutes"):
    st.dataframe(df_insurance.head(10), width="stretch", hide_index=True)

# ---------- Navigation ----------
st.html('<h2 class="ae-section-titre" style="margin-top: 1.5rem">Aller plus loin</h2>')

col_analyse, col_simulateur = st.columns(2)

with col_analyse.container(border=True):
    st.markdown("**Analyse**")
    st.markdown("Comment les frais varient selon l'âge, l'IMC, le tabac ou la région, en graphiques interactifs.")
    st.page_link("pages/1_Analyse.py", label="Explorer l'analyse", icon="📊")

with col_simulateur.container(border=True):
    st.markdown("**Simulateur**")
    st.markdown("Saisir le profil d'un assuré et obtenir une estimation de ses frais médicaux annuels.")
    st.page_link("pages/2_Simulateur.py", label="Estimer des frais", icon="🧮")