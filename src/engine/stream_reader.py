from io import TextIOBase

buffer_size = 8192


def buffered_read(stream: TextIOBase):
    chunk = stream.read(buffer_size)
    while chunk:
        for char in chunk:
            yield char
            chunk = stream.read(buffer_size)
