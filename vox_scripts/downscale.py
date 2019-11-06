import numpy as np
from scipy.ndimage import zoom
import os
import sys

inp = np.load(os.path.abspath(sys.argv[1]))
h, w, d = inp.shape
outh, outw, outd = (8, 8, 8)
zoomh, zoomw, zoomd = outh / h, outw / w, outd / d
rescaled = zoom(inp, (zoomh, zoomw, zoomd))
print(rescaled.shape)