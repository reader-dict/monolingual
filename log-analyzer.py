import sys
from pathlib import Path

file = Path(sys.argv[1])
with file.open("rt", encoding="utf-8") as fh:
    jobs = {}
    for line in fh:
        if "INFO:wikidict.render" not in line:
            continue
        *_, job, word = line.split(" ", 3)
        job = job.split(":")[-1]
        if "Job done." in word:
            jobs.pop(job, None)
        else:
            jobs[job] = word.strip()

main_proc = list(jobs.keys())[0]
jobs.pop(main_proc, None)
print(sorted(jobs.items()))
