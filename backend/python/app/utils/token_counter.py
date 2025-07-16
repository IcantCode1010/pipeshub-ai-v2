import tiktoken

def count_tokens(text: str, model: str) -> int:
    """
    Count the number of tokens contained in ``text`` for the given ``model``.

    Args:
        text (str): The input text.
        model (str): The model name (e.g. ``"gpt-4o"``, ``"gpt-3.5-turbo"``).

    Returns:
        int: Number of tokens in ``text`` when encoded with ``model``&#39;s tokenizer.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))
