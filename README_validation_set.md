# Jura Heavy Metals — Validation Set (n=100)

This repository contains the **validation (testing) subset** of the classic Swiss Jura dataset. It is strictly reserved for spatial model evaluation, performance benchmarking, and assessing algorithmic generalization.

---

## 📂 Included Files

| File | Description |
|---|---|
| `jura_validation_set.csv` | The raw tabular data containing the 100 validation samples. |
| `jura_validation_dashboard.html` | An interactive HTML dashboard visualizing the validation data in isolation. |
| `gen_val_dashboard.py` | The Python script used to generate the dashboard from the CSV. |

*(Note: The other 259 samples from the original dataset are used as the prediction (training) set).*

---

## 📊 Dataset Overview (`jura_validation_set.csv`)

The validation set contains **100 geo-referenced samples** completely separate from the training set.

### Contextual & Spatial Variables
- **S/N**: Unique sample ID
- **X (km), Y (km)**: Spatial coordinates
- **Rock type**: Underlying geology (1=Argovian, 2=Kimmeridgian, 3=Sequanian, 4=Portlandian, 5=Quaternary)
- **Land use**: Surface land cover (1=Forest, 2=Pasture, 3=Meadow, 4=Tillage)

### Target Variables (Heavy Metals)
Concentrations (in ppm) to safely evaluate predictions for:
- **Cd**: Cadmium
- **Cu**: Copper
- **Pb**: Lead
- **Co**: Cobalt
- **Cr**: Chromium
- **Ni**: Nickel
- **Zn**: Zinc

---

## 🗺️ Interactive Validation Dashboard

Open `jura_validation_dashboard.html` in any browser to inspect the evaluation set. 

While EDA is typically reserved for training data, running this dashboard against the validation set allows researchers to visually confirm that the validation distribution holds similar statistical properties (mean/variance/spatial spread) as the prediction set. 

Features included:
- **Validation KPI Cards**: Key metrics for the pure 100-sample test set.
- **Distribution Histograms**: Visualize validation data spread.
- **Spatial Map**: Map highlighting exactly where the "hold-out" test points are located geographically.

---

## 🚀 Usage & AI Evaluation

This 100-sample subset is strictly intended for **testing and evaluation**. 

If you are developing AI models or working with autonomous AI agents:
1. **Do not train models on this file.**
2. Use this data purely to test the predictive accuracy of spatial interpolation algorithms (like Kriging or Random Forests).
3. Evaluate how well categorical insights (Rock Type / Land Use) generalize to unseen coordinate locations.
