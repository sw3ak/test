import requests
import time
import logging


class Logging:
    def __init__(self):
        logging.basicConfig(filename='logFile.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class CheckService:
    @staticmethod
    def check_service(url):
        try:
            start_time = time.time()
            response = requests.post(f'http://{url}', timeout=2)
            end_time = time.time()
            elapsed_time = end_time - start_time
            return response.status_code, elapsed_time
        except requests.RequestException:
            return None, None


class IsServiceStable:
    def __init__(self):
        self.valid_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
        self.error_counts = {}
        self.errors = {}

    def is_service_stable(self, url, status_code, elapsed_time):
        if url not in self.error_counts:
            self.error_counts[url] = {}
            self.errors[url] = None

            if status_code is None:
                self.error_counts[url]['None'] = self.error_counts[url].get('None', 0) + 1
                self.errors[url] = None
                return False

            if status_code not in self.valid_codes:
                error_key = str(status_code)
                self.error_counts[url][error_key] = self.error_counts[url].get(error_key, 0) + 1
                self.errors[url] = status_code
                return False

            if elapsed_time is not None and elapsed_time > 2:
                self.error_counts[url]['408'] = self.error_counts[url].get('408', 0) + 1
                self.errors[url] = 408
                return False

            for error, count in self.error_counts[url].items():
                if count > 3 and self.errors[url] == error:
                    return False
        else:
            self.error_counts[url] = {}
            self.errors[url] = None
            return True


class ServiceMonitor:
    SERVICES = [
        'formit.fake',
        'datavalidator.fake',
        'leadsync.fake',
        'bitdashboard.fake'
    ]

    def __init__(self):
        self.logger = Logging()
        self.checker = CheckService()
        self.validator = IsServiceStable()

    def main_func(self):
        while True:
            for url in self.SERVICES:
                status_code, elapsed_time = self.checker.check_service(url)
                is_stable = self.validator.is_service_stable(url, status_code, elapsed_time)
                log_message = (
                    f"URL: http://{url}, Status: {status_code if status_code else 'None'}, "
                    f"Response Time: {f'{elapsed_time:.2f} second' if elapsed_time else 'None'}, "
                    f"Stable: {is_stable}"
                )
                logging.info(log_message)
            time.sleep(300)


if __name__ == "__main__":
    monitor = ServiceMonitor()
    monitor.main_func()