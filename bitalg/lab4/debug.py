from queue import PriorityQueue
import bisect


def mat_det(a, b):
    return a[0] * b[1] - a[1] * b[0]


pointTypes = {
    "start": 0,
    "end": 1,
    "intersection": 2
}


class Point:
    def __init__(self, x, y, segment=None, type=None, payload=None, tolerance=12) -> None:
        self.tolerance = tolerance  # do 5 miejsc po przecinku
        self.x = x
        self.y = y
        self.segment = segment
        self.type = type
        self.key = round(self.x, tolerance), round(self.y, tolerance)
        self.payload = payload

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.key == other.key

    def __lt__(self, other):
        return self.y < other.y or (self.y == other.y and self.x < other.x)

    def __gt__(self, other):
        return self.y > other.y or (self.y == other.y and self.x > other.x)

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self) -> str:
        return f"({round(self.x,3)}, {round(self.y,3)})"
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return self.__str__()


globalX = 0


class Segment:
    id = 0

    def __init__(self, segment) -> None:
        p1, p2 = segment
        temp = p1
        p1 = min(p1, p2, key=lambda x: x[0])
        p2 = max(temp, p2, key=lambda x: x[0])
        p1 = Point(*p1, segment=self, type=pointTypes["start"])
        p2 = Point(*p2, segment=self, type=pointTypes["end"])
        self.p1 = p1
        self.p2 = p2
        self.xLimits = min(p1.x, p2.x), max(p1.x, p2.x)
        self.formula = self.get_formula()
        self.id = Segment.id
        Segment.id += 1

    def get_formula(self):
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        # returns as lambda function that takes x returns y
        if x1 == x2:
            return lambda x: None
        a = (y1 - y2) / (x1 - x2)
        b = y1 - a * x1
        return lambda x: a * x + b

    def key(self):
        # if self.xLimits[0] <= globalX <= self.xLimits[1]:
        return self.formula(globalX)
        return None

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.id == other.id

    def __lt__(self, other):
        return self.key() < other.key()

    def __gt__(self, other):
        return self.key() > other.key()

    def __str__(self) -> str:
        return f"({self.p1}, {self.p2})"

    def __repr__(self) -> str:
        return self.__str__()


def getIntersect(seg1: Segment, seg2: Segment):
    """
    Funkcja sprawdza czy dwa odcinki się przecinają
    :param seg1: odcinek 1
    :param seg2: odcinek 2
    :return: True jeśli odcinki się przecinają, False w przeciwnym wypadku
    """
    # Wyznaczenie punktów wspólnych
    x1, x2 = seg1.xLimits
    x3, x4 = seg2.xLimits
    y1, y2 = seg1.formula(x1), seg1.formula(x2)
    y3, y4 = seg2.formula(x3), seg2.formula(x4)
    # x1 = seg1[0][0]
    # x2 = seg1[1][0]
    # x3 = seg2[0][0]
    # x4 = seg2[1][0]
    # y1 = seg1[0][1]
    # y2 = seg1[1][1]
    # y3 = seg2[0][1]
    # y4 = seg2[1][1]
    # Wyznaczenie równań prostych
    den = mat_det([(x1-x2), (x3-x4)], [(y1-y2), (y3-y4)])
    if den == 0:
        return None
    t = mat_det([(x1-x3), (x3-x4)], [(y1-y3), (y3-y4)]) / den
    u = -mat_det([(x1-x2), (x1-x3)], [(y1-y2), (y1-y3)]) / den

    if 0 <= t <= 1 and 0 <= u <= 1:
        return Point(x1 + t*(x2-x1), y1 + t*(y2-y1), type=pointTypes["intersection"], payload=(seg1, seg2))
    return None


