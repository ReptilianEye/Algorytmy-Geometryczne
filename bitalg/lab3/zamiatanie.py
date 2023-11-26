import numpy as np
import bisect
import operator
from collections import namedtuple


def prevNbour(i, n): return i-1 if i > 0 else n-1


def nextNbour(i, n): return (i+1) % n


def is_y_monotonic(polygon, return_chain=False):
    """
    Funkcja określa czy podana figura jest y-monotoniczna.
    :param polygon: tablica krotek punktów na płaszczyźnie euklidesowej podanych przeciwnie do ruchu wskazówek zegara - nasz wielokąt
    :return: wartość bool - true, jeśli wielokąt jest monotoniczny i false jeśli nie jest
    """
    n = len(polygon)

    if n < 4:
        return True
    pTop = find_index_of_highest(polygon)
    pBottom = find_index_of_highest(polygon, reversed=True)
    i = nextNbour(pTop, n)
    prev_y = polygon[pTop][1]
    leftChain = []
    while i != pBottom:
        curr_y = polygon[i][1]
        leftChain.append(i)
        if curr_y > prev_y:
            return False
        prev_y = curr_y
        i = nextNbour(i, n)
    i = prevNbour(pTop, n)
    prev_y = polygon[pTop][1]
    rightChain = []
    while i != pBottom:
        curr_y = polygon[i][1]
        rightChain.append(i)
        if curr_y > prev_y:
            return False
        prev_y = curr_y
        i = prevNbour(i, n)

    chain = [pTop]
    i = 0
    j = 0
    while i < len(leftChain) and j < len(rightChain):
        if polygon[leftChain[i]][1] > polygon[rightChain[j]][1]:
            chain.append(leftChain[i])
            i += 1
        else:
            chain.append(rightChain[j])
            j += 1
    while i < len(leftChain):
        chain.append(leftChain[i])
        i += 1
    while j < len(rightChain):
        chain.append(rightChain[j])
        j += 1
    chain.append(pBottom)
    if return_chain:
        return True, chain
    return True


# Labels consts
START = "start"
END = "end"
CONNECT = "connect"
DIVIDE = "divide"
REGULAR = "regular"
COLORS_LABELS = {START: 0, END: 1, CONNECT: 2, DIVIDE: 3, REGULAR: 4}


def find_index_of_highest(points, reversed=False, eps=0):
    p0_idx = 0
    p0 = points[0]
    def compare(x, y): return x > y if reversed else x < y
    for i in range(1, len(points)):
        if compare(p0[1], points[i][1]) or (abs(p0[1] - points[i][1]) <= eps and p0[0] > points[i][0]):
            p0 = points[i]
            p0_idx = i
    return p0_idx


