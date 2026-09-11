# Carbon Footprint Methodology

## Mathematical Formulation

GreenAgent OS translates electrical energy consumption into greenhouse gas emissions expressed in grams of carbon dioxide equivalent ($\text{gCO}_2\text{e}$):

$$\text{Carbon} \, (\text{gCO}_2\text{e}) = E_{\text{kWh}} \times \text{PUE} \times I_{\text{grid}}(r, t)$$

Where:
- $E_{\text{kWh}} = \frac{\text{Joules}}{3,600,000}$
- $\text{PUE}$ = Datacenter Power Usage Effectiveness (ratio of total facility energy to IT equipment energy, typically 1.15 – 1.35).
- $I_{\text{grid}}(r, t)$ = Regional Grid Marginal Carbon Intensity ($\text{gCO}_2\text{e}/\text{kWh}$) in region $r$ at time $t$.

---

## Regional Grid Profiles

GreenAgent OS maintains calibrated diurnal variation profiles for five global datacenter regions:

| Region Code | Region Name | Base Intensity ($I_{\text{base}}$) | Solar Factor | Datacenter PUE | Primary Generation Mix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `eu-north` | Europe North (Stockholm) | 42 $\text{g/kWh}$ | 10 $\text{g}$ | 1.15 | Hydroelectric, Nuclear, Wind |
| `us-west` | US West (Oregon) | 185 $\text{g/kWh}$ | 50 $\text{g}$ | 1.18 | Hydroelectric, Solar, Gas |
| `eu-central` | Europe Central (Frankfurt) | 310 $\text{g/kWh}$ | 75 $\text{g}$ | 1.22 | Wind, Solar, Coal, Gas |
| `us-east` | US East (N. Virginia) | 375 $\text{g/kWh}$ | 60 $\text{g}$ | 1.25 | Gas, Nuclear, Solar, Coal |
| `ap-south` | Asia Pacific (Mumbai) | 610 $\text{g/kWh}$ | 90 $\text{g}$ | 1.35 | Coal, Solar, Hydro |

---

## Diurnal Dynamics & Renewable Valleys

Grid carbon intensity fluctuates throughout the 24-hour cycle due to solar irradiance and wind variations:

$$I_{\text{grid}}(r, t) = \max \left( 20.0, \, I_{\text{base}}(r) - \Delta I_{\text{solar}}(t) - \Delta I_{\text{wind}}(t) \right)$$

- **Solar Abatement**: Peaking between 11:00 and 15:00 local time:
  $$\Delta I_{\text{solar}}(t) = \max \left( 0.0, \, \sin\left(\frac{t - 6}{24} \cdot 2\pi\right) \right) \times S_{\text{factor}}(r)$$
- **Wind Abatement**: Stronger during late night and early morning hours.

---

## Carbon Arbitrage Mechanisms

1. **Spatial Arbitrage (`MOVE_REGION`)**:
   Moving an inference task from a carbon-heavy grid (`us-east`: 375 g/kWh) to a clean hydro/nuclear grid (`eu-north`: 42 g/kWh) reduces emissions by **up to 88.8%** with zero delay.
2. **Temporal Arbitrage (`DELAY`)**:
   Postponing batch or flexible workloads to synchronize with midday solar generation peaks reduces carbon by **15% – 30%** without hardware changes.
