class Point:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __hash__(self):
        return hash(self.id)


class Edge:
    def __init__(self, id, p, q):
        self.id = id
        self.p = p
        self.q = q

        self.num_intersections = 0
        self.color = None
        self.crossed_edges = []

    def __hash__(self):
        return hash(self.id)