class TBST:
    def __init__(self) -> None:
        self.tree:  list[Segment] = []

    def insert(self, segment):
        # global globalX
        # globalX = x
        # if segment is None:
        #     yield Exception("segment is None")
        bisect.insort(self.tree, segment)

    def swap(self, intersect):
        # global globalX
        # closestX = max(intersect.payload,
        #    key=lambda p: p.xLimits[0]).xLimits[0]
        # globalX = closestX
        seq1, seq2 = intersect.payload
        # shadowSeg = Segment(((globalX-1, intersect.y),
        # (intersect.x+1, intersect.y)))
        i = self.find(seq1)
        # i = bisect.bisect_left(self.tree, seq1)
        # if self.tree[i] != seq1:
        #     i = self.find_by_hand(seq1)
        #     if i is None:
        #         raise Exception("not found")
        j = None
        if i + 1 < len(self.tree) and self.tree[i+1] == seq2:
            j = i+1
        elif i-1 >= 0 and self.tree[i-1] == seq2:
            j = i-1
        if j is None:
            j = self.find_by_hand(seq2)
        self.__swapInTree(i, j)
        toCheck = []
        lower, higher = min(i, j), max(i, j)
        if lower > 0:
            toCheck += [(self.tree[lower-1], self.tree[lower])]
        if higher < len(self.tree)-1:
            toCheck += [(self.tree[higher+1], self.tree[higher])]
        return toCheck

    def __swapInTree(self, aPos, bPos):
        # secondPointA = max(self.tree[aPos].segment, key=lambda p: p[0])
        # secondPointB = max(self.tree[bPos].segment, key=lambda p: p[0])
        # pointA = Point(x=secondPointA[0], y=secondPointA[1],
        #                segment=self.tree[aPos].segment, type=self.tree[aPos].type)
        # pointB = Point(x=secondPointB[0], y=secondPointB[1],
        #                segment=self.tree[bPos].segment, type=self.tree[bPos].type)
        # self.tree[bPos], self.tree[aPos] = pointA, pointB
        self.tree[bPos], self.tree[aPos] = self.tree[aPos], self.tree[bPos]

    def delete(self, segment):
        # toDelete = Segment(segment)
        # for i in range(len(self.tree)):
        #     if self.tree[i] == toDelete:
        #         self.tree.pop(i)
        #         return
        i = self.find(segment)
        # i = bisect.bisect_left(self.tree, segment)
        toCheck = []
        if i != 0 and i != len(self.tree)-1:
            toCheck += [(self.tree[i-1], self.tree[i+1])]
        # print(f"removing: {self.tree[i]}")
        self.tree.pop(i)
        return toCheck

    def find_by_hand(self, segment):
        for i in range(len(self.tree)):
            if self.tree[i] == segment:
                return i
        return None

    def getNbours(self, segment):
        res = []
        if len(self.tree) == 1:
            return res
        i = self.find(segment)
        # i = bisect.bisect_left(self.tree, segment)
        if i == 0:
            return [self.tree[i+1]]
        if i == len(self.tree)-1:
            return [self.tree[i-1]]
        return [self.tree[i-1], self.tree[i+1]]

    def find(self, segment):
        i = bisect.bisect_left(self.tree, segment)
        if 0 <= i < len(self.tree) and self.tree[i] == segment:
            return i
        i = self.find_by_hand(segment)
        if i is None:
            raise Exception("not found")
        return i


def is_intersection(sections):
    """
    Funkcja sprawdza czy jakakolwiek para podanych odcinków się przecina 
    :param sections: tablica odcinków w postaci krotek krotek współrzędnych punktów końcowych odcinków
    :return: True / False
    """
    Q = PriorityQueue()
    T = TBST()
    intersections = set()

    def checkAndhandleIntersection(sec1, sec2):
        intersect = getIntersect(sec1, sec2)
        if intersect:
            if intersect not in intersections:
                Q.put((intersect.key, intersect))
                intersections.add(intersect)

    for section in sections:
        segment = Segment(section)
        left = min(section, key=lambda x: x[0])
        leftP = Point(left[0], left[1], segment, pointTypes["start"])
        right = max(section, key=lambda x: x[0])
        rightP = Point(right[0], right[1], segment, pointTypes["end"])
        Q.put((leftP.key, leftP))
        Q.put((rightP.key, rightP))

    global globalX
    globalX = float("-inf")
    prevType = None
    while not Q.empty():
        point = Q.get()[1]
        if point.type == pointTypes["start"]:
            globalX = point.x
            newSeg = point.segment
            if (newSeg is None):
                print("dodajemy nic")
            T.insert(newSeg)
            nbours = T.getNbours(newSeg)
            for nbour in nbours:
                # if nbour is None:
                # break
                checkAndhandleIntersection(newSeg, nbour)

        elif point.type == pointTypes["end"]:
            globalX = point.x
            toCheck = T.delete(point.segment)
            for sec1, sec2 in toCheck:
                checkAndhandleIntersection(sec1, sec2)
        elif point.type == pointTypes["intersection"]:
            if prevType == pointTypes["intersection"]:
                globalX = (globalX+point.x)/2
            toCheck = T.swap(point)
            for sec1, sec2 in toCheck:
                checkAndhandleIntersection(sec1, sec2)
            globalX = point.x
        prevType = point.type
        print(T.tree)
    return [(p.x, p.y) for p in intersections]


