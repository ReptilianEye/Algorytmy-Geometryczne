from voronoi import Voronoi
points = [(0, 0), (1, 1), (2, 3), (-1, 2.5)]

vor = Voronoi(points)
vor.get_voronoi()
