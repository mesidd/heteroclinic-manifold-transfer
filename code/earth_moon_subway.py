import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from numpy import linalg as LA

# --- 1. SYSTEM CONSTANTS ---
mu = 0.0121505856
L1_x = 0.8369152

# --- 2. GET THE DIRECTIONS (EIGENVECTORS) ---
O_xx = 1 + 2*(1-mu)/abs(L1_x + mu)**3 + 2*mu/abs(L1_x - 1 + mu)**3
O_yy = 1 - (1-mu)/abs(L1_x + mu)**3 - mu/abs(L1_x - 1 + mu)**3
A = np.array([[0, 0, 1, 0], [0, 0, 0, 1], [O_xx, 0, 0, 2], [0, O_yy, -2, 0]])
vals, vecs = LA.eig(A)

# Extract Real Eigenvectors (The "Rails")
idx_u = [i for i, v in enumerate(vals) if np.isreal(v) and v > 0][0] # Unstable (+)
idx_s = [i for i, v in enumerate(vals) if np.isreal(v) and v < 0][0] # Stable (-)

v_unstable = vecs[:, idx_u].real
v_stable   = vecs[:, idx_s].real

# Normalize vectors to ensure consistent perturbation size
v_unstable = v_unstable / np.linalg.norm(v_unstable)
v_stable   = v_stable   / np.linalg.norm(v_stable)

# --- 3. THE SCATTERSHOT: MAP ALL 4 ROADS ---
epsilon = 1e-4 # The nudge
T = 15         # Time duration

t_fwd = np.linspace(0, T, 10000)   # Future
t_bwd = np.linspace(0, -T, 10000)  # Past

def cr3bp(s, t, mu):
    x, y, vx, vy = s
    r1 = ((x+mu)**2 + y**2)**0.5
    r2 = ((x-1+mu)**2 + y**2)**0.5
    ax = x + 2*vy - (1-mu)*(x+mu)/r1**3 - mu*(x-1+mu)/r2**3
    ay = y - 2*vx - (1-mu)*y/r1**3 - mu*y/r2**3
    return [vx, vy, ax, ay]

plt.figure(figsize=(12, 8))

# --- PLOT THE STATIC OBJECTS ---
plt.plot(-mu, 0, 'bo', markersize=12, label='Earth')    # Blue Dot
plt.plot(1-mu, 0, 'go', markersize=6, label='Moon')     # Green Dot
plt.plot(L1_x, 0, 'rx', markersize=10, markeredgewidth=3, label='L1 Gateway')

# --- SIMULATE AND PLOT ALL 4 PATHS ---
directions = [1, -1]
labels_u = ["To Moon", "To Earth"]
colors_u = ['black', 'blue']

# 1. UNSTABLE MANIFOLDS (Forward in Time) - The "Drop"
for i, d in enumerate(directions):
    # We test +Vector and -Vector to find both sides
    start = np.array([L1_x, 0, 0, 0]) + d * epsilon * v_unstable
    traj = odeint(cr3bp, start, t_fwd, args=(mu,))
    
    # Check if it went Left (Earth) or Right (Moon)
    final_x = traj[-1, 0]
    label = "Drop to Moon" if final_x > L1_x else "Drop to Earth (Blue)"
    color = 'k' if final_x > L1_x else 'b' # Blue for Earth line
    
    plt.plot(traj[:,0], traj[:,1], color=color, linewidth=1.5, label=label if i==0 or color=='b' else "")

# 2. STABLE MANIFOLDS (Backward in Time) - The "Lift"
for i, d in enumerate(directions):
    start = np.array([L1_x, 0, 0, 0]) + d * epsilon * v_stable
    traj = odeint(cr3bp, start, t_bwd, args=(mu,))
    
    final_x = traj[-1, 0]
    label = "Lift from Moon" if final_x > L1_x else "Lift from Earth (Cyan)"
    color = 'grey' if final_x > L1_x else 'c' # Cyan for Earth line
    
    plt.plot(traj[:,0], traj[:,1], color=color, linestyle='--', linewidth=1.5, label=label if i==0 or color=='c' else "")

plt.title("THE COMPLETE GRAVITY SUBWAY MAP", fontsize=14)
plt.xlabel("x (Normalized Distance)")
plt.ylabel("y (Normalized Distance)")
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right')
plt.axis('equal')
plt.xlim(-0.15, 1.2) # Zoom to see Earth and Moon
plt.ylim(-0.5, 0.5)

plt.show()
