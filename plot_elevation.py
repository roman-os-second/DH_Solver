import numpy as np
import matplotlib.pyplot as plt

elevation = np.load("elevation.npy")

plt.imshow(
    elevation,
    origin="lower",
    extent=[0, 2000, 0, 2000],
    aspect="equal",
    interpolation="bilinear"
    )

plt.colorbar(label="Elevation (m)")
plt.title("Elevation Profile")
plt.xlabel("Distance (m)")
plt.ylabel("Elevation (m)")


plt.show()