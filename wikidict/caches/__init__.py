import json
from gzip import compress, decompress
from pathlib import Path

CACHE_PATH = Path(__file__).parent


def load_cache_file(kind: str) -> dict[str, str]:
    file = CACHE_PATH / f"{kind}.gz"
    contents: dict[str, str] = json.loads(decompress(file.read_bytes()))
    return contents


def expand_cache_file(kind: str, **values: str) -> None:
    contents = load_cache_file(kind)
    contents |= values
    save_cache_file(kind, contents)


def save_cache_file(kind: str, contents: dict[str, str]) -> None:
    file = CACHE_PATH / f"{kind}.gz"
    file.write_bytes(
        compress(
            json.dumps(
                contents,
                check_circular=False,
                ensure_ascii=False,
                indent=0,
                sort_keys=True,
            ).encode()
        )
    )
