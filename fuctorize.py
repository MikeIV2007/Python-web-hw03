import multiprocessing
import logging
import time

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def factorize_single(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors


def factorize(*numbers):
    num_cores = multiprocessing.cpu_count()
    logging.debug(f"\nCPU has {num_cores} cores")

    pool = multiprocessing.Pool(processes=num_cores)
    result = []

    result = pool.map(factorize_single, numbers)

    pool.close()
    logging.debug(f"\nPool stautus: {pool}")
    pool.join()

    return result


if __name__ == "__main__":
    logging.debug("\nProgramm Started")
    start_timer = time.perf_counter()

    a, b, c, d = factorize(128, 255, 99999, 10651060)

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [
        1,
        2,
        4,
        5,
        7,
        10,
        14,
        20,
        28,
        35,
        70,
        140,
        76079,
        152158,
        304316,
        380395,
        532553,
        760790,
        1065106,
        1521580,
        2130212,
        2662765,
        5325530,
        10651060,
    ]

    finish = time.perf_counter()
    logging.debug(f"\nProgramm finished in {finish-start_timer} seconds\n")
