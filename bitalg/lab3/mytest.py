import bisect


class myClass:
    def __init__(self, x, value) -> None:
        self.x = x
        self.value = value

    def __lt__(self, other):
        return self.x < other.x

    def __gt__(self, other):
        return self.x <= other.x

    def __eq__(self, other):
        return self.x == other.x and self.value == self.value


a = [myClass(1, (1, 2, 3)), myClass(2, (2, 3, 4)), myClass(3, (3, 4, 5))]

bisect.insort(a, myClass(4, (4, 5, 6)), key=lambda x: x.x)
i = bisect.bisect(a, myClass(4, (3, 5, 6)))
print(myClass(4, (4, 5, 6)) == myClass(4, (4, 5, 6)))
print(i)
