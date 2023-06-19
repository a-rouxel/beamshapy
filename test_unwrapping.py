from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from LightPipes import *
from utils import save_mask
image_path ="./slm6608_at1550_WFC.bmp"

image = Image.open(image_path)
new_array = np.array(image,dtype=np.float64)[: ,: ,0]

# compute a grid with dimensions equal to the image
X, Y = np.meshgrid(np.arange(0, new_array.shape[1], 1), np.arange(0, new_array.shape[0], 1))
GridDistance = np.sqrt((X - new_array.shape[1]/2)**2 + (Y - new_array.shape[0]/2)**2)

# set your threshold distance
threshold_distance = new_array.shape[0] / 1.5  # this is just an example, adjust as needed

new_array[new_array<=56] += 256
for x in range(new_array.shape[1]):
    for y in range(new_array.shape[0]):
        if y > 1110 and abs(x-900) > 800 and new_array[y,x] > 56:
            new_array[y,x] -= 256

new_array *= 2*np.pi/255
new_array -= np.pi

# Subtract 2*np.pi for values > 2 that are far from the center of the array
new_array[(new_array > 1) & (GridDistance > threshold_distance)] -= 2*np.pi

save_mask(new_array, "./slm6608_at1550_WFC_unwrapped.bmp")
