import cv2
import numpy as np


class Target:

    def __init__(self, color=None, stats=None, centroid=None):
        self._stats = (self._x, self._y, self._width, self._height, self._area) = stats
        self._center_pos = (self._center_x, self._center_y) = int(centroid[0]), int(centroid[1])
        self._color = color

    def __init__(self, color=None, contour=None):
        (self._x, self._y, self._width, self._height) = cv2.boundingRect(contour)
        self._area = cv2.contourArea(contour)
        self._center_pos = (self._center_x, self._center_y) = (self._x+(self._width//2), self._y+(self._height//2))
        self._color = color

    def get_target_roi(self, src, pad=0, visualization=False) -> np.ndarray:
        shape = (h,w) = src.shape[:2]
        min_x = self._x - pad
        max_x = self._x + self._width + pad
        min_y = self._y - pad
        max_y = self._y + self._height + pad

        min_x = 0 if min_x <= 0 else min_x
        max_x = w-1 if max_x >= w-1 else max_x
        min_y = 0 if min_y <= 0 else min_y
        max_y = h-1 if max_y >= h-1 else max_y

        roi = src[min_y:max_y, min_x:max_x]

        if visualization:
            dst = cv2.circle(src, self._center_pos, 10, (255, 255, 255), 10)
            cv2.rectangle(dst, (self._x, self._y), (self._x + self._width, self._y + self._height), (0, 0, 255))
            if pad > 0: cv2.rectangle(dst, (min_x, min_y), (max_x, max_y), (255, 255, 255))
            cv2.imshow("target", dst)
            cv2.imshow("target_roi", roi)
            cv2.waitKey(1)

        return roi

    def get_center_pos(self):
        return self._center_pos

    def get_area(self):
        return self._area

def setLabel(src, pts, label):
    (x, y, w, h) = cv2.boundingRect(pts)
    pt1 = (x, y)
    pt2 = (x+w, y+h)
    cv2.rectangle(src, pt1, pt2, (0,255,0), 2)
    cv2.putText(src, label, (pt1[0], pt1[1]-3), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255))

if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from imutils import auto_canny
    from Sensor.HashDetector import HashDetector
    imageProcessor = ImageProcessor(video_path='src/S.h264')
    hashDetector = HashDetector()
    while True:
        targets = []
        src = imageProcessor.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = auto_canny(mask)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True)*0.02, True)
            vertice = len(approx)

            if vertice == 4 and cv2.contourArea(cnt)> 2500:
                targets.append(Target(contour=cnt))
        if targets:
            targets.sort(key= lambda x: x.get_area)
            roi = targets[0].get_target_roi(src = src, pad=10, visualization=True)
            print(hashDetector.detect_direction_hash(roi))

        #cv2.imshow("src", src)
        #cv2.imshow("mask", mask)
        #cv2.waitKey(1)


