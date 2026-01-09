import re

adapters = {
    "Šablonas:t+": lambda body: re.sub(r"(<sup>.+</sup>)", "", body, count=2),
}
