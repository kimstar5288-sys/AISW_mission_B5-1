class DynamicArray:
    """Explicit capacity doubling; built-in list is only fixed indexed storage."""
    def __init__(self): self.capacity=4; self.length=0; self.data=[None]*self.capacity
    def __len__(self): return self.length
    def __getitem__(self,i): return self.get(i)
    def __setitem__(self,i,v): self.set(i,v)
    def _check(self,i):
        if i<0 or i>=self.length: raise IndexError(i)
    def get(self,i): self._check(i); return self.data[i]
    def set(self,i,v): self._check(i); self.data[i]=v
    def append(self,v):
        if self.length==self.capacity:
            new=[None]*(self.capacity*2)
            for i in range(self.length): new[i]=self.data[i]
            self.data=new; self.capacity*=2
        self.data[self.length]=v; self.length+=1
    def remove(self,i):
        v=self.get(i)
        for j in range(i,self.length-1): self.data[j]=self.data[j+1]
        self.length-=1; self.data[self.length]=None; return v
    def pop(self): return self.remove(self.length-1)
