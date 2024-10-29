

import time


def crawl_with_timeout_retry(max_retries, init_delay, timeout):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            retries = 0
            time.sleep(init_delay)
            while retries < max_retries:
                try:
                    result = fn(*args, **kwargs)
                    return result
                except TimeoutError:
                    print(f"Timeout encountered. Retrying in {timeout} seconds...")
                    time.sleep(timeout)
                    retries += 1
            print(f"Max retries reached. Crawling failed.")
            return None
        return wrapper
    return decorator