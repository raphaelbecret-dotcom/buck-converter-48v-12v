# 48 V → 12 V Buck Converter – Design & Simulation

Personal project (in progress) to apply the **Power Electronics** course from École Centrale de Lyon: sizing, simulating and controlling a DC-DC step-down converter.

## Specification

| Parameter | Value |
|---|---|
| Input voltage | 48 V |
| Output voltage | 12 V |
| Nominal output current | 5 A (60 W) |
| Switching frequency | 100 kHz |
| Inductor current ripple | 30 % of I_out (1.5 A) |
| Output voltage ripple | 1 % of V_out (120 mV pk-pk) |

## Roadmap

- [x] **Step 1 – Hand sizing** (CCM): duty cycle, L, C, component ratings → [`design_calc.py`](design_calc.py)
- [ ] **Step 2 – LTspice simulation**: waveforms, ripple, efficiency vs. load, conduction and switching losses
- [ ] **Step 3 – Averaged model** in Python/Matlab, compared with LTspice
- [ ] **Step 4 – Closed-loop control**: PI regulator, load-step response
- [ ] **Step 5 – Improvement**: synchronous rectification vs. Schottky diode, efficiency comparison
- [ ] Final 2-page report

## Step 1 – Sizing (ideal CCM)

| Quantity | Formula | Result |
|---|---|---|
| Duty cycle | D = V_out / V_in | 0.25 |
| Inductance | L = V_out (1 − D) / (f · ΔI_L) | 60 µH |
| Inductor peak current | I_out + ΔI_L / 2 | 5.75 A |
| Output capacitance | C = ΔI_L / (8 · f · ΔV) | ≈ 15.6 µF → 22 µF |
| CCM boundary | I_out,min = ΔI_L / 2 | 0.75 A |

**Component ratings (to be justified):** MOSFET ≥ 75–100 V, > 6 A, low R_DS(on); Schottky diode 100 V / 10 A.
First-order estimate (V_f = 0.5 V, R_DS(on) = 25 mΩ assumed): diode loss ≈ 1.9 W, MOSFET conduction loss ≈ 0.16 W. Switching losses and ESR effects are **not** included yet.

## Usage

```bash
python design_calc.py
```

## Tools
LTspice · Python · Matlab
