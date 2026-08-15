from __future__ import annotations

from translation_qa.models import AlignedPair
from translation_qa.segment import split_sentences


def align_sentences(english: str, translated: str) -> list[AlignedPair]:
    """Length-based sentence alignment with 1:1, 1:2, and 2:1 matches."""
    en = split_sentences(english)
    tr = split_sentences(translated)
    if not en or not tr:
        return []

    n, m = len(en), len(tr)
    en_len = [max(len(item), 1) for item in en]
    tr_len = [max(len(item), 1) for item in tr]
    mean_en = sum(en_len) / n
    mean_tr = sum(tr_len) / m
    ratio = mean_tr / mean_en if mean_en else 1.0

    inf = 10**12
    cost = [[inf] * (m + 1) for _ in range(n + 1)]
    back: list[list[tuple[int, int]]] = [[(0, 0)] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0

    def mismatch(left: int, right: int) -> float:
        expected = left * ratio
        return abs(right - expected) / max(expected, 1.0)

    for i in range(n + 1):
        for j in range(m + 1):
            current = cost[i][j]
            if current >= inf:
                continue
            if i < n and j < m:
                step = current + mismatch(en_len[i], tr_len[j])
                if step < cost[i + 1][j + 1]:
                    cost[i + 1][j + 1] = step
                    back[i + 1][j + 1] = (1, 1)
            if i < n - 1 and j < m:
                step = current + mismatch(en_len[i] + en_len[i + 1], tr_len[j]) + 0.35
                if step < cost[i + 2][j + 1]:
                    cost[i + 2][j + 1] = step
                    back[i + 2][j + 1] = (2, 1)
            if i < n and j < m - 1:
                step = current + mismatch(en_len[i], tr_len[j] + tr_len[j + 1]) + 0.35
                if step < cost[i + 1][j + 2]:
                    cost[i + 1][j + 2] = step
                    back[i + 1][j + 2] = (1, 2)
            if i < n:
                step = current + 1.6
                if step < cost[i + 1][j]:
                    cost[i + 1][j] = step
                    back[i + 1][j] = (1, 0)
            if j < m:
                step = current + 1.6
                if step < cost[i][j + 1]:
                    cost[i][j + 1] = step
                    back[i][j + 1] = (0, 1)

    pairs: list[AlignedPair] = []
    i, j = n, m
    while i > 0 or j > 0:
        di, dj = back[i][j]
        if di == 0 and dj == 0:
            break
        en_text = " ".join(en[i - di : i]) if di else ""
        tr_text = " ".join(tr[j - dj : j]) if dj else ""
        pairs.append(
            AlignedPair(
                index=0,
                english=en_text,
                translated=tr_text,
                en_start=i - di,
                en_end=i,
                tr_start=j - dj,
                tr_end=j,
            )
        )
        i -= di
        j -= dj
    pairs.reverse()
    for offset, pair in enumerate(pairs):
        pairs[offset] = AlignedPair(
            index=offset,
            english=pair.english,
            translated=pair.translated,
            en_start=pair.en_start,
            en_end=pair.en_end,
            tr_start=pair.tr_start,
            tr_end=pair.tr_end,
        )
    return pairs
