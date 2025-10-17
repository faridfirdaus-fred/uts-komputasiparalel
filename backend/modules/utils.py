import os
import random
import string


def generate_dummy_files(folder='data', count=810, seed=237006081):
    os.makedirs(folder, exist_ok=True)
    random.seed(seed)
    for i in range(1, count + 1):
        text = ' '.join(''.join(random.choices(
            string.ascii_letters + string.digits + " ", k=100)) for _ in range(10))
        with open(os.path.join(folder, f"file_{i}.txt"), 'w', encoding='utf-8') as f:
            f.write(text)


def generate_random_assignment_files(folder='data', count=810, seed=237006081):
    """Generate `count` text files with mixed content (letters, digits, punctuation)

    The files are suitable for testing the Parallel File Analyzer: they include
    vowels, words, digits and symbols. Files are named `sample_001.txt` .. `sample_{count:03d}.txt`.
    """
    os.makedirs(folder, exist_ok=True)
    random.seed(seed)

    # increase spaces probability for word splits
    letters = string.ascii_letters + ' ' * 10
    digits = string.digits
    punct = string.punctuation

    for i in range(1, count + 1):
        parts = []
        # create 20 sentences per file; each sentence contains words, digits and symbols
        for _ in range(20):
            # build 8-16 words per sentence
            words = []
            for _w in range(random.randint(8, 16)):
                # word length 1-12, mix letters and occasional numbers
                wlen = random.randint(1, 12)
                word = ''.join(random.choices(letters + digits, k=wlen))
                words.append(word)
            sentence = ' '.join(words)
            # append some random symbols and digits
            extras = ''.join(random.choices(
                punct + digits, k=random.randint(0, 6)))
            parts.append(sentence + extras)

        content = '\n'.join(parts)
        filename = os.path.join(folder, f"sample_{i:03d}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)


def params_from_nim(nim):
    """Derive parameters from a NIM string or int.

    Returns (threads, processes, data_count)

    - threads = last two digits of NIM % 4 + 2
    - processes = middle two digits of NIM % 3 + 2
    - data_count = last three digits of NIM * 10

    Example: nim=237006081 -> last2=81 -> threads=81%4+2=3; middle two digits (positions 4-5) = '00' -> processes=2; last3=081 -> data_count=810
    """
    s = str(nim)
    if len(s) < 3:
        raise ValueError('NIM must have at least 3 digits')

    last2 = int(s[-2:])
    last3 = int(s[-3:])
    mid_idx = len(s) // 2
    mid_two = s[mid_idx - 1: mid_idx + 1]
    mid_val = int(mid_two)

    threads = last2 % 4 + 2
    processes = mid_val % 3 + 2
    data_count = last3 * 10

    return threads, processes, data_count
