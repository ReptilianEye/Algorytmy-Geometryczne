from copy import deepcopy
from util import getIntersect
from datatypes import *
from dataclasses import dataclass


class Beachline:
    def __init__(self, root: Node = None):
        self.root: Node = root

    def find_node(self, p: Point) -> Node:
        r = self.root
        while r.left or r.right:
            if r.parabolaIntersectX() > p.x:
                r = r.left
            else:
                r = r.right
        return r

    def update_next_prev(self):
        prev = None

        def update_r(root):
            nonlocal prev
            if root.left == None and root.right == None:
                root.prev = prev
                if prev != None:
                    prev.next = root
                prev = root
                return
            if root.left != None:
                update_r(root.left)
            if root.right != None:
                update_r(root.right)
        update_r(self.root)

    def print(self):
        def print_r(root):
            if root.left == None and root.right == None:
                print(
                    root.arc.focus, f"prev={root.prev.arc.focus if root.prev!=None else None}, next={root.next.arc.focus if root.next!=None else None}", end=" | ")
                return
            if root.left != None:
                print_r(root.left)
            if root.right != None:
                print_r(root.right)
        print_r(self.root)
        print("----")

    def replace(self, arc_node: Node, new_arc: Arc):
        arc = arc_node.arc
        # new_arc.setEdgesWithHigher(arc)
        old_arc_l = Arc(arc.focus)
        old_arc_r = Arc(arc.focus)  # deepcopy(arc)
        new_arc.setLeftEdge(old_arc_l)
        new_arc.setRightEdge(old_arc_r)
        old_arc_l.edgeGoingLeft = arc.edgeGoingLeft
        old_arc_r.edgeGoingRight = arc.edgeGoingRight
        #       old_new
        #      /       \
        # old_arc_l   new_old
        #             /  \
        #        new_arc  old_arc_r
        old_new_node = Node()
        old_new_node.arc_pair = Pair(old_arc_l, new_arc)

        old_arc_leaf_l = Node()
        old_arc_leaf_l.arc = old_arc_l

        new_old_node = Node()
        new_old_node.arc_pair = Pair(new_arc, old_arc_r)

        new_arc_leaf = Node()
        new_arc_leaf.arc = new_arc

        old_arc_leaf_r = Node()
        old_arc_leaf_r.arc = old_arc_r

        # relations
        old_new_node.left = old_arc_leaf_l
        old_new_node.right = new_old_node
        old_arc_leaf_l.parent = old_new_node
        new_old_node.parent = old_new_node

        new_old_node.left = new_arc_leaf
        new_old_node.right = old_arc_leaf_r
        new_arc_leaf.parent = new_old_node
        old_arc_leaf_r.parent = new_old_node

        # old_arc_leaf_l.prev = arc_node.prev
        # old_arc_leaf_l.next = new_arc_leaf

        # new_arc_leaf.prev = old_arc_leaf_l
        # new_arc_leaf.next = old_arc_leaf_r

        # old_arc_leaf_r.prev = new_arc_leaf
        # old_arc_leaf_r.next = arc_node.next
        # connect to tree
        old_new_node.parent = arc_node.parent
        if arc_node.parent == None:
            self.root = old_new_node
        elif arc_node.parent.left == arc_node:
            arc_node.parent.left = old_new_node
        else:
            arc_node.parent.right = old_new_node
        self.update_next_prev()
        self.print()
        return old_arc_leaf_l, old_arc_leaf_r

    def insert(self, p: Point):
        arc = Arc(p)
        if self.root == None:
            self.root = Node()
            self.root.arc = arc
            return None, None, None
        node_to_replace = self.find_node(p)

        # # remove circle event
        # self.__removeCircleEvent(node_to_replace.arc)

        left_arc_node, right_arc_node = self.replace(node_to_replace, arc)

        left_circle_event = self.checkForCircleEvent(left_arc_node)
        right_circle_event = self.checkForCircleEvent(right_arc_node)

        return node_to_replace, left_circle_event, right_circle_event

    def handleSquize(self, arc_node):
        al = self.leftNbour(arc_node)
        ar = self.rightNbour(arc_node)

        al.parent.arc_pair.right = ar.arc
        ar.parent.arc_pair.left = al.arc
        intersect = Node()
        intersect.arc_pair = Pair(al.arc, ar.arc)

        self.replaceRemove(arc_node, intersect)
        self.print()
        left_circle_event = self.checkForCircleEvent(al)

        right_circle_event = self.checkForCircleEvent(ar)

        return left_circle_event, right_circle_event

    def checkForCircleEvent(self, node):
        circle_event_point = self.isCirleEvent(node)
        circle_event = None
        if circle_event_point != None:
            circle_event = Event(
                CIRCLE_EVENT, point=circle_event_point, node=node)
            # right_circle_event = Event(right_circle_event_point, 'circle')
            node.arc.circle_event = circle_event

        return circle_event

    def isCirleEvent(self, arc_node: Node):
        # left = self.leftNbour(arc_node)
        # right = self.rightNbour(arc_node)
        # if left == None or right == None:
        #     return
        leftEdge = arc_node.arc.edgeGoingLeft
        rightEdge = arc_node.arc.edgeGoingRight
        if leftEdge == None or rightEdge == None:
            return
        inter = getIntersect(leftEdge.start, leftEdge.direction,
                             rightEdge.start, rightEdge.direction)
        return inter

    def leftNbour(self, node):
        return node.prev

    def rightNbour(self, node):
        return node.next

    # node that starting from which we go to right to get to node
    def leftParent(self, node):
        if node.parent == None:
            return None
        if node.parent.right == node:
            return node.parent
        return self.leftParent(node.parent)

    def rightParent(self, node):
        if node.parent == None:
            return None
        if node.parent.left == node:
            return node.parent
        return self.rightParent(node.parent)

    def replaceRemove(self, node, newPair):
        rParent = self.rightParent(node)
        lParent = self.leftParent(node)
        if rParent == None:
            lParent.arc = newPair
            lParent.right = None
            return
        if lParent == None:
            rParent.arc = newPair
            rParent.left = None
            return
        higherParent = lParent if node.parent == rParent else rParent
        if higherParent == lParent:
            self.__replaceOnRight(node, newPair)
        else:
            self.__replaceOnLeft(node, newPair)

    def __replaceOnRight(self, node, replacement):
        lParent = self.leftParent(node)
        rParent = self.rightParent(node)
        lParent.arc = replacement.arc
        if rParent.parent == lParent:
            lParent.right = rParent.right
        else:
            rParent.parent.left = rParent.right

    def __replaceOnLeft(self, node, replacement):
        rParent = self.rightParent(node)
        lParent = self.leftParent(node)
        rParent.arc = replacement.arc
        if lParent.parent == rParent:
            rParent.left = lParent.left
        else:
            lParent.parent.right = lParent.left

    # def __removeCircleEvent(self, arc):
    #     if arc.circle_event != None:
    #         arc.circle_event.false_alarm = True

    def delete(self, p):
        pass


