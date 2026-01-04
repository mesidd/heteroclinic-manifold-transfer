import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import fsolve

# --- CONFIGURATION ---
AU_Mars = 1.524 
mu_Earth = 3.0034806e-6 

# --- HELPER FUNCTIONS ---
def get_lagrange_L2(mu):
    l2_guess = 1 + (mu/3)**(1/3)
    l2 = fsolve(lambda x: x - (1-mu)/(x+mu)**2 - mu/(x-1+mu)**2, l2_guess)[0]
    return l2

def cr3bp_derivs(s, t, mu):
    x, y, vx, vy = s
    r1 = ((x+mu)**2 + y**2)**0.5
    r2 = ((x-1+mu)**2 + y**2)**0.5
    ax = x + 2*vy - (1-mu)*(x+mu)/r1**3 - mu*(x-1+mu)/r2**3
    ay = y - 2*vx - (1-mu)*y/r1**3 - mu*y/r2**3
    return [vx, vy, ax, ay]

# --- 1. SETUP DEPARTURE (WITH KICK) ---
L2_E = get_lagrange_L2(mu_Earth)
start_x = L2_E + 1e-5 

# PROGRADE KICK (The Force)
kick_velocity = 0.15 
start_E = np.array([start_x, 0, 0, kick_velocity])

# --- 2. PROPAGATE ---
t_span = np.linspace(0, 15, 5000)
traj_Earth = odeint(cr3bp_derivs, start_E, t_span, args=(mu_Earth,))

# --- 3. MARS TARGET ---
theta = np.linspace(0, 2*np.pi, 500)
mars_orbit_x = AU_Mars * np.cos(theta)
mars_orbit_y = AU_Mars * np.sin(theta)

# --- PLOT ---
plt.figure(figsize=(10, 8))

# Static Bodies
plt.plot(0, 0, 'y*', markersize=12, label='Sun')
plt.plot(1, 0, 'bo', markersize=7, label='Earth')
plt.plot(mars_orbit_x, mars_orbit_y, 'r--', linewidth=1, alpha=0.6, label='Mars Orbit (Target)')

# The Energy Barrier (Dotted)
circle_12 = plt.Circle((0, 0), 1.2, color='grey', fill=False, linestyle=':', alpha=0.5, label='1.2 AU Energy Barrier (Breached)')
plt.gca().add_patch(circle_12)

# The Manifold (The Path)
plt.plot(traj_Earth[:,0], traj_Earth[:,1], 'g-', linewidth=1.2, label='Manifold Trajectory (Post-Kick)')

# Labels and Styling
plt.title("BREAKING THE BARRIER: Earth-Mars Manifold Connection", fontsize=12)
plt.xlabel("x (AU)")
plt.ylabel("y (AU)")
plt.legend(loc='upper right', framealpha=0.9, fontsize=9)
plt.grid(True, alpha=0.3)
plt.axis('equal')
plt.xlim(-2, 2)
plt.ylim(-2, 2)

plt.show()
