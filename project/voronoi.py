from priorityqueue import PriorityQueue
from beachline import Beachline
from datatypes import *
# beachline
# insert, delete, find arc by x coordinate
# Na razie może być linkedlita


class Voronoi:
    def __init__(self, points):
        self.points = map(lambda p: Point(*p), points)
        self.Q = PriorityQueue()
        self.T = Beachline()
        self.D = []

    def get_voronoi(self):
        Q = self.Q
        T = self.T
        D = self.D
        for p in self.points:
            Q.add(Event(SITE_EVENT, point=p))
        # print(Q.heap)
        while Q:
            event = Q.pop()
            Arc.setDirectrix(event.point.y)
            if event.type == SITE_EVENT:
                self.handleSiteEvent(event.point)
            else:
                self.handleCircleEvent(event)

    def handleSiteEvent(self, p):
        T = self.T
        Q = self.Q
        D = self.D

        arc_above_node, left_circle_event, right_circle_event = T.insert(p)
        if arc_above_node is None:
            return
        # arc = Arc(p)
        # if not T:
        #     T.insert(arc)
        #     return

        # # Find arc above p
        # arcAbove = T.find_node(p)

        if arc_above_node.arc.circle_event != None:
            Q.delete(arc_above_node.arc.circle_event)

        # afl, afr = T.replace(arcAbove, arc)

        if left_circle_event != None:
            Q.add(left_circle_event)
        if right_circle_event != None:
            Q.add(right_circle_event)

    def handleCircleEvent(self, event):
        T = self.T
        Q = self.Q
        leaf: Node = event.node
        point: Point = event.point
        lnode: Node = T.leftNbour(leaf)
        rnode: Node = T.rightNbour(leaf)
        al: Arc = lnode.arc
        ar: Arc = rnode.arc

        closedLeft = leaf.arc.edgeGoingLeft
        closedRight = leaf.arc.edgeGoingRight

        closedLeft.end = point
        closedRight.end = point
        self.D.append((closedLeft.start, closedLeft.end))
        self.D.append((closedRight.start, closedRight.end))

        al.setRightEdge(ar, point)
        # ar.setLeftEdge(al, point) # not needed because setRightEdge does it

        # leftEdge = al.edgeGoingLeft
        # rightEdge = ar.edgeGoingRight
        # leftEdge.end = point
        # rightEdge.end = point

        left_circle_event, right_circle_event = T.handleSquize(leaf)
        if left_circle_event != None:
            Q.add(left_circle_event)
        if right_circle_event != None:
            Q.add(right_circle_event)
