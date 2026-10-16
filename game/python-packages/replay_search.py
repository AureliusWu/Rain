"""Filter a supplied native history without consulting or changing the story."""
import unicodedata


def normalize_history_text(value):
    return " ".join(unicodedata.normalize("NFKC", value).lower().split())


def history_speakers(history, plain=lambda value: value):
    return list(dict.fromkeys(plain(entry.who or "旁白") for entry in history))


def filter_history(history, query="", speaker="", plain=lambda value: value):
    terms = normalize_history_text(query).split()
    found = []
    for index, entry in enumerate(history):
        who = plain(entry.who or "旁白")
        if speaker and speaker != who:
            continue
        text = normalize_history_text(who + " " + plain(entry.what))
        if all(term in text for term in terms):
            # Native history indices remain stable after filtering, including voices.
            found.append((index, entry))
    return found
