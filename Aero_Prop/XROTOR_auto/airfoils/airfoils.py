import numpy as np
import matplotlib.pyplot as plt


filename = r"C:\Users\helen\Downloads\XFOIL6.99\naca0012final.pol" 



# === Parse polar file ===
alpha, cl, cd, cm = [], [], [], []
re_number = 100000.0  # Default
mach_number = 0.0


with open(filename, 'r') as f:
    lines = f.readlines()

# Find Re and Mach from file header
for line in lines:
    if "Re =" in line and "Mach" in line:
        try:
            parts = line.replace('=', ' ').split()
            re_index = parts.index("Re") + 1
            re_val_str = parts[re_index] + parts[re_index + 1]  # Handle '0.100' 'e' '6'
            re_number = float(eval(re_val_str))  # e.g. "0.100e6"
            mach_index = parts.index("Mach") + 1
            mach_number = float(parts[mach_index])
        except:
            pass
        break

data_section = False
for line in lines:
    if "alpha" in line and "CL" in line:
        data_section = True
        continue
    if data_section:
        parts = line.strip().split()
        if len(parts) >= 5:
            try:
                alpha.append(float(parts[0]))
                cl.append(float(parts[1]))
                cd.append(float(parts[2]))
                cm.append(float(parts[4]))
            except ValueError:
                continue

alpha = np.array(alpha)
cl = np.array(cl)
cd = np.array(cd)
cm = np.array(cm)

# === Computations for XROTOR ===
cl_max = np.max(cl)
cl_min = np.min(cl)
cd_min = np.min(cd)
cl_at_cdmin = cl[np.argmin(cd)]

# Linear lift slope dCL/dalpha
linear_region = (alpha >= -5) & (alpha <= 5)
dcl_dalpha = np.polyfit(alpha[linear_region], cl[linear_region], 1)[0]

# Stall slope: after max CL (rough estimate)
stall_region = (alpha >= 10)
if np.sum(stall_region) >= 2:
    dcl_dalpha_stall = np.polyfit(alpha[stall_region], cl[stall_region], 1)[0]
else:
    dcl_dalpha_stall = 0.1  # fallback default

# Zero-lift alpha
zero_lift_alpha = float(np.interp(0.0, cl, alpha))

# CL increment to stall (CL_max – CL at 5 deg)
cl_at_5deg = float(np.interp(5.0, alpha, cl))
delta_cl_stall = cl_max - cl_at_5deg

# CD vs CL^2 drag polar fit
cl2 = cl**2
dcd_dcl2 = np.polyfit(cl2, cd, 1)[0]

# Cm average near 0 alpha
cm_avg = np.mean(cm[(alpha >= -5) & (alpha <= 5)])

# === Estimate Mcrit ===
# Rough empirical estimate
mcrit = mach_number + 0.75 * (0.8 - mach_number)
mcrit = min(mcrit, 0.80)  # do not exceed 0.80 for typical airfoils


# Output in XROTOR format
print("======================================================================")
print(f" 1) Zero-lift alpha (deg):       {zero_lift_alpha:.2f}")
print(f" 2) d(Cl)/d(alpha):              {dcl_dalpha:.3f}")
print(f" 3) d(Cl)/d(alpha)@stall:        {dcl_dalpha_stall:.3f}")
print(f" 4) Maximum Cl:                  {cl_max:.3f}")
print(f" 5) Minimum Cl:                  {cl_min:.3f}")
print(f" 6) Cl increment to stall:       {delta_cl_stall:.3f}")
print(f" 7) Minimum Cd:                  {cd_min:.5f}")
print(f" 8) Cl at minimum Cd:            {cl_at_cdmin:.3f}")
print(f" 9) d(Cd)/d(Cl**2):              {dcd_dcl2:.5f}")
print(f"10) Reference Re number:         {re_number:.0f}")
print(f"11) Re scaling exponent:         -0.40   # Assumed idk what this is")
print(f"12) Cm:                          {cm_avg:.3f}")
print(f"13) Mcrit:                       {mcrit:.2f} # rough etimate emp")
print(f"14) d(Cd)/d(M**2):               0.0000  # Default")
print("======================================================================")
