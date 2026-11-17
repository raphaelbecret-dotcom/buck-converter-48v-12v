"""Step 1 - Hand-sizing of a 48 V -> 12 V / 5 A buck converter (CCM).

Run: python design_calc.py
"""

# --- Specification -----------------------------------------------------
VIN = 48.0        # input voltage [V]
VOUT = 12.0       # output voltage [V]
IOUT = 5.0        # nominal output current [A]
FSW = 100e3       # switching frequency [Hz]
RIPPLE_I = 0.30   # inductor current ripple, fraction of IOUT
RIPPLE_V = 0.01   # output voltage ripple, fraction of VOUT

# --- Ideal CCM sizing --------------------------------------------------
D = VOUT / VIN
dI = RIPPLE_I * IOUT
dV = RIPPLE_V * VOUT
L = VOUT * (1 - D) / (FSW * dI)
C = dI / (8 * FSW * dV)
I_peak = IOUT + dI / 2
I_valley = IOUT - dI / 2
I_ccm_limit = dI / 2
POUT = VOUT * IOUT

# --- First-order loss estimate (asynchronous buck, Schottky diode) -----
VF_DIODE = 0.5    # Schottky forward drop [V] (assumption)
RDS_ON = 0.025    # MOSFET on-resistance [ohm] (assumption)
I_rms_sw = (IOUT**2 + dI**2 / 12) ** 0.5 * D**0.5
P_diode = VF_DIODE * (1 - D) * IOUT
P_cond_sw = RDS_ON * I_rms_sw**2

if __name__ == "__main__":
    print(f"Duty cycle D            = {D:.3f}")
    print(f"Ripple current dIL      = {dI:.2f} A")
    print(f"Inductance L            = {L*1e6:.1f} uH")
    print(f"Inductor peak current   = {I_peak:.2f} A (valley {I_valley:.2f} A)")
    print(f"Capacitance C (ideal)   = {C*1e6:.1f} uF -> pick 22 uF")
    print(f"CCM limit (Iout min)    = {I_ccm_limit:.2f} A")
    print(f"Output power            = {POUT:.0f} W")
    print(f"Diode loss (est.)       = {P_diode:.2f} W")
    print(f"MOSFET conduction (est.)= {P_cond_sw:.2f} W")
    print(f"Efficiency (cond. only) = {POUT/(POUT+P_diode+P_cond_sw)*100:.1f} %")
