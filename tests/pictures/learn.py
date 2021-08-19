import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt

img_rgb = cv2.imread("Top.jpg")
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

template = cv2.imread("mlcc.jpg", 0)
h, w = template.shape[::]

res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.5
loc = np.where(res >= threshold)

ax = plt.subplot()
ax.imshow(img_rgb)
for pt in zip(*loc[::-1]):
	# cv2.rectangle(img_rgb, pt, (pt[0]+w, pt[1]+h), (255,0,0), 1)
	r = mpl.patches.Rectangle(pt, w, h, fill=False)
	ax.add_patch(r)

plt.show()
# cv2.imshow("Matched", img_rgb)
# cv2.waitKey()
# cv2.destroyAllWindows()