import cv2 as cv
import numpy as np
import math


class FrameSelector:
    def __init__(self, batch=10):
        self.batch = batch

    def read_frames(self, video_path):
        frames = []
        capture = cv.VideoCapture(video_path)
        fps = int(capture.get(cv.CAP_PROP_FPS))
        if capture.isOpened() is False:
            raise Exception("Cannot open video!")
        while capture.isOpened():
            ret, frame = capture.read()
            if ret:
                frames.append(frame)
            else:
                break
        capture.release()
        return frames, fps

    def blur_filter(self, frames, top):
        variance = np.array([])

        for frame in frames:
            variance = np.append(variance, cv.Laplacian(frame, cv.CV_64F).var())

        p = np.percentile(variance, (1 - top) * 100)

        selected_frames = []
        for frame, var in zip(frames, variance):
            if var > p:
                selected_frames.append(frame)

        return selected_frames

    def filter_blur_frames(self, frames, top):
        selected_frames = []
        frames = np.stack(frames)
        n_batches = math.ceil(frames.shape[0] / self.batch)
        for idx in range(n_batches):
            selected_frames.extend(
                self.blur_filter(
                    frames[idx * self.batch: idx * self.batch + self.batch],
                    top,
                )
            )
        return selected_frames

    def select(self, video_path, top=0.1):
        frames, fps = self.read_frames(video_path)
        selected_frames = self.filter_blur_frames(frames, top)
        return frames, selected_frames
