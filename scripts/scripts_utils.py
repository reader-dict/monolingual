from time import sleep
from typing import Any

import requests
from requests.exceptions import HTTPError, RequestException

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "https://www.reader-dict.com"


def get_content(url: str, *, max_retries: int = 5, sleep_time: int = 5, as_json: bool = False) -> str | dict[str, Any]:
    """Fetch given *url* content with retries mechanism."""
    retry = 0
    while retry < max_retries:
        try:
            with SESSION.get(url, timeout=10) as req:
                req.raise_for_status()
                return req.json() if as_json else req.text
        except TimeoutError:
            sleep(sleep_time)
            retry += 1
        except HTTPError as err:
            resp = err.response
            if resp is not None and resp.status_code == 404:
                return ""
            wait_time = 1
            if resp is not None and resp.status_code == 429:
                wait_time = int(resp.headers.get("retry-after") or "1")
            sleep(wait_time * sleep_time)
            retry += 1
        except RequestException:
            sleep(sleep_time)
            retry += 1
    raise RuntimeError(f"Sorry, too many tries [{retry}] for {url!r}")
