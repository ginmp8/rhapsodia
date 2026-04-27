"""Common evaluation metrics.

Each metric is a function ``metric(actual, expected) -> float`` that returns a
score in the range ``[0.0, 1.0]``.
"""

from __future__ import annotations

from typing import Any


def accuracy(actual: Any, expected: Any) -> float:
    """Exact-match accuracy.

    Returns ``1.0`` if *actual* equals *expected*, ``0.0`` otherwise.

    Args:
        actual: The value produced by the skill.
        expected: The ground-truth value.

    Returns:
        ``1.0`` or ``0.0``.
    """
    return 1.0 if actual == expected else 0.0


def f1_score(actual: str, expected: str) -> float:
    """Token-level F1 score between two strings.

    Tokenizes both strings by whitespace and computes the F1 between the
    resulting token bags.

    Args:
        actual: The predicted string.
        expected: The reference string.

    Returns:
        F1 score in ``[0.0, 1.0]``.
    """
    actual_tokens = set(actual.lower().split())
    expected_tokens = set(expected.lower().split())

    if not expected_tokens:
        return 1.0 if not actual_tokens else 0.0

    true_positives = len(actual_tokens & expected_tokens)
    if true_positives == 0:
        return 0.0

    precision = true_positives / len(actual_tokens)
    recall = true_positives / len(expected_tokens)
    return 2 * precision * recall / (precision + recall)


def rouge_l(actual: str, expected: str) -> float:
    """ROUGE-L score based on the longest common subsequence (LCS).

    Args:
        actual: The predicted string (space-tokenized).
        expected: The reference string (space-tokenized).

    Returns:
        ROUGE-L F1 score in ``[0.0, 1.0]``.
    """
    a_tokens = actual.lower().split()
    e_tokens = expected.lower().split()

    lcs_len = _lcs_length(a_tokens, e_tokens)

    if lcs_len == 0:
        return 0.0

    precision = lcs_len / len(a_tokens) if a_tokens else 0.0
    recall = lcs_len / len(e_tokens) if e_tokens else 0.0
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _lcs_length(a: list[str], b: list[str]) -> int:
    """Return the length of the longest common subsequence of *a* and *b*."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
