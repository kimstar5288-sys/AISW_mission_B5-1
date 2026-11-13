from linked_list import DoublyLinkedList
class TreeNode:
    def __init__(self,value): self.value=value; self.left=None; self.right=None
class BinaryTree:
    def __init__(self,root=None): self.root=root
    def preorder(self,node=None):
        result=[]
        def walk(n):
            if n: result.append(n.value); walk(n.left); walk(n.right)
        walk(self.root if node is None else node); return result
    def inorder(self):
        result=[]
        def walk(n):
            if n: walk(n.left); result.append(n.value); walk(n.right)
        walk(self.root); return result
    def postorder(self):
        result=[]
        def walk(n):
            if n: walk(n.left); walk(n.right); result.append(n.value)
        walk(self.root); return result
    def levelorder(self):
        if self.root is None: return []
        queue=DoublyLinkedList(); queue.insert_back(self.root); result=[]
        while queue.length:
            n=queue.remove_front(); result.append(n.value)
            if n.left: queue.insert_back(n.left)
            if n.right: queue.insert_back(n.right)
        return result
class BST(BinaryTree):
    def insert(self,value):
        def add(n):
            if n is None: return TreeNode(value)
            if value<n.value: n.left=add(n.left)
            elif value>n.value: n.right=add(n.right)
            return n
        self.root=add(self.root)
    def search(self,value):
        n=self.root
        while n:
            if value==n.value: return True
            n=n.left if value<n.value else n.right
        return False
    def delete(self,value):
        def remove(n):
            if n is None: return None
            if value<n.value: n.left=remove(n.left)
            elif value>n.value: n.right=remove(n.right)
            else:
                if n.left is None: return n.right
                if n.right is None: return n.left
                successor=n.right
                while successor.left: successor=successor.left
                n.value=successor.value
                def delete_min(t):
                    if t.left is None: return t.right
                    t.left=delete_min(t.left); return t
                n.right=delete_min(n.right)
            return n
        self.root=remove(self.root)
