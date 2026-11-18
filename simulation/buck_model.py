"""Step 3 (part 1) - Switching-level Python model of the 48 V -> 12 V buck converter.

Same circuit and assumed parasitics as buck_open_loop.cir (LTspice), so results
can be compared one-to-one. Open loop, fixed duty cycle.

Model: states = inductor current iL and capacitor voltage vC, integrated with a
fixed step. Switch = Ron when on. Diode = linear approximation Vf + Rd*i
(Vf = 0.42 V, Rd = 20 mOhm, approximating the SPICE Schottky model).
Discontinuous conduction (DCM) is handled: iL is clamped at 0 when the diode stops.

Run: python buck_model.py   (writes waveforms.png and efficiency_vs_load.png)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Parameters (same as the LTspice netlist) ---------------------------
VIN, FSW, DUTY = 48.0, 100e3, 0.25
L, RL = 60e-6, 10e-3          # inductance, winding resistance
C, ESR = 22e-6, 10e-3         # capacitance, ESR
RON = 25e-3                   # switch on-resistance
VF, RD = 0.42, 20e-3          # diode forward model
DT = 5e-9                     # time step
T_SIM, T_MEAS = 3e-3, 2.5e-3  # total time, start of the measurement window


def simulate(r_load, duty=DUTY, t_sim=T_SIM, keep=True):
    """Return time, vout, iL arrays and the average input current."""
    period = 1 / FSW
    n = int(t_sim / DT)
    il, vc = 0.0, 0.0
    t = np.arange(n) * DT
    vout_a, il_a, iin_a = np.empty(n), np.empty(n), np.empty(n)
    for k in range(n):
        on = (t[k] % period) < duty * period
        vout = (vc + ESR * il) / (1 + ESR / r_load)
        if on:
            vsw = VIN - RON * il
        elif il > 0:
            vsw = -(VF + RD * il)
        else:
            vsw = vout          # DCM: diode off, inductor current stays at 0
        dil = (vsw - RL * il - vout) / L
        ic = il - vout / r_load
        il = il + dil * DT
        if (not on) and il < 0:
            il = 0.0
        vc += ic / C * DT
        vout_a[k], il_a[k] = vout, il
        iin_a[k] = il if on else 0.0
    return t, vout_a, il_a, iin_a


def metrics(t, vout, il, iin, r_load):
    m = t >= T_MEAS
    pout = np.mean(vout[m] ** 2 / r_load)
    pin = VIN * np.mean(iin[m])
    return dict(vavg=vout[m].mean(), vpp=np.ptp(vout[m]), ilpp=np.ptp(il[m]),
                ilmax=il[m].max(), pout=pout, pin=pin, eff=pout / pin)


if __name__ == "__main__":
    # 1) Nominal operating point: 5 A load (2.4 ohm)
    t, vo, il, iin = simulate(2.4)
    r = metrics(t, vo, il, iin, 2.4)
    print("Nominal (R = 2.4 ohm):")
    print(f"  Vout avg = {r['vavg']:.3f} V   Vout p-p = {r['vpp']*1e3:.0f} mV")
    print(f"  IL p-p   = {r['ilpp']:.2f} A   IL max   = {r['ilmax']:.2f} A")
    print(f"  Pout = {r['pout']:.1f} W   Pin = {r['pin']:.1f} W   efficiency = {r['eff']*100:.1f} %")

    fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    w = (t >= 2.9e-3) & (t <= 2.95e-3)
    ax[0].plot(t[w] * 1e3, vo[w]); ax[0].set_ylabel("Vout [V]"); ax[0].grid(alpha=.3)
    ax[1].plot(t[w] * 1e3, il[w], color="tab:red"); ax[1].set_ylabel("IL [A]")
    ax[1].set_xlabel("Time [ms]"); ax[1].grid(alpha=.3)
    ax[0].set_title("Steady state, 48 V -> 12 V buck, open loop, 5 A load")
    fig.tight_layout(); fig.savefig("waveforms.png", dpi=150)

    # 2) Efficiency and output voltage versus load current
    loads = [0.25, 0.5, 1, 2, 3, 4, 5, 6]            # target currents [A], R = 12 / I
    eff, vout_avg = [], []
    for i in loads:
        rl = 12.0 / i
        tt, v, ii, iin_ = simulate(rl, t_sim=3e-3)
        mm = metrics(tt, v, ii, iin_, rl)
        eff.append(mm["eff"] * 100); vout_avg.append(mm["vavg"])
        print(f"  I = {i:>4} A : Vout = {mm['vavg']:.2f} V, efficiency = {mm['eff']*100:.1f} %")
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    ax[0].plot(loads, eff, "o-"); ax[0].set_xlabel("Load current [A]"); ax[0].set_ylabel("Efficiency [%]"); ax[0].grid(alpha=.3)
    ax[1].plot(loads, vout_avg, "o-", color="tab:green"); ax[1].set_xlabel("Load current [A]"); ax[1].set_ylabel("Vout [V]"); ax[1].grid(alpha=.3)
    fig.suptitle("Open loop (D = 0.25): conduction losses only, ideal switching")
    fig.tight_layout(); fig.savefig("efficiency_vs_load.png", dpi=150)
