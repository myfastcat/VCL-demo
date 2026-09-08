# Lab 1 — The relevant document disappeared

## Interview brief

Your assistant searches a small document collection. A user can read several relevant documents, yet sometimes receives no result. The starter ranks every document and then removes inaccessible documents. Your task is to repair `retrieve(documents, principal, query, k)` and explain the tradeoff.

This is an in-memory lexical exercise, not a vector database or production authorization service. Documents are mappings with unique authorized string IDs and string text. `readers`, if present, must be a list of exact principal strings. Missing or malformed permission lists grant no access. A principal must be a nonempty string.

## Observable contract

- Match whitespace-separated words after case folding; punctuation remains part of a token. Use distinct query words, not frequency.
- Only authorized documents participate in ranking. Score is the number of shared words; exclude zero-score documents.
- Sort by decreasing score, then ascending document ID for deterministic ties.
- Return at most k IDs, without modifying documents. Empty query, empty principal or k=0 returns an empty list.
- k must be a nonnegative integer; reject booleans and invalid values with ValueError.
- Reject duplicate IDs among authorized documents with ValueError. Duplicates among excluded documents do not reveal additional information or affect the result.

Example: one inaccessible document matches `red blue`, and an accessible document matches only `red`. With query `red blue` and k=1, the accessible document must be returned. Ranking all documents before permission filtering incorrectly returns no result.

## Attempt

1. Run `python3 practice.py retrieval` and explain the first failure before changing code.
2. Sketch the order of validation, permission filtering, scoring and truncation.
3. Repair the exercise; add one test of your own if you think the contract has a gap.
4. Explain why an empty list can be correct, and when it reflects missing authorization rather than missing relevance.

<details><summary>Hint 1 — execution order</summary>

Top-k selection discards candidates. Applying permissions afterward cannot bring an authorized candidate back. Define the permitted candidate set first.
</details>

<details><summary>Hint 2 — permission representation</summary>

Python membership on a string is substring membership. A readers value of `joann` must not authorize principal `ann`. Validate the permission container rather than treating any iterable as an ACL.
</details>

<details><summary>Hint 3 — deterministic output</summary>

Sort tuples by negative score and document ID. Check duplicate IDs before assigning multiple ranking entries to the same authorized identity.
</details>

## Reference reasoning

The reference first validates k, handles empty inputs, and forms a set of case-folded query terms. It inspects permission lists before using document text for scoring. It then checks identity uniqueness for authorized documents, excludes zero scores, sorts explicitly and truncates.

The original failure is a recall failure: unauthorized documents consumed the limited result slots. The fix does not require a more powerful language model. A second flaw is malformed ACL interpretation; exact identity membership in a list avoids substring authorization. A third flaw is unstable ranking ties, which can make tests or explanations change with input ordering.

Complexity is O(n × tokenization work + a log a), where a is the number of relevant authorized documents. For large collections, an authorization-aware index or oversampling with carefully defined completeness guarantees might be considered. Oversampling alone does not guarantee recall: every oversampled result may still be unauthorized.

## Oral follow-up rubric

Score each dimension 0 (missing), 1 (mechanism named) or 2 (mechanism plus failure example): permission order; malformed permissions; deterministic ranking; limitations. The total is a self-review aid, not a hiring prediction.

Follow-ups: What happens if access is revoked after retrieval? Where would a final disclosure check occur? How would you paginate without skipping authorized results? Why does the supplied solution not establish protection against concurrent revocation? A strong answer separates this immutable-snapshot exercise from a real authorization system that must define freshness, cache keys, revocation and final output policy.
