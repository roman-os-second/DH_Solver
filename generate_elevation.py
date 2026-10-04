import numpy as np

GRID_SIZE = 81

x = np.linspace(0, 2000, GRID_SIZE)
y = np.linspace(0, 2000, GRID_SIZE)

X, Y = np.meshgrid(x, y)

# Base terrain level
Z = np.full((GRID_SIZE, GRID_SIZE), 110.0)

# Large hill
Z += 25 * np.exp(
    -((X - 600) ** 2 + (Y - 1400) ** 2) / (2 * 350 ** 2)
)

# Smaller hill
Z += 15 * np.exp(
    -((X - 1500) ** 2 + (Y - 600) ** 2) / (2 * 250 ** 2)
)

# Depression / valley
Z -= 10 * np.exp(
    -((X - 1200) ** 2 + (Y - 1500) ** 2) / (2 * 300 ** 2)
)

# Small random variation
rng = np.random.default_rng(42)
Z += rng.normal(0, 0.7, Z.shape)

np.save("elevation.npy", Z)

print("elevation.npy created")