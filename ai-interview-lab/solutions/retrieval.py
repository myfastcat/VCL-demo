"""Reference implementation for the explicitly bounded in-memory exercise."""
def retrieve(documents, principal, query, k):
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError('k must be a non-negative integer')
    if not principal or not isinstance(principal, str):
        return []
    words = set(query.casefold().split())
    if not words or k == 0:
        return []
    seen = set()
    scored = []
    for d in documents:
        readers = d.get('readers')
        if not isinstance(readers, list) or principal not in readers:
            continue
        identity = d['id']
        if identity in seen:
            raise ValueError('duplicate authorized document ID')
        seen.add(identity)
        score = len(words & set(d['text'].casefold().split()))
        if score:
            scored.append((score, identity))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [identity for _, identity in scored[:k]]
