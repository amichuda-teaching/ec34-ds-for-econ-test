# OPERATION: DECRYPT

## CLASSIFIED BRIEFING

Agents,

Welcome to the **Bureau of Economic Intelligence (BEI)**. At 0300 hours this morning, our field operatives intercepted a encrypted transmission broadcast by an unknown entity. The sender, anticipating interception, fractured the message into **7 data packets** and buried each fragment inside 1,000 rows of system noise — fake log data designed to make the signal indistinguishable from garbage.

Your mission: **recover the hidden message before it's too late.**

There is a complication. A rival AI — codenamed **THE INSTRUCTOR** — has obtained the same intercepted cipher and is currently running a brute-force decryption attack on the main display. If THE INSTRUCTOR cracks the encryption before you decode the packets manually, the message falls into enemy hands.

**You are the last line of defense.**

---

## RULES OF ENGAGEMENT

1. Each group receives **one CSV file** (a "data packet") containing 1,000 rows.
2. Follow your group's **step-by-step decryption protocol** below using `pandas` string operations.
3. The cleaning steps will turn noise rows into `NaN` — only the real signal survives.
4. Your final step is always **`.dropna()`** to reveal your fragment of the message.
5. Once decoded, **shout your fragment** so the class can reconstruct the full transmission.

**Load your file like this:**

```python
import pandas as pd

df = pd.read_csv("<your_file>.csv")
s = df["transmission_log"]  # This is the column you'll work with
```

---

## GROUP 1 — File: `packet_3.csv`
### Codename: LOG FILTER
**Skill: `.str.contains()` + `.where()`**

Your data packet contains system logs tagged with severity levels like `[ERROR]`, `[DEBUG]`, and `[WARNING]`. The real signal is hidden in a row tagged `[CRITICAL]`.

**Protocol:**

```python
# Step 1: Create a boolean mask — which rows contain "CRITICAL"?
mask = s.str.contains('<your string pattern here>')

# Step 2: Use .where() to keep only CRITICAL rows (everything else → NaN)
filtered = s.where(mask)

# Step 3: Extract the text after the critical log level tag
result = filtered.str.extract(r'<your regex pattern here>')

# Step 4: Drop the noise
result.dropna()
```

---

## GROUP 2 — File: `packet_4.csv`
### Codename: CASE CRACKER
**Skill: `.str.lower()` + `.str.extract()`**

Your data looks like system identifiers: `"SYS_<gibberish>_END"`. One row contains a payload marker written in wildly mixed case (e.g., `PaYlOaD`). You need to normalize the case before you can find it.

**Protocol:**

```python
# Step 1: Lowercase everything so the pattern becomes consistent
lowered = s.str.lower()

# Step 2: Extract the text after "payload:" and before "_end"
result = lowered.str.extract(r'<your regex pattern here>')

# Step 3: Drop the noise
result = result.dropna()

# Step 4: The answer is uppercase — convert it back
result[0].str.upper()
```

---

## GROUP 3 — File: `packet_6.csv`
### Codename: FIELD SPLITTER
**Skill: `.str.split()` + `.str[n]` indexing**

Your packet contains pipe-delimited (`|`) log entries with 5 fields each. The signal is hiding in the **third field** (index 2), marked with a `MSG:` prefix. The other fields are decoys.

**Protocol:**

```python
# Step 1: Split each row by the pipe delimiter
split_data = s.str.split("|")

# Step 2: Grab just the third field (index 2)
field_3 = split_data.str[2]

# Step 3: Extract text after the "MSG:" prefix (only real signals have it)
result = field_3.str.extract(r'<your regex pattern here>')

# Step 4: Drop the noise
result.dropna()
```

---

## GROUP 4 — File: `packet_7.csv`
### Codename: BRACKET HUNTER
**Skill: `.str.findall()` + `.str.join()`**

Your data contains strings of characters enclosed in square brackets: `[x][8][k]`. The signal uses **uppercase letters** in the brackets; the noise uses lowercase and digits. You need to find all the uppercase letters and join them together.

**Protocol:**

```python
# Step 1: Find all uppercase letters inside square brackets
found = s.str.findall(r'<your regex pattern here>')

# Step 2: Join the list of letters into a single string
joined = found.str.join("")

# Step 3: Empty strings mean no uppercase was found — replace with NaN
import numpy as np
joined = joined.replace("", np.nan)

# Step 4: Drop the noise
joined.dropna()
```

---

## GROUP 5 — File: `packet_2.csv`
### Codename: NOISE STRIPPER
**Skill: `.str.replace()` + `.str.extract()`**

The sender scrambled their message by inserting `@#` between every character. Your job: remove the interference pattern, then identify which row contains a clean all-uppercase result.

**Protocol:**

```python
# Step 1: Remove all occurrences of the "@#" interference pattern
cleaned = s.str.replace("<what to replace>", "<replace with an empty string>", regex=False)

# Step 2: Extract rows that are purely uppercase letters (the signal)
result = cleaned.str.extract(r'<your regex pattern here>')

# Step 3: Drop the noise
result.dropna()
```

---

## GROUP 6 — File: `packet_5.csv`
### Codename: WHITESPACE WARDEN
**Skill: `.str.strip()` + `.str.replace()`**

Your packet is padded with whitespace and wrapped in `~~~` delimiters. Buried in one row is a `SIGNAL{...}` tag containing the fragment. You need to clean the formatting before you can extract it.

**Protocol:**

```python
# Step 1: Strip leading/trailing whitespace
stripped = s.str.strip()

# Step 2: Remove the ~~~ delimiters
cleaned = stripped.str.replace("<what to replace>", "<replace with an empty string>", regex=False)

# Step 3: Extract the content inside SIGNAL{...}
result = cleaned.str.extract(r'<your regex pattern here>')

# Step 4: Drop the noise
result.dropna()
```

---

## GROUP 7 — File: `packet_0.csv`
### Codename: MIRROR READER
**Skill: `.str.replace()` + `str[::-1]` reversal**

The sender reversed their message and wrapped it in `>>` and `<<` markers. You need to strip the markers and flip the string back to its original form.

**Protocol:**

```python
# Step 1: Remove the >> marker
step1 = s.str.replace("<what to replace>", "<replace with an empty string>", regex=False)

# Step 2: Remove the << marker
step2 = step1.str.replace("<what to replace>", "<replace with an empty string>", regex=False)

# Step 3: Reverse every string
reversed_s = step2.str[::-1]

# Step 4: Extract rows that are purely uppercase (the signal)
result = reversed_s.str.extract(r'<your regex pattern here>')

# Step 5: Drop the noise
result.dropna()
```

---

## FINAL ASSEMBLY

Once every group has decoded their fragment, shout it out. The class must **reconstruct the original message** from all 7 pieces.

The fragments have no inherent order — you'll need to figure out how they fit together.

Good luck, agents. The clock is ticking.

— **BEI Command**
