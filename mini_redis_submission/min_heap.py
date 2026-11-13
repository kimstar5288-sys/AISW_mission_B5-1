from dynamic_array import DynamicArray
class MinHeap:
    """Binary min-heap for (expiration, sequence, key, generation)."""
    def __init__(self): self.items=DynamicArray()
    def size(self): return len(self.items)
    def peek(self): return None if not self.size() else self.items[0]
    def push(self,item): self.items.append(item); self._heapify_up(self.size()-1)
    def pop(self):
        if not self.size(): return None
        root=self.items[0]; last=self.items.pop()
        if self.size(): self.items[0]=last; self._heapify_down(0)
        return root
    def _heapify_up(self,i):
        while i>0:
            p=(i-1)//2
            if self.items[p]<=self.items[i]: break
            self.items[p],self.items[i]=self.items[i],self.items[p]; i=p
    def _heapify_down(self,i):
        n=self.size()
        while True:
            left=2*i+1; right=left+1; smallest=i
            if left<n and self.items[left]<self.items[smallest]: smallest=left
            if right<n and self.items[right]<self.items[smallest]: smallest=right
            if smallest==i: break
            self.items[i],self.items[smallest]=self.items[smallest],self.items[i]; i=smallest
