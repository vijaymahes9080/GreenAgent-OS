# Multi-Objective Optimization Specification

## Mathematical Formulation

The GreenAgent OS optimization solver balances five competing dimensions: Energy ($E$), Carbon ($C$), Financial Cost ($\text{Cost}$), Latency ($L$), and Quality Loss ($Q_{\text{loss}}$).

$$\min J = \alpha \cdot \bar{E} + \beta \cdot \bar{C} + \gamma \cdot \bar{\text{Cost}} + \delta \cdot \bar{L} + \epsilon \cdot (1 - \text{Quality})$$

### Normalization Baselines

Raw physical units are normalized into non-dimensional metrics bounded in $[0, 1]$:

$$\bar{E} = \min\left(1.0, \, \frac{E}{E_{\text{norm}}}\right), \quad E_{\text{norm}} = 100.0 \, \text{Joules}$$

$$\bar{C} = \min\left(1.0, \, \frac{C}{C_{\text{norm}}}\right), \quad C_{\text{norm}} = 0.05 \, \text{gCO}_2\text{e}$$

$$\bar{\text{Cost}} = \min\left(1.0, \, \frac{\text{Cost}}{\text{Cost}_{\text{norm}}}\right), \quad \text{Cost}_{\text{norm}} = \$0.005$$

$$\bar{L} = \min\left(1.0, \, \frac{L}{L_{\text{norm}}}\right), \quad L_{\text{norm}} = 2000.0 \, \text{ms}$$

### Default Weight Calibration

| Parameter | Dimension | Default Value | Tuning Scope |
| :--- | :--- | :--- | :--- |
| $\alpha$ | Energy Consumption | `0.25` | Favors distilled 1B–3B parameter models |
| $\beta$ | Carbon Footprint | `0.35` | Favors low-carbon regional shifts |
| $\gamma$ | Financial Cost | `0.20` | Penalizes high-parameter token costs |
| $\delta$ | Execution Latency | `0.10` | Enforces fast interactive SLA |
| $\epsilon$ | Quality Preservation | `0.10` | Restricts quality degradation |

---

## Constraints

Every candidate execution plan must satisfy strict hard constraints:

1. **Quality Floor**:
   $$\text{Quality}(m) \ge Q_{\text{min}}$$
2. **Latency Ceiling**:
   $$L(m) \le L_{\text{max}}$$
3. **Deadline Invariant**:
   $$t_{\text{scheduled}} + L(m) \le \text{Deadline}$$
4. **Availability Constraint**:
   $$\text{Availability}(m) = \text{True}$$

---

## Routing & Optimization Pipeline

1. **Semantic Cache Evaluation**:
   If an identical or high-similarity query ($\text{sim} \ge 0.90$) exists in the cache and the workload is not safety-critical, the optimizer selects `USE_CACHE`, achieving **99.9% energy reduction**.
2. **Complexity Classification**:
   Evaluates prompt length, code tokens, multi-step reasoning keywords, and tool requirements to classify task into `EASY`, `MEDIUM`, `HARD`, or `CRITICAL`.
3. **Candidate Model Pruning**:
   Filters out models in the registry that fail the quality floor or latency limit.
4. **Spatial & Temporal Scheduling**:
   Determines the cleanest region and whether temporal shifting is permissible.
5. **Quality Guard Post-Validation**:
   Verifies generated output structure and schema. If quality degrades, the system automatically triggers a rollback and re-executes with a higher-tier model.