def mat_det(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    return (bx-ax)*(cy-by)-(by-ay)*(cx-bx)


class Edge:
    def __init__(self, a, b, helperIdx=None) -> None:
        self.diag = sorted([a, b])
        self.helperIdx = helperIdx
        # self.__orderKey = self.firstToRight(0)
        self.__orderKey = self.orderKey()

    def orderKey(self):
        return min(self.diag, key=lambda x: x[0])[0]

    # def firstToRight(self, key=0):
    #     func = min if key == 0 else max
    #     return self.__closestCoordinate(func, key)

    # def firstToLeft(self, key=0):
    #     func = max if key == 0 else min
    #     return self.__closestCoordinate(func, key)

    # def __closestCoordinate(self, func, key):
    #     return func(self.diag, key=lambda x: x[key])[key]

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.diag == other.diag

    def __lt__(self, other):
        return self.__orderKey < other.__orderKey

    def __gt__(self, other):
        return self.__orderKey > other.__orderKey


class TriBST:

    def __init__(self, polygon, pointsColors, LABELS_COLORS=dict((v, k) for (k, v) in COLORS_LABELS.items())) -> None:
        self.tree = []
        self.polygon = polygon
        self.pointsColors = pointsColors
        self.labels = LABELS_COLORS

    def insertEdge(self, edge: Edge):
        bisect.insort(self.tree, edge)

    def getEdgeHelper(self, edge: Edge):
        if edge.helperIdx is not None:
            return edge.helperIdx
        edgeInState = self.__findEdge(edge)
        if edgeInState != None:
            return edgeInState.helperIdx

    def removeEdge(self, edge):
        i = self.__findEdgeIdx(edge)
        if i != None:
            self.tree.pop(i)

    def createLeftEdge(self, point_idx, helper_idx=None):
        return self.__create_edge_horizonally(point_idx, operator.ge, helper_idx=helper_idx)

    def createRightEdge(self, point_idx, helper_idx=None):
        return self.__create_edge_horizonally(point_idx, operator.le, helper_idx=helper_idx)

    def createHigherEdge(self, point_idx, helper_idx=None):
        return self.__create_edge_vertically(point_idx, "higher", helper_idx=helper_idx)

    def createLowerEdge(self, point_idx, helper_idx=None):
        return self.__create_edge_vertically(point_idx, "lower", helper_idx=helper_idx)

    def __create_edge_vertically(self, point_idx, higher_or_lower, helper_idx=None):
        """Always called with regular point!"""
        polygon = self.polygon
        n = len(polygon)
        func = max if higher_or_lower == "higher" else min
        return Edge(self.polygon[point_idx], func([polygon[prevNbour(point_idx, n)],
                                                  polygon[nextNbour(point_idx, n)]], key=lambda x: x[1]), helper_idx)

    def __create_edge_horizonally(self, point_idx, relate, helper_idx=None):
        polygon = self.polygon
        n = len(polygon)
        which = "left" if relate == operator.ge else "right"
        candidates = np.array([polygon[prevNbour(point_idx, n)],
                               polygon[nextNbour(point_idx, n)]])
        # if self.getPointLabel(point_idx) in [CONNECT, END]:
        #     vert_beetween_neighbours = (
        #         vert_beetween_neighbours[0], polygon[point_idx][1]-1)

        vert_beetween_neighbours = tuple(np.mean(candidates, axis=0))
        if self.getPointLabel(point_idx) in [START, DIVIDE]:
            relate = operator.le if relate == operator.ge else operator.ge

        for candidate in candidates:
            candidate = tuple(candidate)
            if relate(mat_det(polygon[point_idx],  vert_beetween_neighbours, candidate), 0):
                return Edge(polygon[point_idx], candidate, helper_idx)

    def getPointLabel(self, point_idx):
        if point_idx == None:
            return None
        return self.labels[self.pointsColors[point_idx]]

    def __findFirstLeftEdgeFromX(self, x) -> Edge:
        # A = [e.orderKey() for e in self.tree]
        x = Edge((x, 0), (x, 0))
        i = bisect.bisect(self.tree, x)
        if i != 0:
            return i-1

    def __findEdgeIdx(self, edge: Edge) -> int:
        i = bisect.bisect(self.tree, edge)
        if i < len(self.tree) and self.tree[i] == edge:
            return i
        if i > 0 and self.tree[i-1] == edge:
            return i-1

    def __findEdge(self, edge: Edge) -> Edge:
        i = self.__findEdgeIdx(edge)
        if i != None:
            return self.tree[i]

    def findFirstToTheLeft(self, point_idx):
        while len(self.tree) > 0:
            found_idx = self.__findFirstLeftEdgeFromX(
                self.polygon[point_idx][0])
            found: Edge = self.tree[found_idx]
            if found is not None and min(found.diag, key=lambda x: x[1])[1] < self.polygon[point_idx][1]:
                return found
            self.tree.pop(found_idx)


def onLeftSideOfPolygon(polygon):
    n = len(polygon)
    result = [False for _ in range(n)]
    p = find_index_of_highest(polygon)
    result[p] = True
    p = nextNbour(p, n)
    last = find_index_of_highest(polygon, reversed=True)
    result[last] = True
    while p != last:
        result[p] = True
        p = nextNbour(p, n)

    return result


def color_vertex(polygon, colors=COLORS_LABELS):
    """

    Funkcja dzieli wierzchołki na kategorie i przypisuje wierzchołkom odpowiednie numery: 0 - początkowy, 1 - końcowy, 2 - łączący, 3 - dzielący, 4 - prawdiłowy
    :param polygon: tablica krotek punktów na płaszczyźnie euklidesowej podanych przeciwnie do ruchu wskazówek zegara - nasz wielokąt
    :return: tablica o długości n, gdzie n = len(polygon), zawierająca cyfry z przedziału 0 - 4, gdzie T[i] odpowiada kategorii i-tego wierzchołka.
    """
    n = len(polygon)
    categorized = [0 for _ in range(n)]
    for p in range(n):
        leftP = polygon[nextNbour(p, n)]
        midP = polygon[p]
        rightP = polygon[prevNbour(p, n)]
        if midP[1] >= max(leftP[1], rightP[1]):
            # starting - rightP -> midP -> leftP turns to the left => det(left,p,right) > 0
            if mat_det(rightP, midP, leftP) > 0:
                categorized[p] = colors["start"]
            # dividing
            else:
                categorized[p] = colors["divide"]
        elif midP[1] <= min(leftP[1], rightP[1]):
            # ending - rightP -> midP -> leftP turns to the left => det(left,p,right) > 0
            if mat_det(rightP, midP, leftP) > 0:
                categorized[p] = colors["end"]
            # connect
            else:
                categorized[p] = colors["connect"]
        else:
            categorized[p] = colors["regular"]
    return categorized


def checkAndAppendDiagonal(newDiagonals, v, helperIdx, n):
    if nextNbour(helperIdx, n) != v and prevNbour(helperIdx, n) != v:
        new = (v, helperIdx)
        newDiagonals.append(new)


def divideToMonotonicPolygons(polygon, colors=COLORS_LABELS):
    if is_y_monotonic(polygon):
        return []
    labels = dict((v, k) for k, v in colors.items())
    n = len(polygon)
    colors = color_vertex(polygon)

    isPointOnLeft = onLeftSideOfPolygon(polygon)
    # Struktura zdarzeń
    pointsOrder = [i for i in range(n)]
    pointsOrder = sorted(
        pointsOrder, key=lambda x: (-polygon[x][1], polygon[x][0]))

    # Struktura stanu
    BSC = TriBST(polygon, colors)  # BroomStateController

    newDiagonals = []

    for v in pointsOrder:
        currentLabel = BSC.getPointLabel(v)
        if currentLabel == START:
            leftEdge = BSC.createLeftEdge(v, v)
            BSC.insertEdge(leftEdge)

        elif currentLabel == END:
            leftEdge = BSC.createLeftEdge(v)
            helperIdx = BSC.getEdgeHelper(leftEdge)
            if BSC.getPointLabel(helperIdx) == CONNECT:
                checkAndAppendDiagonal(newDiagonals, v, helperIdx, n)
            BSC.removeEdge(leftEdge)

        elif currentLabel == DIVIDE:
            leftEdgeFromBroom = BSC.findFirstToTheLeft(v)  # ev
            helperIdx = BSC.getEdgeHelper(leftEdgeFromBroom)
            checkAndAppendDiagonal(newDiagonals, v, helperIdx, n)
            leftEdgeFromBroom.helperIdx = v
            rightEdge = BSC.createRightEdge(v, v)
            BSC.insertEdge(rightEdge)

        elif currentLabel == CONNECT:
            rightEdge = BSC.createRightEdge(v)
            helperIdx = BSC.getEdgeHelper(rightEdge)
            if helperIdx != None:
                if labels[colors[helperIdx]] == CONNECT:
                    checkAndAppendDiagonal(newDiagonals, v, helperIdx, n)
                BSC.removeEdge(rightEdge)
            leftEdgeFromBroom = BSC.findFirstToTheLeft(v)
            helperIdx = BSC.getEdgeHelper(leftEdgeFromBroom)
            if BSC.getPointLabel(helperIdx) == CONNECT:
                checkAndAppendDiagonal(newDiagonals, v, helperIdx, n)
            leftEdgeFromBroom.helperIdx = v

        elif currentLabel == REGULAR:
            if isPointOnLeft[v]:
                higherEdge = BSC.createHigherEdge(v)
                helperIdx = BSC.getEdgeHelper(higherEdge)
                if helperIdx != None:
                    if BSC.getPointLabel(helperIdx) == CONNECT:
                        checkAndAppendDiagonal(newDiagonals, v, helperIdx, n)
                    BSC.removeEdge(higherEdge)
                new = BSC.createLowerEdge(v, v)
                BSC.insertEdge(new)
            else:
                leftEdgeFromBroom = BSC.findFirstToTheLeft(v)
                helperIdx = BSC.getEdgeHelper(leftEdgeFromBroom)
                if BSC.getPointLabel(helperIdx) == CONNECT:
                    new = (v, helperIdx)
                    newDiagonals.append(new)
                leftEdgeFromBroom.helperIdx = v

    return newDiagonals


polygon = [(3, 0), (5, 5), (4, 7), (3.5, 4.5), (3, 4), (2, 4), (0, 5.5)]
# polygon = [(2, 0), (5, 1), (6, 0), (8, 3), (7, 2), (8, 7), (6, 9), (5, 8),
#            (2, 9), (1, 7), (2, 4), (4, 5), (3, 6), (5, 7), (5.5, 3), (2, 2), (1, 3), (0, 1)]
polygon = [(2, 0), (2, 2), (0.75, 2), (1.25, 1.5), (0.5, 1), (1, 0.5), (0, 0)]
polygon = [[3.9919354838709675, 3.6087622549019613], [3.459677419354839, 0.42401960784313686], [4.912298387096774, 0.9969362745098038], [4.213709677419355, 1.3170955882352937], [
    4.790322580645162, 1.7552083333333333], [4.357862903225806, 1.9911151960784312], [4.745967741935484, 2.412377450980392], [4.513104838709678, 2.5808823529411766], [4.856854838709678, 3.103247549019608]]
polygon = [[0.7862903225806451, 0.7199754901960784], [0.592741935483871, 0.8517156862745099], [0.5201612903225806, 0.5330882352941175], [0.3931451612903226,
                                                                                                                                         0.41053921568627444], [0.25604838709677413, 0.41053921568627444], [0.11088709677419353, 0.4534313725490196], [0.5362903225806451, 0.039828431372548934]]
polygon = [tuple(el) for el in polygon]
print(polygon)
print(divideToMonotonicPolygons(polygon))
