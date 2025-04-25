import requests
import sys
import time
import threading

LOGIN_URL = "http://phc.prontonetworks.com/cgi-bin/authlogin?URI=http://detectportal.firefox.com/canonical.html"

class Spinner:
    spinner_cycle = ['|', '/', '-', '\\']

    def __init__(self, delay=0.1):
        self.delay = delay
        self.busy = False
        self.spinner_thread = threading.Thread(target=self.spin)

    def spin(self):
        while self.busy:
            for char in self.spinner_cycle:
                sys.stdout.write(f'\r[{char}] Logging in... ')
                sys.stdout.flush()
                time.sleep(self.delay)

    def start(self):
        self.busy = True
        self.spinner_thread.start()

    def stop(self):
        self.busy = False
        self.spinner_thread.join()
        sys.stdout.write('\r✅ Login Attempted.        \n')

def login(username, password):
    payload = {
        "userId": username,
        "password": password,
        "serviceName": "ProntoAuthentication"
    }

    try:
        spinner = Spinner()
        spinner.start()
        response = requests.post(LOGIN_URL, data=payload, timeout=10)
        spinner.stop()

        if response.status_code == 200:
            print("✅ Login successful.")
            return True
        else:
            print(f"⚠️ Login returned status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        spinner.stop()
        print(f"❌ Login failed: {e}")
        return False
