CHUNK_SIZE = 64 * 1024


class FileTooLargeError(Exception):
    pass


async def read_limited(file, limit: int) -> bytes:
    """Read an upload in chunks, aborting as soon as it exceeds `limit`."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise FileTooLargeError
        chunks.append(chunk)
    return b"".join(chunks)
