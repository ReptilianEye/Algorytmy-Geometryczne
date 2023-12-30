from dataclasses import dataclass
from numpy import sqrt
# from beachline import Node

SITE_EVENT = 'site'
CIRCLE_EVENT = 'circle'


class Node:
    def __init__(self):
        self.arc = None
        self.arc_pair: Pair = None
        self.parent = None
        self.left = None
        self.right = None
        self.prev = None
        self.next = None

    def parabolaIntersectX(self):
        return self.arc_pair.parabolaIntersect()


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y


class Edge:
    def __init__(self, start: Point, direction: Point):
        self.start = start
        self.direction = direction
        self.twin = None
        self.end = None

    def close_edge(self, end: Point):
        self.end = end


class Arc:
    directrix: float

    objects = []

    def __init__(self, focus):
        self.focus = focus
        self.circle_event = None
        self.edgeGoingLeft = None
        self.edgeGoingRight = None
        self.a = None
        self.b = None
        self.c = None
        if self.directrix is not None:
            self.updateABC()
        self.__class__.objects.append(self)

    # def setEdgesWithHigher(self, higher_arc):
    #     start_x = self.focus.x
    #     start = Point(start_x, higher_arc.__unit_val(start_x))
    #     left_intersection, right_intersection = self.lookupIntersectionsWithHigher(
    #         higher_arc)
    #     leftEdge = Edge(start, left_intersection)
    #     rightEdge = Edge(start, right_intersection)
    #     leftEdge.twin = rightEdge
    #     rightEdge.twin = leftEdge
    #     self.edgeGoingLeft = leftEdge
    #     self.edgeGoingRight = rightEdge

    def setRightEdge(self, side_arc, start=None):
        if start is None:
            start_x = self.focus.x
            start = Point(start_x, side_arc.__unit_val(start_x))
        right_intersection = self.lookForIntersectionBetween(side_arc)
        rightEdge = Edge(start, right_intersection)
        # leftEdge = self.edgeGoingLeft
        # leftEdge.twin = rightEdge
        # rightEdge.twin = leftEdge
        side_arc.edgeGoingLeft = rightEdge
        self.edgeGoingRight = rightEdge

    def setLeftEdge(self, side_arc, start=None):
        if start is None:
            start_x = self.focus.x
            start = Point(start_x, side_arc.__unit_val(start_x))

        left_intersection = side_arc.lookForIntersectionBetween(self)
        leftEdge = Edge(start, left_intersection)
        # rightEdge = self.edgeGoingRight
        # leftEdge.twin = rightEdge
        # rightEdge.twin = leftEdge
        side_arc.edgeGoingRight = leftEdge
        self.edgeGoingLeft = leftEdge

    @classmethod
    def setDirectrix(cls, directrix, all=True):
        cls.directrix = directrix
        if all:
            for obj in cls.objects:
                obj.updateABC()

    def updateABC(self):
        if self.focus.y == self.directrix:
            return
        f = abs(self.focus.y - self.directrix)/2.0
        vertex = Point(self.focus.x, self.focus.y - f)
        self.a = 1.0 / (4*f)
        self.b = -vertex.x / (2*f)
        self.c = vertex.x**2 / (4*f) + vertex.y

    def __unit_val(self, x):
        # if self.a is None or self.b is None or self.c is None:
        #     self.updateABC()
        return self.a*x**2 + self.b*x + self.c
        # return x**2/(4*f) + -vertex.x*x/(2*f) + vertex.x**2/(4*f) + vertex.y
        # return 1.0 / (2*(self.focus.y - self.directrix)) * (x - self.focus.x)**2 + (self.focus.y + self.directrix)/2.0

    def value(self,  x, directrix=None):
        if directrix is not None:
            self.setDirectrix(directrix)
        # self.directrix = directrix
        # self.updateABC()
        return [self.__unit_val(x) for x in x]

    def lookForIntersectionBetween(self, right_arc):
        prevDirectrix = self.directrix
        self.setDirectrix(prevDirectrix-1, False)
        self.updateABC()
        right_arc.updateABC()
        found_intersect = self.intersect(right_arc)
        self.setDirectrix(prevDirectrix, False)
        self.updateABC()
        right_arc.updateABC()
        return found_intersect

    def lookupIntersectionsWithHigher(self, higher):
        return higher.lookForIntersectionBetween(self), self.lookForIntersectionBetween(higher)

    def intersect(self, arc) -> Point:
        a = self.a - arc.a
        b = self.b - arc.b
        c = self.c - arc.c
        x = (-b + sqrt(b**2 - 4*a*c))/(2*a)
        return Point(x, self.__unit_val(x))


@dataclass
class Event:
    type: str
    point: Point = None
    node: Node = None
    false_alarm: bool = False


class Pair:
    # left: Arc
    # right: Arc

    def __init__(self, left: Arc, right: Arc):
        self.left = left
        self.right = right
        # higher_arc = max([left, right], key=lambda p: p.focus.y)
        # lower_arc = min([left, right], key=lambda p: p.focus.y)
        # start_x = lower_arc.focus.x
        # self.start = Point(start_x, higher_arc.value(start_x))

    def parabolaIntersect(self):
        return self.left.intersect(self.right).x
