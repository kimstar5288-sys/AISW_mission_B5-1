import unittest
from mini_redis import MiniRedis,OOM
from hash_map import HashMap
from linked_list import DoublyLinkedList
from min_heap import MinHeap
from dynamic_array import DynamicArray
from trees import BST,BinaryTree,TreeNode
class Tests(unittest.TestCase):
    def test_list(self):
        l=DoublyLinkedList(); a=l.insert_back('a'); l.insert_front('b'); l.move_to_front(a)
        self.assertEqual(l.remove_front(),'a'); self.assertEqual(l.remove_back(),'b')
    def test_hash_resize_collision(self):
        m=HashMap(2)
        for i in range(100): m.put('key'+str(i),i)
        self.assertEqual(m.size(),100)
        for i in range(100): self.assertEqual(m.get('key'+str(i)),i)
        self.assertEqual(m.remove('key2'),2)
    def test_heap(self):
        h=MinHeap()
        for x in (8,3,5,1,9): h.push((x,'x'))
        self.assertEqual([h.pop()[0] for _ in range(5)],[1,3,5,8,9])
    def test_array(self):
        a=DynamicArray()
        for i in range(20): a.append(i)
        self.assertEqual(a.capacity,32); a.set(0,99); self.assertEqual(a.remove(0),99)
    def test_commands(self):
        r=MiniRedis(); self.assertEqual(r.execute('SET a "hello world"'),'OK')
        self.assertEqual(r.execute('GET a'),'"hello world"')
        self.assertEqual(r.execute('EXISTS a'),'(integer) 1')
        self.assertEqual(r.execute('DBSIZE'),'(integer) 1')
        self.assertEqual(r.execute('DEL a'),'(integer) 1')
        self.assertEqual(r.execute('GET a'),'(nil)')
    def test_lru_and_oom(self):
        r=MiniRedis(); r.execute('CONFIG SET maxmemory 6')
        r.execute('SET a 11'); r.execute('SET b 22'); r.execute('GET a')
        r.execute('SET c 33'); self.assertEqual(r.execute('GET b'),'(nil)')
        self.assertEqual(r.evicted_keys,1); self.assertEqual(r.used_memory,6)
        self.assertEqual(r.execute('SET huge 123456'),OOM)
        self.assertEqual(r.used_memory,6)
    def test_ttl(self):
        now=[100.0]; r=MiniRedis(lambda:now[0]); r.execute('SET a one'); r.execute('EXPIRE a 3')
        self.assertEqual(r.execute('TTL a'),'(integer) 3')
        now[0]+=4; self.assertEqual(r.execute('GET a'),'(nil)')
        self.assertEqual(r.execute('TTL a'),'(integer) -2')
    def test_ttl_reset_and_stale_heap(self):
        now=[10.0]; r=MiniRedis(lambda:now[0]); r.execute('SET a old'); r.execute('EXPIRE a 2')
        r.execute('SET a new'); now[0]=13
        self.assertEqual(r.execute('GET a'),'"new"'); self.assertEqual(r.execute('TTL a'),'(integer) -1')
    def test_unicode(self):
        r=MiniRedis(); r.execute('SET 한 글'); self.assertEqual(r.used_memory,6)
    def test_errors(self):
        r=MiniRedis(); self.assertIn('wrong number',r.execute('GET'))
        self.assertIn('unknown command',r.execute('HELLO'))
        self.assertIn('integer',r.execute('EXPIRE a x'))
    def test_pubsub(self):
        r=MiniRedis(); r.execute('SUBSCRIBE news kim'); r.execute('PUBLISH news hello')
        self.assertEqual(r.execute('RECEIVE kim'),'news: hello')
        self.assertEqual(r.execute('RECEIVE kim'),'(empty array)')
    def test_tree(self):
        b=BST()
        for x in (5,3,7,2,4,6,8): b.insert(x)
        self.assertEqual(b.inorder(),[2,3,4,5,6,7,8]); self.assertTrue(b.search(4))
        b.delete(5); self.assertEqual(b.inorder(),[2,3,4,6,7,8])
        self.assertEqual(b.levelorder(),[6,3,7,2,4,8])
if __name__=='__main__': unittest.main(verbosity=2)
