"""
Generates 7 CSV files for the OPERATION: DECRYPT classroom game.

Each CSV contains 1000 rows of string data. One row contains a hidden
message fragment; the other 999 are structurally similar noise. Students
must apply specific pandas string operations to isolate the message row
via .dropna().

The full message: "I AM THE HAND THAT YOU CANNOT SEE"
"""

import json
import os
import random
import string

import pandas as pd

# ── Configuration ────────────────────────────────────────────────────────────
MESSAGE = "I AM THE HAND THAT YOU CANNOT SEE"
MESSAGE_PARTS = ["I AM", "THE", "HAND", "THAT", "YOU", "CANNOT", "SEE"]
NUM_FILES = 7
ROWS_PER_FILE = 1000
OUTPUT_DIR = "sparse_data_files"
SEED = 42

random.seed(SEED)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def _rand_alnum(length: int = 10) -> str:
    """Random alphanumeric string (mixed case + digits)."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _rand_mixed_no_allcaps(length: int = 10) -> str:
    """Random mixed-case string that is guaranteed NOT to be all uppercase."""
    while True:
        s = _rand_alnum(length)
        if not s.isupper():
            return s


def _timestamp(row: int) -> str:
    return f"2026-02-17 14:{row // 60:02d}:{row % 60:02d}"


# ── Puzzle generators ────────────────────────────────────────────────────────
# Each returns a list of 1000 strings. Exactly one contains the message.


def puzzle_strip_replace(msg: str) -> list[str]:
    """Group: str.strip() + str.replace() + str.extract()

    Message row:  "   ~~~SIGNAL{I AM}~~~   "
    Noise row:    "   ~~~xK3jM2pL9a~~~   "

    Steps:
      1. .str.strip()
      2. .str.replace('~~~', '', regex=False)
      3. .str.extract(r'SIGNAL\\{(.+)\\}')
      4. .dropna()
    """
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            rows.append(f"   ~~~SIGNAL{{{msg}}}~~~   ")
        else:
            rows.append(f"   ~~~{_rand_alnum(random.randint(8, 15))}~~~   ")
    return rows


def puzzle_lower_extract(msg: str) -> list[str]:
    """Group: str.lower() + str.extract()

    Message row:  "SYS_PaYlOaD:ThE_END"  (mixed case, contains 'payload:')
    Noise row:    "SYS_xK3mP9fT2qR_END"  (random, no 'payload' pattern)

    Steps:
      1. .str.lower()
      2. .str.extract(r'payload:([a-z\\s]+)_end')
      3. .dropna()
    """
    # Build the mixed-case version of "payload:<msg>"
    def _mixcase(s: str) -> str:
        return "".join(c.upper() if random.random() > 0.5 else c.lower() for c in s)

    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            payload = _mixcase(f"payload:{msg}")
            rows.append(f"SYS_{payload}_END")
        else:
            rows.append(f"SYS_{_rand_alnum(random.randint(10, 16))}_END")
    return rows


def puzzle_split_index(msg: str) -> list[str]:
    """Group: str.split() + .str[n] indexing + str.extract()

    Message row:  "alfa|bravo|MSG:HAND|delta|echo"
    Noise row:    "alfa|bravo|xK8f3jM|delta|echo"

    Steps:
      1. .str.split('|').str[2]
      2. .str.extract(r'MSG:([A-Z\\s]+)')
      3. .dropna()
    """
    fillers = ["alfa", "bravo", "delta", "echo"]
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        f0 = random.choice(fillers)
        f1 = random.choice(fillers)
        f3 = random.choice(fillers)
        f4 = random.choice(fillers)
        if i == target:
            field2 = f"MSG:{msg}"
        else:
            field2 = _rand_alnum(random.randint(6, 12))
        rows.append(f"{f0}|{f1}|{field2}|{f3}|{f4}")
    return rows


def puzzle_contains_where(msg: str) -> list[str]:
    """Group: str.contains() + .where() + str.extract()

    Message row:  "[CRITICAL] THAT"
    Noise rows:   "[ERROR] xK3j", "[DEBUG] mP9f", "[WARNING] aB2c", etc.

    Steps:
      1. mask = .str.contains('CRITICAL')
      2. .where(mask)          # non-CRITICAL rows become NaN
      3. .str.extract(r'\\[CRITICAL\\]\\s+(.+)')
      4. .dropna()
    """
    levels = ["ERROR", "DEBUG", "WARNING", "INFO", "TRACE"]
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            rows.append(f"[CRITICAL] {msg}")
        else:
            level = random.choice(levels)
            rows.append(f"[{level}] {_rand_alnum(random.randint(4, 10))}")
    return rows


def puzzle_regex_replace(msg: str) -> list[str]:
    """Group: str.replace() with regex + str.extract()

    Message row:  "Y@#O@#U"  (uppercase letters separated by @#)
    Noise row:    "k@#8@#j@#M"  (mixed case + digits separated by @#)

    Steps:
      1. .str.replace('@#', '', regex=False)
      2. .str.extract(r'^([A-Z\\s]+)$')    # only all-uppercase survives
      3. .dropna()
    """
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            rows.append("@#".join(msg))  # "Y@#O@#U" for "YOU"
        else:
            # Ensure noise is never all-uppercase after removing @#
            noise_chars = list(_rand_mixed_no_allcaps(random.randint(4, 8)))
            rows.append("@#".join(noise_chars))
    return rows


def puzzle_reverse(msg: str) -> list[str]:
    """Group: str.replace() + str[::-1] reversal + str.extract()

    Message row:  ">>TONNAC<<"  (reversed message with markers)
    Noise row:    ">>xK3fMp<<"  (random with same markers)

    Steps:
      1. .str.replace('>>', '', regex=False)
      2. .str.replace('<<', '', regex=False)
      3. .str[::-1]
      4. .str.extract(r'^([A-Z\\s]+)$')
      5. .dropna()
    """
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            rows.append(f">>{msg[::-1]}<<")
        else:
            rows.append(f">>{_rand_mixed_no_allcaps(random.randint(5, 12))}<<")
    return rows


def puzzle_findall_join(msg: str) -> list[str]:
    """Group: str.findall() + str.join()

    Message row:  "[S][E][E]"  (each uppercase letter in brackets)
    Noise row:    "[x][8][k][m]"  (lowercase + digits in brackets)

    Steps:
      1. .str.findall(r'\\[([A-Z])\\]')     # only captures uppercase
      2. .str.join('')                        # joins list into string
      3. .where(lambda s: s.str.len() > 0)   # empty strings → NaN
      4. .dropna()
    """
    target = random.randint(1, ROWS_PER_FILE - 1)
    rows = []
    for i in range(ROWS_PER_FILE):
        if i == target:
            rows.append("".join(f"[{c}]" for c in msg if c != " "))
        else:
            n = random.randint(3, 8)
            chars = random.choices(string.ascii_lowercase + string.digits, k=n)
            rows.append("".join(f"[{c}]" for c in chars))
    return rows


# ── Map puzzles to message parts ─────────────────────────────────────────────
PUZZLE_FUNCS = [
    puzzle_strip_replace,   # part 0: "I AM"
    puzzle_lower_extract,   # part 1: "THE"
    puzzle_split_index,     # part 2: "HAND"
    puzzle_contains_where,  # part 3: "THAT"
    puzzle_regex_replace,   # part 4: "YOU"
    puzzle_reverse,         # part 5: "CANNOT"
    puzzle_findall_join,    # part 6: "SEE"
]

# ── Generate files ───────────────────────────────────────────────────────────
# Assign file numbers 0-7 (8 numbers) to 7 groups → one number is missing
file_numbers = list(range(8))
random.shuffle(file_numbers)
file_numbers = file_numbers[:NUM_FILES]  # pick 7 of 8

# Shuffle which message part goes to which file
part_order = list(range(NUM_FILES))
random.shuffle(part_order)

key_map = {}  # instructor answer key

for idx, part_idx in enumerate(part_order):
    file_num = file_numbers[idx]
    msg_part = MESSAGE_PARTS[part_idx]
    puzzle_fn = PUZZLE_FUNCS[part_idx]

    rows = puzzle_fn(msg_part)
    df = pd.DataFrame(
        {
            "timestamp": [_timestamp(r) for r in range(ROWS_PER_FILE)],
            "transmission_log": rows,
        }
    )

    filename = f"packet_{file_num}.csv"
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)

    group_label = f"Group {idx + 1}"
    key_map[filename] = {
        "group": group_label,
        "message_part": msg_part,
        "message_position": part_idx,
        "puzzle_type": puzzle_fn.__name__,
    }
    print(f"  {group_label} → {filename} | puzzle: {puzzle_fn.__name__} | fragment: \"{msg_part}\"")

# Save answer key for instructor
with open(os.path.join(OUTPUT_DIR, "answer_key.json"), "w") as f:
    json.dump(key_map, f, indent=2)

print(f"\nGenerated {NUM_FILES} files in {OUTPUT_DIR}/")
print(f"Full message: \"{MESSAGE}\"")
print(f"Answer key saved to {OUTPUT_DIR}/answer_key.json")
