import os
import subprocess
import sys
from datetime import timedelta
from multiprocessing.pool import ThreadPool
from pathlib import Path
from time import monotonic

# TODO: Use the official API after https://github.com/astral-sh/ruff/issues/659 is done
from ruff_api import FormatOptions, format_string

FILES = {
    "all-namespaces.py": "wikidict/namespaces.py",
    "ca-labels.py": "wikidict/lang/ca/labels.py",
    "ca-langs.py": "wikidict/lang/ca/langs.py",
    "da-langs.py": "wikidict/lang/da/langs.py",
    "de-abk.py": "wikidict/lang/de/abk.py",
    "de-langs.py": "wikidict/lang/de/langs.py",
    "de-lang-adjs.py": "wikidict/lang/de/lang_adjs.py",
    "en-form-of.py": "wikidict/lang/en/form_of.py",
    "en-scripts.py": "wikidict/lang/en/scripts.py",
    "el-aliases.py": "wikidict/lang/el/aliases.py",
    "el-labels.py": "wikidict/lang/el/labels.py",
    "el-langs.py": "wikidict/lang/el/langs.py",
    "el-topos-kind.py": "wikidict/lang/el/topos/kind.py",
    "el-topos-where.py": "wikidict/lang/el/topos/where.py",
    "en-labels.py": "wikidict/lang/en/labels.py",
    "en-langs.py": "wikidict/lang/en/langs.py",
    "en-places.py": "wikidict/lang/en/places.py",
    "en-pronunciations.py": "wikidict/lang/en/transliterator/pronunciations.py",
    "eo-dialects.py": "wikidict/lang/eo/dialects.py",
    "eo-langs.py": "wikidict/lang/eo/langs.py",
    "eo-tags.py": "wikidict/lang/eo/tags.py",
    "es-langs.py": "wikidict/lang/es/langs.py",
    "es-campos-semanticos.py": "wikidict/lang/es/campos_semanticos.py",
    "fr-contexts.py": "wikidict/lang/fr/contexts.py",
    "fr-domain-templates.py": "wikidict/lang/fr/domain_templates.py",
    "fr-langs.py": "wikidict/lang/fr/langs.py",
    "fr-racines-arabes.py": "wikidict/lang/fr/ar/racines_arabes.py",
    "fr-regions.py": "wikidict/lang/fr/regions.py",
    "fr-temps-geologiques.py": "wikidict/lang/fr/temps_geologiques.py",
    "it-codelangs.py": "wikidict/lang/it/codelangs.py",
    "it-langs.py": "wikidict/lang/it/langs.py",
    "no-labels.py": "wikidict/lang/no/labels.py",
    "no-langs.py": "wikidict/lang/no/langs.py",
    "pt-codelangs.py": "wikidict/lang/pt/codelangs.py",
    "pt-escopo.py": "wikidict/lang/pt/escopos.py",
    "pt-gramatica.py": "wikidict/lang/pt/gramatica.py",
    "pt-langs.py": "wikidict/lang/pt/langs.py",
    "ru-labels.py": "wikidict/lang/ru/labels.py",
    "ru-etymologies.py": "wikidict/lang/ru/etymologies.py",
    "ru-langs.py": "wikidict/lang/ru/langs.py",
    "ru-langs-short.py": "wikidict/lang/ru/langs_short.py",
    "sv-langs.py": "wikidict/lang/sv/langs.py",
}

# En error will be raised when the percentage of deletions from the new content
# compared to the original content is higher than this percent.
# Note: the behaviour can be skipped by using the `MANUAL=1` envar.
MAX_PERCENT_DELETIONS = 2 / 100


class MarkersNotFoundError(ValueError):
    def __str__(self) -> str:
        return "Markers not found."


class TooManyDeletionsError(ValueError):
    def __init__(self, old: int, new: int) -> None:
        self.old = old
        self.new = new

    def __str__(self) -> str:
        return f"Too many deletions ({self.new - self.old:,}), please check manually using the MANUAL=1 envar."


def replace(file: str, data: str) -> None:
    """Update contents in the file, even if there was no change."""
    path = Path(file)
    original_content = path.read_text()

    start_marker, end_marker = "# START", "# END"
    if (start := original_content.find(start_marker)) < 0 or (end := original_content.find(end_marker)) < 0:
        raise MarkersNotFoundError()

    new_content = f"{original_content[:start]}{start_marker}\n{data}{original_content[end:]}"
    new_content = format_string(__file__, new_content, options=FormatOptions(line_width=120))
    if not os.getenv("MANUAL"):
        percent_deletions = 1 - len(new_content.splitlines()) / len(original_content.splitlines())
        if percent_deletions > MAX_PERCENT_DELETIONS:
            raise TooManyDeletionsError(len(original_content.splitlines()), len(new_content.splitlines()))

    path.write_text(new_content)


def process_script(script: str, file: str, errors: dict[str, str], idx: int, total: int) -> None:
    """Process one script."""
    try:
        replace(file, subprocess.check_output([sys.executable, f"scripts/{script}"], text=True))
    except Exception as exc:
        errors[script] = str(exc)
    else:
        print(f"[{idx}/{total}] Processed {script} with success.", flush=True)


def set_output(errors: int) -> None:
    """It is very specific to GitHub Actions."""
    if "CI" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "ab") as fh:
            fh.write(f"errors={errors}\n".encode())


def main() -> int:
    """Entry point."""
    errors: dict[str, str] = {}
    total = len(FILES)
    tasks = [(script, file, errors, idx, total) for idx, (script, file) in enumerate(FILES.items(), 1)]

    processes: int | None = None
    if "MAX_PROCESS" in os.environ:
        processes = int(os.environ["MAX_PROCESS"])
    elif "CI" in os.environ:
        processes = 2

    start = monotonic()
    with ThreadPool(processes=processes) as pool:
        for _ in pool.starmap(process_script, tasks):
            pass

    set_output(len(errors))

    for script, error in errors.items():
        print(f" !! {script}")
        print(error)
        print()

    elapsed = timedelta(seconds=monotonic() - start)
    print(f"Scripts synchronized in {elapsed}!")
    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
