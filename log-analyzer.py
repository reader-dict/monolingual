import sys
from pathlib import Path

file = Path(sys.argv[1])
with file.open("rt", encoding="utf-8") as fh:
    jobs = {}
    for line in fh:
        if not line.startswith("INFO:wikidict.render"):
            continue
        job, word = line.split(" ", 1)
        job = job.split(":")[-1]
        if "Job done." in word:
            jobs.pop(job, None)
        else:
            jobs[job] = word

print(jobs)
