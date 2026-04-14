# utils/text_utils.py
import re
import nltk
from nltk.corpus import stopwords

try:
    _STOP_WORDS = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    _STOP_WORDS = set(stopwords.words('english'))

# Keep negation words — they're critical for sentiment
_NEGATION_WORDS = {
    "not","no","never","nobody","nothing","neither","nor","nowhere",
    "hardly","barely","scarcely","don't","doesn't","didn't","won't",
    "wouldn't","can't","cannot","couldn't","shouldn't","isn't","aren't",
    "wasn't","weren't","haven't","hasn't","hadn't"
}
_STOP_WORDS -= _NEGATION_WORDS

# Negation scope — words after a negation get "not_" prefix
_NEGATION_TRIGGERS = {"not","no","never","don't","doesn't","didn't",
                      "won't","can't","cannot","couldn't","isn't","aren't"}

# Emphasis multipliers — for VADER these are already handled,
# but we normalise common slang
_SLANG_MAP = {
    "luv": "love", "gr8": "great", "amazin": "amazing",
    "gud": "good",  "bro": "",      "lol": "",
    "omg": "oh my god", "wtf": "very bad", "tbh": "",
    "imo": "", "ngl": "", "ikr": "",
}


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline:
      1. Lowercase
      2. Slang normalisation
      3. Strip digits + extra whitespace
      4. Negation scoping (not_word for next 3 tokens)
      5. Stopword removal (keeping negations)
    """
    text = text.lower().strip()

    # Slang normalisation
    tokens = text.split()
    tokens = [_SLANG_MAP.get(t, t) for t in tokens]
    text   = ' '.join(t for t in tokens if t)

    # Strip digits
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Negation scoping
    tokens = text.split()
    result = []
    negate = 0
    for token in tokens:
        if token in _NEGATION_TRIGGERS:
            result.append(token)
            negate = 3          # scope: next 3 words
        elif negate > 0:
            result.append("not_" + token)
            negate -= 1
        else:
            result.append(token)

    # Stopword removal (negations already kept above)
    cleaned = [w for w in result if w not in _STOP_WORDS]
    return ' '.join(cleaned)
