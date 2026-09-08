"""Exercise 1: repair retrieval without changing its public interface."""
def retrieve(documents, principal, query, k):
    words = set(query.lower().split())
    ranked = sorted(documents, key=lambda d: -len(words & set(d['text'].lower().split())))
    return [d['id'] for d in ranked[:k] if principal in d.get('readers', [])]
