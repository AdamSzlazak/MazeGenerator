import heapq


class AStarQueue(object):
    def __init__(self):
        self.myheap = []

    def show(self):
        return self.myheap

    def push(self, priority, distance, node):
        heapq.heappush(self.myheap, (priority, distance, node))

    def pop(self):
        priority, distance, node = heapq.heappop(self.myheap)
        return priority, distance, node


# Create a priority queue
class PriorityQueue(object):
    def __init__(self):
        self.myheap = []

    def show(self):
        return self.myheap

    def push(self, priority, node):
        heapq.heappush(self.myheap, (priority, node))

    def pop(self):
        priority, node = heapq.heappop(self.myheap)
        return priority, node
