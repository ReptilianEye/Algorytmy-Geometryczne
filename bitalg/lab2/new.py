class DataPreparer():
    def __init__(self,genFunction, ranges) -> None:
        self.genFunction = genFunction
        self.file_base = os.path.join(self.genFunction.__name__,"dane")
        self.ranges = ranges
        self.pointsN = [50,100,1_000,10_000,25_000,50_000,80_000,100_000,200_000,300_000]
        self.inExt = '.in'
        self.outExt = '.out'

    def preparePoints(self,saveInFile=True): 
        All = []
        for i in range(len(self.pointsN)):
            if saveInFile:
                Q = self.genFunction(*self.ranges[i], self.pointsN[i])
                with open(self.file_base+str(i)+self.inExt, "w") as file:
                    temp = " ".join(str(el) for el in self.ranges[i])
                    file.write(f"{temp} {self.pointsN[i]}"+"\n")
                    for p in Q:
                        file.write(" ".join(str(el) for el in p) + "\n")
            else:
                with open(self.file_base+str(i)+self.inExt, "r") as file:
                    _ = file.readline()
                    Q = []
                    for _ in range(self.pointsN[i]):
                        Q.append(np.array(tuple(map(float, file.readline().split()))))
            All.append(Q)
        return All
    
class uniformDataPreparer(DataPreparer):
    def __init__(self, ranges) -> None:
        super().__init__(generate_uniform_points, ranges)

class circleDataPreparer(DataPreparer):
    def __init__(self, ranges) -> None:
        super().__init__(generate_circle_points, ranges)

class rectangleDataPreparer(DataPreparer):
    def __init__(self, ranges) -> None:
        super().__init__(generate_rectangle_points, ranges)

class squareDataPreparer(DataPreparer):
    def __init__(self, ranges) -> None:
        super().__init__(generate_square_points, ranges)