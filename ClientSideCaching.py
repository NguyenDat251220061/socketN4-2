import os
import pickle
from PIL import Image


class ClientSideCaching:
    def __init__(self, maxSize):
        self.maxSize = maxSize
        self.buffer = {}
        self.accessCounter = 0
        self.accessOrder = {}
        self.oldestKey = None

    def getFrame(self, frameNumber, sessionId):
        key = self.makeKey(frameNumber, sessionId)

        if key in self.buffer:
            if key == self.oldestKey:
                self.updateOldestKey()

            return self.buffer[key]
        else:
            return None

    def cacheFrame(self, frameNumber, sessionId, frameData):
        key = self.makeKey(frameNumber, sessionId)

        if key in self.buffer:
            self.accessOrder[key] = self.accessCounter
            self.accessCounter += 1

            if key == self.oldestKey:
                self.updateOldestKey()
            return

        else:
            print("Caching frame {}".format(frameNumber))
            self.buffer[key] = frameData
            self.accessOrder[key] = self.accessCounter
            self.accessCounter += 1

            if len(self.buffer) > self.maxSize:
                self.evictOldest()
            if len(self.buffer) == 1:
                self.oldestKey = key
            elif self.accessOrder[key] < self.accessOrder[self.oldestKey]:
                self.oldestKey = key

    def makeKey(self, frameNumber, sessionId):
        return (frameNumber, sessionId)

    def clear(self):

        self.buffer.clear()
        self.accessOrder.clear()
        self.accessCounter = 0
        self.oldestKey = None

    def evictOldest(self):
        if not self.accessOrder:
            return

        if self.oldestKey is None or self.oldestKey not in self.accessOrder:
            self.updateOldestKey()

        if self.oldestKey:
            del self.accessOrder[self.oldestKey]
            del self.buffer[self.oldestKey]

            self.updateOldestKey()

    def updateOldestKey(self):
        if not self.accessOrder:
            self.oldestKey = None
            return

        self.oldestKey = min(self.accessOrder.items(), key=lambda x: x[1])[0]

    def getCachedFrames(self, sessionId):
        return [
            frameNumber for (frameNumber, sessId) in self.buffer.keys()
            if sessId == sessionId
        ]

    def getStats(self):
        return {
            'cached_frames': len(self.buffer),
            'max_size': self.maxSize,
            'access_counter': self.accessCounter,
            'oldest_key': self.oldestKey
        }