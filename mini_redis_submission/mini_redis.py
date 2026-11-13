import math
import shlex
import time
from hash_map import HashMap
from linked_list import DoublyLinkedList
from min_heap import MinHeap

INTEGER_ERROR='(error) ERR value is not an integer or out of range'
OOM="(error) OOM command not allowed when used_memory > 'maxmemory'"
def integer(n):
    try: return int(n)
    except (ValueError,TypeError): raise ValueError(INTEGER_ERROR)
class Entry:
    def __init__(self,key,value,node):
        self.key=key; self.value=value; self.node=node; self.expire_at=None; self.generation=0
class MiniRedis:
    """In-memory Redis-like CLI; no dict/set/collections for indexing."""
    def __init__(self,clock=None):
        self.clock=clock or time.monotonic
        self.store=HashMap(); self.lru=DoublyLinkedList(); self.expirations=MinHeap()
        self.used_memory=0; self.maxmemory=0; self.evicted_keys=0; self.sequence=0
        self.channels=HashMap()
    def _weight(self,key,value): return len(key.encode('utf-8'))+len(value.encode('utf-8'))
    def _delete(self,key,evicted=False):
        entry=self.store.remove(key)
        if entry is None: return False
        self.lru.remove_node(entry.node); self.used_memory-=self._weight(key,entry.value)
        entry.expire_at=None; entry.generation+=1
        if evicted: self.evicted_keys+=1
        return True
    def _purge(self):
        now=self.clock()
        while self.expirations.size() and self.expirations.peek()[0]<=now:
            deadline,seq,key,generation=self.expirations.pop(); entry=self.store.get(key)
            if entry is not None and entry.generation==generation and entry.expire_at==deadline:
                self._delete(key)
    def _entry(self,key): self._purge(); return self.store.get(key)
    def _evict(self):
        while self.maxmemory>0 and self.used_memory>self.maxmemory:
            self._delete(self.lru.tail.prev.data,True)
    def execute(self,line):
        try: parts=shlex.split(line)
        except ValueError: return '(error) ERR invalid quoting'
        if not parts: return ''
        cmd=parts[0].upper(); args=parts[1:]
        if cmd in ('EXIT','QUIT'): return None
        valid=('SET','GET','DEL','EXISTS','DBSIZE','KEYS','CONFIG','INFO','EXPIRE','TTL','SUBSCRIBE','PUBLISH','RECEIVE')
        if cmd not in valid: return "(error) ERR unknown command '%s'"%parts[0]
        arities=(('SET',2),('GET',1),('DEL',1),('EXISTS',1),('DBSIZE',0),('KEYS',0),('EXPIRE',2),('TTL',1),('SUBSCRIBE',2),('PUBLISH',2),('RECEIVE',1))
        for name,count in arities:
            if cmd==name and len(args)!=count: return "(error) ERR wrong number of arguments for '%s' command"%cmd
        if cmd=='CONFIG' and (len(args)!=3 or args[0].upper()!='SET' or args[1].lower()!='maxmemory'):
            return "(error) ERR wrong number of arguments for 'CONFIG' command"
        if cmd=='INFO' and (len(args)!=1 or args[0].lower()!='memory'):
            return "(error) ERR wrong number of arguments for 'INFO' command"
        self._purge()
        if cmd=='SET':
            key,value=args; size=self._weight(key,value)
            if self.maxmemory and size>self.maxmemory: return OOM
            old=self.store.get(key)
            if old:
                self.used_memory-=self._weight(key,old.value); old.value=value
                old.expire_at=None; old.generation+=1; self.lru.move_to_front(old.node)
            else:
                node=self.lru.insert_front(key); self.store.put(key,Entry(key,value,node))
            self.used_memory+=size; self._evict(); return 'OK'
        if cmd=='GET':
            entry=self.store.get(args[0])
            if entry is None: return '(nil)'
            self.lru.move_to_front(entry.node); return repr(entry.value).replace("'", "\"")
        if cmd=='DEL': return '(integer) '+str(int(self._delete(args[0])))
        if cmd=='EXISTS': return '(integer) '+str(int(self.store.contains(args[0])))
        if cmd=='DBSIZE': return '(integer) '+str(self.store.size())
        if cmd=='KEYS':
            keys=self.store.keys(); return '(empty array)' if not keys else '\n'.join('%d. "%s"'%(i+1,key) for i,key in enumerate(keys))
        if cmd=='CONFIG':
            try: n=integer(args[2])
            except ValueError as e: return str(e)
            if n<0: return INTEGER_ERROR
            self.maxmemory=n; self._evict(); return 'OK'
        if cmd=='INFO': return 'used_memory:%d\nmaxmemory:%d\nevicted_keys:%d'%(self.used_memory,self.maxmemory,self.evicted_keys)
        if cmd=='EXPIRE':
            try: seconds=integer(args[1])
            except ValueError as e: return str(e)
            entry=self.store.get(args[0])
            if entry is None: return '(integer) 0'
            if seconds<=0: self._delete(args[0]); return '(integer) 1'
            entry.generation+=1; entry.expire_at=self.clock()+seconds; self.sequence+=1
            self.expirations.push((entry.expire_at,self.sequence,args[0],entry.generation))
            return '(integer) 1'
        if cmd=='TTL':
            entry=self.store.get(args[0])
            if entry is None: return '(integer) -2'
            if entry.expire_at is None: return '(integer) -1'
            return '(integer) '+str(max(0,math.floor(entry.expire_at-self.clock())))
        if cmd=='SUBSCRIBE':
            channel,subscriber=args; subscribers=self.channels.get(channel)
            if subscribers is None: subscribers=HashMap(); self.channels.put(channel,subscribers)
            if not subscribers.contains(subscriber): subscribers.put(subscriber,DoublyLinkedList())
            return '(integer) 1'
        if cmd=='PUBLISH':
            channel,message=args; subscribers=self.channels.get(channel)
            if subscribers is None: return '(integer) 0'
            for subscriber in subscribers.keys(): subscribers.get(subscriber).insert_back(message)
            return '(integer) '+str(subscribers.size())
        if cmd=='RECEIVE':
            subscriber=args[0]; result=[]
            for channel in self.channels.keys():
                q=self.channels.get(channel).get(subscriber)
                if q is not None:
                    while q.length: result.append(channel+': '+q.remove_front())
            return '(empty array)' if not result else '\n'.join(result)

def main():
    redis=MiniRedis(); print('Mini Redis | HELP: SET GET DEL EXISTS DBSIZE KEYS CONFIG INFO EXPIRE TTL SUBSCRIBE PUBLISH RECEIVE | quit')
    while True:
        try: line=input('mini-redis> ')
        except (EOFError,KeyboardInterrupt): print(); break
        result=redis.execute(line)
        if result is None: break
        if result: print(result)
if __name__=='__main__': main()
