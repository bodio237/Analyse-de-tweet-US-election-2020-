import re
import pandas as pd

# Regex de base
URL_RE = re.compile(r'https?://\S+|www\.\S+')          # URLs
MENTION_RE = re.compile(r'@\w+')                      # @user
HASHTAG_RE = re.compile(r'#(\w+)')                    # #mot -> mot
WS_RE = re.compile(r'\s+')                            # espaces multiples

# Regex pour enlever emojis + ponctuation forte
EMOJI_PUNCT_RE = re.compile(
    r'[^\w\s]'                                        # tout ce qui n'est pas lettre/chiffre/espace
)


def fix_mojibake(s: str):
    """Corrige des artefacts d'encodage (ex. 'Ã©' -> 'é') si détecté."""
    if pd.isna(s):
        return s
    s = str(s)
    try:
        if "Ã" in s or "Â" in s:
            return s.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        pass
    return s


def clean_text(t: str):
    """Nettoyage complet du champ tweet pour l'analyse de sentiments."""
    if pd.isna(t):
        return t
    t = str(t)

    # 1) supprimer les URLs
    t = URL_RE.sub(' ', t)

    # 2) supprimer les mentions
    t = MENTION_RE.sub(' ', t)

    # 3) enlever le # mais garder le mot (#Trump -> Trump)
    t = HASHTAG_RE.sub(r'\1', t)

    # 4) passer en minuscules
    t = t.lower()

    # 5) supprimer emojis et ponctuation forte
    t = EMOJI_PUNCT_RE.sub(' ', t)

    # 6) compacter espaces et sauts de ligne
    t = WS_RE.sub(' ', t).strip()

    return t


def is_retweet_from_text(t: str) -> bool:
    if pd.isna(t):
        return False
    return str(t).startswith("RT @")
