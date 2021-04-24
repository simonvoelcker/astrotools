import numpy as np
from tensorflow import keras

from lib.util import load_image, save_image

model = keras.models.load_model("color_calib_model_1")
filepath = "/home/simon/Hobby/astro/M106 - Galaxy/Lights/s10083.tif"
xyc_image = load_image(filepath)

w, h, c = xyc_image.shape

lookup = {}

for x in range(w):
    hits, misses = 0, 0
    for y in range(h):
        in_color = xyc_image[x, y]
        hsh = (int(in_color[0]) << 16) | (int(in_color[1]) << 8) | int(in_color[2])
        if hsh in lookup:
            xyc_image[x, y] = lookup[hsh]
            hits += 1
        else:
            in_color = np.expand_dims(in_color, 0)
            in_color = np.expand_dims(in_color, -1)
            out_color = model.predict(in_color)
            out_color = (out_color * 256).astype(np.int16)
            xyc_image[x, y] = out_color
            lookup[hsh] = out_color
            misses += 1
    print(x, w, hits, misses)

# save the result
save_image(xyc_image, "out.png")
