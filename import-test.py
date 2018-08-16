import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

db = pd.read_csv("resources/region-data/database.csv")

x = np.array(db["304_AVG_INTEN"])
y = np.array(db["UNSIG_GAUSS"])

bad_values = np.where(np.isnan(y))[0]
x = np.delete(x, bad_values)
y = np.delete(y, bad_values)

# x = np.sort(x)
# y = np.sort(y)

plt.scatter(x, y)
plt.show()
