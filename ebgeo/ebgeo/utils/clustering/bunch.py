class Bunch(object):
    """
    A bunch is a list of objects which knows its center point,
    determined as the average of its objects' points. It's a useful
    data structure for clustering.
    """
    __slots__ = ["objects", "center", "points"]

    def __init__(self, obj, point):
        self.objects = []
        self.points = []
        self.center = (0, 0)
        self.add_obj(obj, point)

    def add_obj(self, obj, point):
        """Add an object and point, and update self.center.
        """
        self.objects.append(obj)
        self.points.append(point)
        self.update_center()

    def update_center(self):
        """Recalculates the center coordinate based on self.points.
        """
        # This runs in O(N), but it gets called for
        # every point you add to the cluster, so overall time to
        # create a Bunch of size N is nearly O(N**2).
        # That's probably fine as long as bunches are reasonably small...
        # Could maybe do something O(1) like (untested): 
        # new_center_x = ((self.center[0] * old_len) + new_x) / new_len
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        self.center = (sum(xs) * 1.0 / len(self.objects), sum(ys) * 1.0 / len(self.objects))

    @property
    def x(self):
        return self.center[0]

    @property
    def y(self):
        return self.center[1]
        
    def __repr__(self):
        objs = list.__repr__(self.objects[:3])
        if len(self.objects) > 3:
            objs = objs[:-1] + ", ...]"
        return u"<Bunch: %s, center: (%.3f, %.3f)>" % (objs, self.x, self.y)
