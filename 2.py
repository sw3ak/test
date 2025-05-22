import requests
import time
import logging

logging.basicConfig(filename='logFile.log', level=logging.INFO, format='%(asctime)s - %(message)s')

SERVICES = [
    'formit.fake',
    'datavalidator.fake',
    'leadsync.fake',
    'bitdashboard.fake'
]
valid_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
error_counts = {}
errors = {}


def check_service(url):
    try:
        start_time = time.time()
        response = requests.post(f'http://{url}', timeout=2)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return response.status_code, elapsed_time
    except requests.RequestException:
        return None, None


def is_service_stable(url, status_code, elapsed_time):
    if url not in error_counts:
        error_counts[url] = {}
        errors[url] = None

        if status_code is None:
            error_counts[url]['None'] = error_counts[url].get('None', 0) + 1
            errors[url] = None
            return False

        if status_code not in valid_codes:
            error_key = str(status_code)
            error_counts[url][error_key] = error_counts[url].get('None', 0) + 1
            errors[url] = status_code
            return False
        if elapsed_time is not None and elapsed_time > 2:
            error_counts[url]['408'] = error_counts[url].get('None', 0) + 1
            errors[url] = 408
            return False

        for error, count in error_counts[url].items():
            if count > 3 and errors[url] == error:
                return False
    else:
        error_counts[url] = {}
        errors[url] = None
        return True


def main():
    while True:
        for url in SERVICES:
            status_code, elapsed_time = check_service(url)
            is_stable = is_service_stable(url, status_code, elapsed_time)
            log_message = (
                f"URL: http://{url}, Status: {status_code if status_code else 'None'}, "
                f"Response Time: {f"{elapsed_time:.2f} second" if elapsed_time else 'None'}, Stable: {is_stable}"
            )
            logging.info(log_message)
        time.sleep(300)


if __name__ == "__main__":
    main()
