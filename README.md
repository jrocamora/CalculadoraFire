# 🔥 Calculadora FIRE Pro (Streamlit)

Aplicació web interactiva per calcular la **Independència Financera i Jubilació Anticipada (FIRE)** tenint en compte la fiscalitat real a **Catalunya**, **Irlanda** i **Andorra**.

Migrada de React/Vite/TypeScript a **Python + Streamlit + Plotly**.

---

## 🚀 Com executar en local

1. **Instal·la les dependències**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicia l'aplicació**:
   ```bash
   streamlit run app.py
   ```

3. Obre el navegador a `http://localhost:8501`.

---

## ☁️ Com hostejar GRATIS a Streamlit Community Cloud

Pots hostejar aquesta aplicació de manera **100% gratuïta** a **[Streamlit Community Cloud](https://share.streamlit.io/)**:

1. Puja aquest repositori a **GitHub** (públic o privat).
2. Entra a [share.streamlit.io](https://share.streamlit.io/) i inicia sessió amb el teu compte de GitHub.
3. Fes clic a **"New app"**.
4. Selecciona el teu repositori (`CalculadoraFire`), branca `main` o `master`, i fitxer principal `app.py`.
5. Fes clic a **"Deploy"**.

A partir d'aquí, qualsevol `git push` que facis s'actualitzarà automàticament al teu domini gratuït de Streamlit (`https://<el-teu-nom>-calculadorafire.streamlit.app`).

---

## 🏛️ Funcionalitats fiscals incloses

- **Catalunya (CAT)**:
  - Trams d'IRPF de l'Estalvi (19% a 28%) amb 50% tram autonòmic de la Generalitat.
  - Càlcul sobre la plusvàlua latent real (el capital principal invertit no tributa).
  - Impost sobre el Patrimoni propi de Catalunya amb mínim exempt de 500.000 € i escala progressiva (0,21% - 3,48%) amb escut fiscal del 60%.
- **Irlanda (IE)**:
  - Exit Tax del 41% en ETFs UCITS + Deemed Disposal cada 8 anys (opció 1/8 anual escalonat DCA o en bloc).
  - Capital Gains Tax (CGT) del 33% en accions individuals amb exempció anual de 1.270 €.
- **Andorra (AD)**:
  - 0% d'impost en compravenda de borsa cotitzada internacional (<25%).
  - Règim general de rendes de capital al 10% amb 3.000 € anuals exempts.
  - Sense impost de patrimoni.
- **Canvi de residència fiscal planificat**:
  - Simula començar acumulant a Catalunya o Irlanda i passar a viure a Andorra en un any concret.
- **Reforma fiscal**:
  - Simula increments o reduccions generals en la tributació de l'estalvi (-5% a +10%).

---

## 📁 Arquitectura del Projecte

```
CalculadoraFire/
├── app.py                      # Orquestrador principal Streamlit
├── requirements.txt            # Dependències (streamlit, plotly, pandas)
├── .streamlit/
│   └── config.toml             # Tema fosc personalitzat
├── config/
│   ├── defaults.py             # Valors inicials i constants
│   └── translations.py         # Diccionari i18n Català / Anglès
├── models/
│   ├── types.py                # Dataclasses de tipus de dades
│   └── __init__.py
├── engine/
│   ├── fire_simulation.py      # Motor de simulació pur Python
│   ├── tax_calculators.py      # Motor de càlcul fiscal CAT/IE/AD
│   └── __init__.py
└── ui/
    ├── header.py               # Capçalera i estils CSS
    ├── metric_cards.py         # Targetes de mètriques clau
    ├── inputs.py               # Inputs bidireccionals i actius
    ├── swr_control.py          # Selector SWR i presets
    ├── country_tax.py          # Selector fiscal per territori
    ├── macro_scenario.py       # Escenaris macroeconòmics
    ├── fire_chart.py           # Gràfic interactiu Plotly
    ├── tax_breakdown.py        # Desglossament de despesa i impostos
    ├── country_comparison.py   # Comparativa dels 3 països
    ├── yearly_table.py         # Taula any a any i descàrrega CSV
    └── __init__.py
```
