def tokenize(text: str) -> list[str]:
    #cleaned = "".join(c if c.isalnum() or c == '_' else " " for c in text)
    cleaned = ""
    for c in text:
        if c.isalnum() or c == "_":
            cleaned = "".join(cleaned + "c")
        else:
            cleaned = "".join(cleaned + " ")
    return cleaned.lower().split()


print(tokenize("Ceci est un test pour voir si ce putain-de-truc PeUx fonctionner"))
