from linked_list import DoublyLinkedList
class HashMap:
    """Polynomial UTF-8 hash with separate chaining and 0.75 resize."""
    def __init__(self,capacity=8):
        self.capacity=capacity; self.buckets=[DoublyLinkedList() for _ in range(capacity)]; self.count=0
    def _hash(self,key):
        h=0
        for b in key.encode('utf-8'): h=(h*131+b)&0xffffffffffffffff
        return h
    def _locate(self,key):
        bucket=self.buckets[self._hash(key)%self.capacity]; node=bucket.head.next
        while node is not bucket.tail:
            if node.data[0]==key: return bucket,node
            node=node.next
        return bucket,None
    def put(self,key,value):
        bucket,node=self._locate(key)
        if node is not None: node.data=(key,value); return
        bucket.insert_back((key,value)); self.count+=1
        if self.count/self.capacity>0.75: self._resize()
    def _resize(self):
        old=self.buckets; self.capacity*=2
        self.buckets=[DoublyLinkedList() for _ in range(self.capacity)]; self.count=0
        for bucket in old:
            node=bucket.head.next
            while node is not bucket.tail:
                self.put(node.data[0],node.data[1]); node=node.next
    def get(self,key,default=None):
        _,node=self._locate(key); return default if node is None else node.data[1]
    def contains(self,key): return self._locate(key)[1] is not None
    def remove(self,key):
        bucket,node=self._locate(key)
        if node is None: return None
        self.count-=1; return bucket.remove_node(node)[1]
    def keys(self):
        result=[]
        for bucket in self.buckets:
            node=bucket.head.next
            while node is not bucket.tail:
                result.append(node.data[0]); node=node.next
        return result
    def size(self): return self.count