# def print_T(root):
#     if root is None:
#         return
#     print_T(root.left)
#     print(root.arc.focus)
#     print_T(root.right)


# r = Node()
# r.arc = Arc(10)
# r.left = Node()
# r.left.arc = Arc(5)
# r.right = Node()
# r.right.arc = Arc(20)
# r.left.parent = r
# r.right.parent = r
# r.left.left = Node()
# r.left.left.arc = Arc(2)
# r.left.right = Node()
# r.left.right.arc = Arc(7)
# r.left.left.parent = r.left
# r.left.right.parent = r.left
# r.left.left.left = Node()
# r.left.left.left.arc = Arc(1)
# r.left.left.right = Node()
# r.left.left.right.arc = Arc(3)
# r.left.left.left.parent = r.left.left
# r.left.left.right.parent = r.left.left
# r.left.right.left = Node()
# r.left.right.left.arc = Arc(6)
# r.left.right.right = Node()
# r.left.right.right.arc = Arc(8)
# r.left.right.left.parent = r.left.right
# r.left.right.right.parent = r.left.right

# r.right.left = Node()
# r.right.left.arc = Arc(15)
# r.right.right = Node()
# r.right.right.arc = Arc(25)
# r.right.left.parent = r.right
# r.right.right.parent = r.right
# r.right.left.left = Node()
# r.right.left.left.arc = Arc(13)
# r.right.left.right = Node()
# r.right.left.right.arc = Arc(16)
# r.right.left.left.parent = r.right.left
# r.right.left.right.parent = r.right.left
# r.right.right.left = Node()
# r.right.right.left.arc = Arc(24)
# r.right.right.right = Node()
# r.right.right.right.arc = Arc(30)
# r.right.right.left.parent = r.right.right
# r.right.right.right.parent = r.right.right
# # print_T(r)
# replacement = Node()
# replacement.arc = Arc(14)
# replacement2 = Node()
# replacement2.arc = Arc(17)
# replacement3 = Node()
# replacement3.arc = Arc(23)

# # replaceRemove(r.right.left.left, replacement)
# # replaceRemove(r.right.left.right, replacement2)
# replaceRemove(r.right.right.left, replacement3)
# print_T(r)
