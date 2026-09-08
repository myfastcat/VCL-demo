import unittest
from lab_loader import load
retrieve = load('retrieval').retrieve
class RetrievalTests(unittest.TestCase):
    def test_authorize_before_top_k(self):
        docs=[{'id':'private','text':'red blue','readers':['other']},{'id':'public','text':'red','readers':['me']}]
        self.assertEqual(retrieve(docs,'me','red blue',1),['public'])
    def test_exact_principal(self):
        self.assertEqual(retrieve([{'id':'x','text':'red','readers':'joann'}],'ann','red',1),[])
    def test_relevance(self):
        self.assertEqual(retrieve([{'id':'x','text':'blue','readers':['me']}],'me','red',1),[])
    def test_tie_is_stable(self):
        docs=[{'id':i,'text':'red','readers':['me']} for i in ['z','a']]
        self.assertEqual(retrieve(docs,'me','red',2),['a','z'])
    def test_missing_permissions(self):
        self.assertEqual(retrieve([{'id':'x','text':'red'}],'me','red',1),[])
    def test_empty_query(self):
        self.assertEqual(retrieve([{'id':'x','text':'red','readers':['me']}],'me',' ',1),[])
    def test_invalid_k(self):
        for k in [-1,True,1.5]:
            with self.assertRaises(ValueError):retrieve([], 'me','red', k)
    def test_duplicate_authorized_id(self):
        d={'id':'x','text':'red','readers':['me']}
        with self.assertRaises(ValueError):retrieve([d,d],'me','red',2)
