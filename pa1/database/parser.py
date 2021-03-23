def prepare(data):
    new_data = {}
    for key, value in data.items():
        if isinstance(value, (int, float,)):
            value = repr(value)
        elif isinstance(value, str):
            value = repr(value.replace("'", "\""))
        elif value is None:
            value = 'NULL'
        new_data[key] = value
    return new_data