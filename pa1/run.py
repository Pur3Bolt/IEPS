import subprocess
import datetime
command = "python process.py --threads 10"

with open("crawler.logs", "w") as log_file:
    while True:
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log_file.writelines(["\n"+"TIME:",
                             "\n"+str(datetime.datetime.now()),
                             "\n"+"SUCCESS:",
                             "\n"+result.stdout.decode("utf-8"),
                             "\n"+"ERROR:",
                             "\n"+result.stderr.decode("utf-8")])
