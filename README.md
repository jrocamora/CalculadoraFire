# 🇮🇪 FIRE Calculator Ireland (Budget 2027)

Aplicació web (Python + Streamlit + Plotly) per planificar la **independència financera i la jubilació anticipada (FIRE)** amb la fiscalitat d'**Irlanda**, incloses les mesures anunciades al **Budget 2027**. La interfície és en anglès.

> Eina educativa i de simulació. No és assessorament financer, fiscal ni legal. Les xifres del Budget 2027 depenen de la Finance Bill: comprova-les amb Revenue abans de fer-les servir per decidir res.

---

## 🚀 Com executar en local

Cal Python 3.11 o posterior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Obre el navegador a `http://localhost:8501`.

## ☁️ Publicar a Streamlit Community Cloud

1. Puja el repositori a GitHub.
2. A [share.streamlit.io](https://share.streamlit.io/), fes **New app**, tria el repositori, la branca `main` i el fitxer `app.py`.
3. **Deploy**. Cada `git push` a `main` actualitza l'app.

## 🔒 Privadesa

Streamlit executa el càlcul **al servidor**: les xifres que introdueix l'usuari hi viatgen, però l'app no les desa ni demana cap compte, i es descarten en tancar la pàgina. L'enllaç per compartir porta totes les xifres codificades dins la URL, de manera que qualsevol persona que el tingui les pot llegir.

---

## 🏛️ Què modela

**Cartera líquida**, en tres pots amb fiscalitat pròpia:

| Pot | Actius | Fiscalitat |
|---|---|---|
| Compte d'Inversió (Budget 2027) | Categoria «New Investment Account» | Obre l'1 de juliol de 2027, màxim 12.000 €/any (6.000 € el 2027). 1% anual sobre el saldo que supera 50.000 €. Retirades sense impost. |
| ETFs / fons UCITS | Categoria «Index Funds / ETFs» | Exit Tax del 35% (38% el 2026) sobre la plusvàlua en retirar. Deemed Disposal opcional (1/8 anual o en bloc cada 8 anys). |
| Altres | Accions, efectiu, immobles | CGT del 31% sobre la plusvàlua, amb 1.270 € d'exempció anual. |

- L'opció «Where do your new monthly savings go?» decideix on van els estalvis nous. Amb el Compte d'Inversió, l'excés sobre el límit (i tot el que s'estalvia abans que obri) va a ETFs.
- El rendiment de cada pot és la mitjana ponderada del rendiment esperat dels seus actius. L'escenari macro el desplaça respecte al 7% base.
- El cost d'adquisició de cada actiu determina quina part de cada retirada és plusvàlua.
- En jubilació es retira primer del Compte d'Inversió, després de les accions i altres, i finalment dels ETFs.

**Pensions** (desactivades per defecte):

- **State Pension**: 309,30 €/setmana des de gener de 2027 (~1.340 €/mes), a partir dels 66 anys. No tributa en aquest model.
- **Pensió privada / PRSA**: creix sense impostos; en arribar a l'edat d'accés, el 25% (màxim 200.000 €) passa a la cartera líquida sense impost i la resta es retira com a ARF.
- **MyFutureFund** (auto-enrolment): aportació de l'empresa igual a la teva i 1 € de l'Estat per cada 3 €; accés als 66 anys amb el mateix 25% exempt.
- Les retirades d'ARF i MyFutureFund tributen a un tipus efectiu configurable (20% per defecte).

**Altres controls**: taxa de retirada segura (SWR), escenaris macro (base, optimista, conservador, estrès amb caiguda els dos primers anys de jubilació), sensibilitat a reformes fiscals i taula any a any amb descàrrega CSV.

### Simplificacions conegudes

- Per calcular l'objectiu FIRE s'assumeix que les retirades tributen com els ETFs (o com les accions, si els estalvis hi van). És una estimació prudent: les retirades del Compte d'Inversió no tributen.
- Els interessos de l'efectiu es tracten com a plusvàlua amb CGT, no amb DIRT anual.
- No es modelen l'impost sobre la renda dels dividends, l'USC ni el PRSI més enllà del tipus efectiu de les pensions.

---

## 📁 Estructura

```
├── app.py                  # Orquestrador Streamlit
├── requirements.txt        # Versions provades
├── .streamlit/config.toml  # Tema clar
├── config/                 # Valors per defecte i textos
├── models/types.py         # Dataclasses
├── engine/
│   ├── fire_simulation.py  # Simulació any a any
│   └── tax_calculators.py  # Càlcul fiscal per retirada
├── ui/                     # Components de la interfície (ui/keys.py: claus de widgets i reset)
└── utils/serialization.py  # Enllaç per compartir i import/export JSON
```
