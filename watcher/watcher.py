import time
import re
import os
import subprocess
import logging

LOG_OUTPUT_PATH = os.environ.get("WATCHER_LOG_FILE", "/var/log/watcher.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_OUTPUT_PATH),
        logging.StreamHandler() 
    ]
)

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/cron.log")
APP_PHP_PATH = os.environ.get("MAX_WORKERS_FILE", "/app/config/app.php")
MAX_WORKERS_KEY = "'maxworkers'"
ERROR_PATTERN = "Cannot start worker: Too many workers"

# Nombre de cycles sans erreur avant de réduire les workers
NO_ERROR_THRESHOLD = 60
MIN_WORKERS = 2


def get_workers():
    val = subprocess.run(
        "cat /app/config/app.php | grep 'maxworkers' | awk -F'=>' '{print $2}' | awk -F',' '{print $1}' | awk '{print $1}'",
        shell=True,
        capture_output=True,
        text=True
    )
    return val.stdout.strip()

def get_current_max_workers():
    with open(APP_PHP_PATH, 'r') as f:
        for line in f:
            if MAX_WORKERS_KEY in line:
                match = re.search(r"\s*'maxworkers'\s*=>\s*(\d+)", line)
                if match:
                    return int(match.group(1))
    return None

def set_max_workers(new_value):
    updated = False
    lines = []
    with open(APP_PHP_PATH, 'r') as f:
        for line in f:
            if MAX_WORKERS_KEY in line:
                line = re.sub(r"('maxworkers'\s*=>\s*)\d+", r"\g<1>" + str(new_value), line)
                updated = True
            lines.append(line)
    if updated:
        with open(APP_PHP_PATH, 'w') as f:
            f.writelines(lines)
        logging.info(f"Updated maxWorkers to {new_value}")
    else:
        logging.warning("maxWorkers setting not found or unchanged")
        

def monitor_log():
    logging.info("Monitoring log for scaling hints...")
    last_position = 0
    no_error_cycles = 0
    
    max_workers = int(get_workers())
    logging.info(f" maxWorkers  = {max_workers}")

    while True:
        error_count = max_workers

        try:
            with open(LOG_FILE, 'r') as f:
                f.seek(last_position)
                lines = f.readlines()
                last_position = f.tell()
        except FileNotFoundError:
            logging.error(f"{LOG_FILE} not found. Retrying...")
            time.sleep(5)
            continue

        for line in lines:
            if ERROR_PATTERN in line:
                error_count += 1
                
        logging.info(f"number of error:  {error_count} current workers + 1: {max_workers + 1} ")

        # SCALE UP
        if error_count >= (max_workers + 1):
            logging.info(f"Detected {error_count} errors (threshold {max_workers + 1}) → scaling up.")
            max_workers += 1
            set_max_workers(max_workers)
            no_error_cycles = 0

        # SCALE DOWN
        elif error_count == max_workers:
            no_error_cycles += 1
            logging.info(f"No errors this cycle ({no_error_cycles}/{NO_ERROR_THRESHOLD})")
            if no_error_cycles >= NO_ERROR_THRESHOLD:
                if max_workers > MIN_WORKERS:
                    max_workers -= 1
                    logging.info(f"No errors for {NO_ERROR_THRESHOLD} cycles → scaling down to {max_workers}.")
                    set_max_workers(max_workers)
                else:
                    logging.info(f"Already at minimum workers ({MIN_WORKERS}) → no scale down.")
                no_error_cycles = 0
        else:
            logging.info(f"Detected {error_count} errors but below threshold → no scale.")
            no_error_cycles = 0

        time.sleep(10)

if __name__ == "__main__":
    monitor_log()
