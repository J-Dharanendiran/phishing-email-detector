def semicolon_tokenizer(value):
    return [
        item.strip().lower()
        for item in value.split(';')
        if item.strip()
    ]