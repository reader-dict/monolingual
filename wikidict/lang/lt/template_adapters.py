import re

adapters = {
    "Šablonas:t+": lambda body: re.sub(r"(&nbsp;<sup>.+</sup>)", "", body, count=2),
}
