import numpy as np
import matplotlib.pyplot as plt

# === Change this to your .pol file ===
filename = 'naca4412.pol'

# === Read polar data ===
alpha, cl, cd, cm = [], [], [], []
with open(filename, 'r') as f:
    for line in f:
        if line.strip().startswith('-') or 'alpha' in line.lower():
            continue  # Skip headers
        parts = line.strip().split()
        if len(parts) >= 6:
            alpha.append(float(parts[0]))
            cl.append(float(parts[1]))
            cd.append(float(parts[2]))
            cm.append(float(parts[4]))

alpha = np.array(alpha)
cl = np.array(cl)
cd = np.array(cd)
cm = np.array(cm)

# === Compute parameters ===
cl_max = np.max(cl)
cl_min = np.min(cl)
cd_min = np.min(cd)
cl_at_cdmin = cl[np.argmin(cd)]

# Linear fit for dCL/dalpha (between -5° and 5°)
mask_linear = (alpha >= -5) & (alpha <= 5)
fit_lin = np.polyfit(alpha[mask_linear], cl[mask_linear], 1)
dcl_dalpha = fit_lin[0]

# Post-stall slope estimate (past 14 deg)
mask_stall = (alpha >= 14) & (alpha <= 20)
if np.sum(mask_stall) >= 2:
    fit_stall = np.polyfit(alpha[mask_stall], cl[mask_stall], 1)
    dcl_dalpha_stall = fit_stall[0]
else:
    dcl_dalpha_stall = 0.01  # fallback estimate

# Zero-lift alpha
zero_lift_alpha = np.interp(0, cl, alpha)

# CD vs CL^2 fit for d(CD)/d(CL^2)
cl2 = cl**2
fit_cd_cl2 = np.polyfit(cl2, cd, 1)
dcd_dcl2 = fit_cd_cl2[0]

# Delta CL to stall (CLmax - CL at 5 deg)
cl_at_5deg = np.interp(5, alpha, cl)
delta_cl_stall = cl_max - cl_at_5deg

# Average Cm near alpha = 0
cm_avg = np.mean(cm[(alpha >= -2) & (alpha <= 2)])

# === Print output ===
print("=== XROTOR .AERO Section Parameters ===")
print(f"1) Zero-lift alpha (deg):       {zero_lift_alpha:.2f}")
print(f"2) d(CL)/d(alpha):              {dcl_dalpha:.3f}")
print(f"3) d(CL)/d(alpha)@stall:        {dcl_dalpha_stall:.3f}")
print(f"4) Maximum CL:                  {cl_max:.3f}")
print(f"5) Minimum CL:                  {cl_min:.3f}")
print(f"6) CL increment to stall:       {delta_cl_stall:.3f}")
print(f"7) Minimum CD:                  {cd_min:.4f}")
print(f"8) CL at minimum CD:            {cl_at_cdmin:.3f}")
print(f"9) d(CD)/d(CL^2):               {dcd_dcl2:.4f}")
print(f"12) Cm:                         {cm_avg:.3f}")

# Optional plots
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(alpha, cl, label='CL vs α')
plt.xlabel('α (deg)')
plt.ylabel('CL')
plt.grid()
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(cl**2, cd, 'o', label='CD vs CL²')
plt.plot(cl2, np.polyval(fit_cd_cl2, cl2), '--', label='Fit')
plt.xlabel('CL²')
plt.ylabel('CD')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
