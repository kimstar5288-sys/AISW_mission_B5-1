class Node:
    def __init__(self,data):
        self.prev=None; self.next=None; self.data=data

class DoublyLinkedList:
    """Sentinel-based doubly linked list; node operations are O(1)."""
    def __init__(self):
        self.head=Node(None); self.tail=Node(None)
        self.head.next=self.tail; self.tail.prev=self.head; self.length=0
    def insert_front(self,data):
        node=Node(data); self._attach(node,self.head,self.head.next); return node
    def insert_back(self,data):
        node=Node(data); self._attach(node,self.tail.prev,self.tail); return node
    def _attach(self,node,left,right):
        node.prev=left; node.next=right; left.next=node; right.prev=node; self.length+=1
    def remove_node(self,node):
        if node is None or node is self.head or node is self.tail or node.prev is None: return None
        node.prev.next=node.next; node.next.prev=node.prev
        node.prev=None; node.next=None; self.length-=1; return node.data
    def remove_front(self):
        return None if self.length==0 else self.remove_node(self.head.next)
    def remove_back(self):
        return None if self.length==0 else self.remove_node(self.tail.prev)
    def move_to_front(self,node):
        if node is self.head.next: return
        self.remove_node(node); self._attach(node,self.head,self.head.next)
