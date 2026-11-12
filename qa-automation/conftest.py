"""Isolated local site, Chrome WebDriver, and failure evidence for Selenium QA."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
from threading import Thread

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "qa-automation" / "artifacts"


class SilentHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@pytest.fixture(scope="session")
def site_url():
    handler = partial(SilentHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


@pytest.fixture
def driver(request):
    options = Options()
    if os.environ.get("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]
    for option in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                   "--window-size=1440,1000", "--force-device-scale-factor=1"):
        options.add_argument(option)
    driver_path = os.environ.get("CHROMEDRIVER")
    service = Service(executable_path=driver_path) if driver_path else Service()
    browser = webdriver.Chrome(service=service, options=options)
    browser.set_page_load_timeout(30)
    try:
        yield browser
    finally:
        if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
            ARTIFACTS.mkdir(parents=True, exist_ok=True)
            name = re.sub(r"[^a-zA-Z0-9_-]+", "_", request.node.nodeid)[-135:]
            browser.save_screenshot(str(ARTIFACTS / (name + ".png")))
        browser.quit()
