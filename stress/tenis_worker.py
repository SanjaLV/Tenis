import random
import time

import requests
import threading


class Crawler(threading.Thread):

    def run(self):

        cnt = 0
        max_time = 0
        totall_time = 0

        #print("thread started!")

        w8_time = random.randint(10, 300) / 10
        time.sleep(w8_time)

        t_end = time.time() + 120
        while time.time() < t_end:
            # Run for 1min
            cnt += 1

            rand = random.randint(1, 50)
            r = requests.get("http://localhost:8000/core?page=" + str(rand))
            e_time = r.elapsed.total_seconds()
            max_time = max(max_time, e_time)
            totall_time += e_time

            w8_time = random.randint(5, 100) / 10
            time.sleep(w8_time)

        #print("thread ended")
        self.cnt = cnt
        self.max_time = max_time
        self.totall_time = totall_time


def main():


    user_count = 50

    while True:

        threads = []

        for x in range(user_count):
            threads.append(Crawler())

        for x in range(user_count):
            threads[x].start()

        for x in range(user_count):
            threads[x].join()

        request_count = 0
        max_time = 0.0
        totall_time = 0.0

        for x in range(user_count):
            request_count += threads[x].cnt
            max_time = max(max_time, threads[x].max_time)
            totall_time += threads[x].totall_time

        print("Worker ", user_count)
        print("request count:", request_count)
        print("max time     :", max_time)
        print("avg time     :", totall_time / request_count)
        print("totall time  :", totall_time)
        print("req/sec      :", request_count / 120.0)

        if (max_time > 0.9):
            break

        user_count += 1





if __name__ == '__main__':
    main()




