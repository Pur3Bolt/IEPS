from _crawler import Crawler
import argparse
import sys
import concurrent.futures
import threading


parser = argparse.ArgumentParser(description='Crawler')
parser.add_argument('--threads', type=int)

args = parser.parse_args(sys.argv[1:])
number_of_threads = vars(args).get('threads', 5)
crawlers = []
lock1 = threading.Lock()
lock2 = threading.Lock()

with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads) as executor:
    # executor.shutdown(wait=False)
    for idx in range(number_of_threads):
        crawler = Crawler(lock1, lock2)
        crawlers.append(crawler)
        executor.submit(crawler.process)


