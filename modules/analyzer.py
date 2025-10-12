import string


def analyze_text(text):
    words = text.split()
    vowels = sum(c in 'aeiouAEIOU' for c in text)
    digits = sum(c.isdigit() for c in text)
    symbols = sum(c in string.punctuation for c in text)
    avg_len = sum(len(w) for w in words) / len(words) if words else 0
    return {
        'words': len(words),
        'vowels': vowels,
        'digits': digits,
        'symbols': symbols,
        'avg_len': avg_len
    }


def detailed_analyze_text(text, top_k=20):
    """Return detailed analysis including token frequencies and word-length histogram.

    Output shape:
    {
      'words': int,
      'vowels': int,
      'digits': int,
      'symbols': int,
      'avg_len': float,
      'top_words': [(word, count), ...],
      'len_histogram': {length: count, ...}
    }
    """
    import collections
    words = [w.strip(string.punctuation).lower()
             for w in text.split() if w.strip(string.punctuation)]
    vowels = sum(c in 'aeiouAEIOU' for c in text)
    digits = sum(c.isdigit() for c in text)
    symbols = sum(c in string.punctuation for c in text)
    avg_len = sum(len(w) for w in words) / len(words) if words else 0

    counter = collections.Counter(words)
    top_words = counter.most_common(top_k)

    len_hist = collections.Counter(len(w) for w in words)

    return {
        'words': len(words),
        'vowels': vowels,
        'digits': digits,
        'symbols': symbols,
        'avg_len': avg_len,
        'top_words': top_words,
        'len_histogram': dict(len_hist)
    }
