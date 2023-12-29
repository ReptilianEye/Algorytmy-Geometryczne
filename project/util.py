
from datatypes import Point


def mat_det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def getIntersect(start1: Point, direction1: Point, start2: Point, direction2: Point):
    x1, y1 = start1.x, start1.y
    x2, y2 = direction1.x, direction1.y

    x3, y3 = start2.x, start2.y
    x4, y4 = direction2.x, direction2.y
    # Wyznaczenie równań prostych
    den = mat_det([(x1-x2), (x3-x4)], [(y1-y2), (y3-y4)])
    if den == 0:
        return None
    t = mat_det([(x1-x3), (x3-x4)], [(y1-y3), (y3-y4)]) / den
    u = -mat_det([(x1-x2), (x1-x3)], [(y1-y2), (y1-y3)]) / den

    if 0 <= t and 0 <= u:
        return Point(x1 + t*(x2-x1), y1 + t*(y2-y1))
    return None


def leftParent(node):
    if node.parent == None:
        return None
    if node.parent.right == node:
        return node.parent
    return leftParent(node.parent)


def rightParent(node):
    if node.parent == None:
        return None
    if node.parent.left == node:
        return node.parent
    return rightParent(node.parent)


# def replaceRemove(node, replacement):
#     rParent = rightParent(node)
#     lParent = leftParent(node)
#     if rParent == None:
#         lParent.arc = replacement
#         lParent.right = None
#         return
#     if lParent == None:
#         rParent.arc = replacement
#         rParent.left = None
#         return
#     higherParent = lParent if node.parent == rParent else rParent
#     if higherParent == lParent:
#         __replaceOnRight(node, replacement)
#     else:
#         __replaceOnLeft(node, replacement)


# def __replaceOnRight(node, replacement):
#     lParent = leftParent(node)
#     rParent = rightParent(node)
#     lParent.arc = replacement.arc
#     if rParent.parent == lParent:
#         lParent.right = rParent.right
#     else:
#         rParent.parent.left = rParent.right


# def __replaceOnLeft(node, replacement):
#     rParent = rightParent(node)
#     lParent = leftParent(node)
#     rParent.arc = replacement.arc
#     if lParent.parent == rParent:
#         rParent.left = lParent.left
#     else:
#         lParent.parent.right = lParent.left
