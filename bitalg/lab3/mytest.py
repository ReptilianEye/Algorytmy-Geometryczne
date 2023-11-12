import operator
from collections import namedtuple
import bisect

polygon_example_1 = [(5, 5), (3, 4), (6, 3), (4, 2), (6, 0), (7, 1), (8, 4)]
polygon_example_2 = [(2, 0), (5, 1), (6, 0), (8, 3), (7, 2), (8, 7), (6, 9), (5, 8),
                     (2, 9), (1, 7), (2, 4), (4, 5), (3, 6), (5, 7), (5.5, 3), (2, 2), (1, 3), (0, 1)]
polygon_example_colors = [1, 3, 1, 0, 2, 4, 0, 2, 0, 4, 1, 4, 4, 3, 4, 2, 0, 4]
polygon_example_tri = [(polygon_example_1[0], polygon_example_1[2]),
                       (polygon_example_1[2], polygon_example_1[5]),
                       (polygon_example_1[2], polygon_example_1[6]),
                       #   (polygon_example_1[6], polygon_example_1[3]),
                       (polygon_example_1[2], polygon_example_1[4]),
                       ]


def prevNbour(i, n): return i-1 if i > 0 else n-1
def nextNbour(i, n): return (i+1) % n


def mat_det(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    return (bx-ax)*(cy-by)-(by-ay)*(cx-bx)


def orient(a, b, c, eps=0):
    """
    Celem funkcji jest stworzenie porządku dla punktów. Sprawdza czy mniejszy kąt względem osi OX tworzy prosta ab czy ac
    """
    det = mat_det(a, b, c)
    if abs(det) <= eps:
        return 0
    if det < eps:
        return 1
    return -1


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


def color_vertex(polygon, colors=COLORS_LABELS):
    """

    Funkcja dzieli wierzchołki na kategorie i przypisuje wierzchołkom odpowiednie numery: 0 - początkowy, 1 - końcowy, 2 - łączący, 3 - dzielący, 4 - prawdiłowy
    :param polygon: tablica krotek punktów na płaszczyźnie euklidesowej podanych przeciwnie do ruchu wskazówek zegara - nasz wielokąt
    :return: tablica o długości n, gdzie n = len(polygon), zawierająca cyfry z przedziału 0 - 4, gdzie T[i] odpowiada kategorii i-tego wierzchołka.
    """
    n = len(polygon)
    categorized = [0 for _ in range(n)]
    pointsSortedByY = [i for i in range(n)]
    pointsSortedByY = sorted(pointsSortedByY, key=lambda x: -polygon[x][1])
    for p in pointsSortedByY:
        leftP = polygon[nextNbour(p, n)]
        midP = polygon[p]
        rightP = polygon[prevNbour(p, n)]
        if midP[1] > max(leftP[1], rightP[1]):
            # starting - rightP -> midP -> leftP turns to the left => det(left,p,right) > 0
            if mat_det(rightP, midP, leftP) > 0:
                categorized[p] = colors["start"]
            # dividing
            else:
                categorized[p] = colors["divide"]
        elif midP[1] < min(leftP[1], rightP[1]):
            # ending - rightP -> midP -> leftP turns to the left => det(left,p,right) > 0
            if mat_det(rightP, midP, leftP) > 0:
                categorized[p] = colors["end"]
            # connect
            else:
                categorized[p] = colors["connect"]
        else:
            categorized[p] = colors["regular"]
    return categorized


def onLeftSideOfPolygon(polygon):
    n = len(polygon)
    result = [False for _ in range(n)]
    p = find_index_of_highest(polygon)
    p = nextNbour(p, n)
    last = find_index_of_highest(polygon, reversed=True)
    while p != last:
        result[p] = True
        p = nextNbour(p, n)

    return result


class Edge:
    def __init__(self, a, b, helperIdx=None) -> None:
        self.diag = sorted([a, b])
        self.helperIdx = helperIdx
        self.__orderKey = self.firstToRight(0)

    def firstToRight(self, key=0):
        func = min if key == 0 else max
        return self.__closestCoordinate(func, key)

    def firstToLeft(self, key=0):
        func = max if key == 0 else min
        return self.__closestCoordinate(func, key)

    def __closestCoordinate(self, func, key):
        return func(self.diag, key=lambda x: x[key])[key]

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
    EdgeQuery = namedtuple("EdgeQuery", ["func", "operator", "coordinate"])

    def createLeftEdge(self, point_idx, helper_idx=None):
        # polygon = self.polygon
        # n = len(polygon)
        # candidates = [polygon[prevNbour(point_idx, n)],
        #               polygon[nextNbour(point_idx, n)]]
        # if max(candidates, key=lambda x: x[0])[0] < polygon[point_idx][0]:
        #     return Edge(polygon[point_idx], max(candidates,key=lambda x:x[1]), helper_idx)
        # else:
        #     return Edge(polygon[point_idx], min(candidates,key=lambda x:x[0]), helper_idx)

        return self.__createEdge(point_idx, self.EdgeQuery(min, operator.le, 0), helper_idx=helper_idx)

    def createRightEdge(self, point_idx, helper_idx=None):
        return self.__createEdge(point_idx, self.EdgeQuery(max, operator.ge, 0), helper_idx=helper_idx)

    def createHigherEdge(self, point_idx, helper_idx=None):
        return self.__createEdge(point_idx, self.EdgeQuery(max, operator.ge, 1), helper_idx=helper_idx)

    def createLowerEdge(self, point_idx, helper_idx=None):
        return self.__createEdge(point_idx, self.EdgeQuery(min, operator.le, 1), helper_idx=helper_idx)

    def __createEdge(self, point_idx, params: EdgeQuery, helper_idx=None):
        polygon = self.polygon
        n = len(polygon)
        coordinate = params.coordinate
        secondCoordinate = 1-coordinate
        relate = params.operator
        func = params.func
        help_func = max if func.__name__ == "min" else min
        candidates = [polygon[prevNbour(point_idx, n)],
                      polygon[nextNbour(point_idx, n)]]
        # if both candidates are on the same side of the point - we return higher/lower edge
        if relate(help_func(candidates, key=lambda x: x[coordinate])[coordinate], polygon[point_idx][coordinate]):
            return Edge(polygon[point_idx], help_func(candidates, key=lambda x: x[secondCoordinate]), helper_idx)
            #     return Edge(polygon[point_idx], max(candidates,key=lambda x:x[1]), helper_idx)
        #     return Edge(polygon[point_idx], min(candidates,key=lambda x:x[0]), helper_idx)
        return Edge(polygon[point_idx], func(candidates, key=lambda x: x[coordinate]), helper_idx)
        # second = func(polygon[prevNbour(point_idx, n)],
        #               polygon[nextNbour(point_idx, n)], key=lambda x: x[coordinate])
        # return Edge(polygon[point_idx], second, helper_idx)

    def getPointLabel(self, point_idx):
        if point_idx == None:
            return None
        return self.labels[self.pointsColors[point_idx]]

    def __findFirstLeftEdgeFromX(self, x) -> Edge:

        # toFind = Edge((x, 0), (x, 0))
        # x = x
        A = [e.firstToLeft(0) for e in self.tree]
        i = bisect.bisect(A, x)
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
            found = self.tree[found_idx]
            if found.firstToLeft(1) < self.polygon[point_idx][1]:
                return found
            self.tree.pop(found_idx)


def divideToMonotonicPolygons(polygon, colors=COLORS_LABELS):
    labels = dict((v, k) for k, v in colors.items())
    n = len(polygon)
    colors = color_vertex(polygon)

    isPointOnLeft = onLeftSideOfPolygon(polygon)
    # Struktura zdarzeń
    PointsOrder = [i for i in range(n)]
    PointsOrder = sorted(
        PointsOrder, key=lambda x: (-polygon[x][1], polygon[x][0]))

    # Struktura stanu
    BSC = TriBST(polygon, colors)  # BroomStateController

    newDiagonals = []

    for v in PointsOrder:
        currentLabel = BSC.getPointLabel(v)
        if currentLabel == START:
            leftEdge = BSC.createLeftEdge(v, v)
            BSC.insertEdge(leftEdge)

        elif currentLabel == END:
            leftEdge = BSC.createLeftEdge(v)
            helperIdx = BSC.getEdgeHelper(leftEdge)
            if BSC.getPointLabel(helperIdx) == CONNECT:
                new = (v, helperIdx)
                newDiagonals.append(new)
            BSC.removeEdge(leftEdge)

        elif currentLabel == DIVIDE:
            leftEdgeFromBroom = BSC.findFirstToTheLeft(v)  # ev
            helperIdx = BSC.getEdgeHelper(leftEdgeFromBroom)
            new = (v, helperIdx)
            newDiagonals.append(new)
            leftEdgeFromBroom.helperIdx = v
            rightEdge = BSC.createRightEdge(v, v)
            BSC.insertEdge(rightEdge)

        elif currentLabel == CONNECT:
            rightEdge = BSC.createRightEdge(v)
            helperIdx = BSC.getEdgeHelper(rightEdge)
            if labels[colors[helperIdx]] == CONNECT:
                new = (v, helperIdx)
                newDiagonals.append(new)
            BSC.removeEdge(rightEdge)
            leftEdgeFromBroom = BSC.findFirstToTheLeft(v)
            helperIdx = BSC.getEdgeHelper(leftEdgeFromBroom)
            if BSC.getPointLabel(helperIdx) == CONNECT:
                new = (v, helperIdx)
                newDiagonals.append(new)
            leftEdgeFromBroom.helperIdx = v

        elif currentLabel == REGULAR:
            if isPointOnLeft[v]:
                higherEdge = BSC.createHigherEdge(v)
                helperIdx = BSC.getEdgeHelper(higherEdge)
                if helperIdx != None:
                    if BSC.getPointLabel(helperIdx) == CONNECT:
                        new = (v, helperIdx)
                        newDiagonals.append(new)
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


newDiag = divideToMonotonicPolygons(polygon_example_2)
# newDiag