# section = [((0.3125, 0.2297794117647058), (0.7903225806451613, 0.6311274509803921)), ((
#     0.3286290322580645, 0.6311274509803921), (0.6975806451612904, 0.24203431372549017))]
section = [((-0.5, 0.5), (8.5, 3.5)),
           ((1, 3), (7, 5)),
           ((2, 4), (5, 1)),
           ((4.5, 3), (6.5, 6)),
           ((0, 5), (5.5, 5.5))]
section = [((725.8807341104167, 883.4293042406749), (367.19201582569747, 671.6770787497147)), ((136.89462215833248, 463.9725182930372), (198.92094231264934, 719.3521481709241)), ((542.7799497311285, 249.2031298067089), (88.09090098117889, 251.4930310933442)), ((302.02236295372654, 923.3752532957801), (70.23121845732338, 427.56291395593917)), ((469.5744179764243, 389.78913183499674), (250.04627589610496, 546.6531244529035)), ((59.73243400095718, 193.32456837437107), (126.78694433483373, 943.4488100090412)), ((379.3498891179109, 58.789069821667425), (607.3422581516231, 801.878967389482)), ((407.4083916663341, 539.5524507916907), (224.6493818607914, 785.9253652292941)), ((409.7451136183925, 385.3958112394532), (431.9710743256161, 710.3279879330696)), ((415.174394733836, 579.4570139756195), (229.860835822442, 266.5595040129106)), ((
    588.6205211536466, 947.5715669600971), (985.9696980558851, 525.7326663068686)), ((625.0738849004488, 334.70798559707725), (638.0657129246732, 420.38983718886936)), ((953.9676381342422, 230.8906481632277), (347.2132513807312, 287.8073006695964)), ((706.8962238257552, 216.63835276355348), (673.8043987013478, 137.5310570042112)), ((446.4203718257047, 361.3551851855338), (474.1989709701585, 164.69977002307868)), ((230.89506495268398, 882.3977933128716), (540.1140519204378, 879.4156548980385)), ((204.4910965643052, 882.3939038161909), (916.1800596254822, 4.792063825851733)), ((480.47742322201793, 671.4136000141451), (461.5661587406916, 367.92588342468304)), ((20.017446423061024, 668.4680314113805), (378.58196666447816, 670.8218480621713)), ((819.1621784713428, 605.1377000836642), (718.2911194906691, 382.8120148738611))]
# print(len(section))
# section = [((1, 2), (2, 6)), ((0.5, 3.5), (4, 7)),
#    ((1, 5), (7, 5)), ((2.5, 3.5), (3, 6.5))]
section = section[:15]
section = [((614.6967959399402, 507.1066936712443), (159.28778199882876, 909.9689710719657)), ((836.0059680967792, 199.83307691793118), (195.35616907066412, 180.38865769217304)), ((630.1801636303213, 12.219572506503518), (240.43782565027072, 451.4237752084471)), ((15.629868474346331, 330.1050666040972), (780.145518861381, 59.050720104170566)), ((867.8977649581522, 721.609479485634), (407.1732870684872, 605.2454158364895)), ((414.91770820884545, 407.27863454017955), (250.2798029288028, 159.78773148005544)), ((444.65087468310315, 415.3214837522844), (678.1599872279313, 832.289054777296)), ((887.1605213671796, 938.9867199511706), (217.26930252039324, 399.6296651742888)), ((377.4075994707156, 356.67964338342597), (492.0717817822511, 732.7797425624046)), ((106.05756753872153, 549.1242217826979), (360.2777181979936, 943.3322656398663)), ((
    790.1035518788549, 11.005706970119267), (967.5641451557121, 727.097556320258)), ((370.1626084460886, 284.7724784752187), (63.52866600788776, 115.51572292005163)), ((162.11893267653176, 928.2001379018176), (734.9066517634305, 417.663814940981)), ((722.9837013873914, 478.7263268623182), (937.5473929448951, 583.104209108265)), ((835.8877653068688, 764.3158613187636), (747.042267294496, 381.37151741805644)), ((552.5724403408055, 450.8701625166739), (125.17018090523113, 193.60482236681176)), ((360.4384254803156, 999.7786936180712), (295.52388199452173, 598.6980826332488)), ((209.01547777754982, 618.1145603038563), (847.0509677072803, 145.20698264286358)), ((380.11249374178533, 856.9932934280224), (596.7683438180402, 357.1415227647753)), ((191.32074633169228, 448.4462878157199), (600.4649735819625, 907.9078272476888))]
intersections = is_intersection(section)
print(intersections)
# for section in section:
#     print(section)
