"""Browser-level contract and regression tests against the real portfolio UI."""
import csv
from pathlib import Path
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.portfolio import PortfolioPage


@pytest.fixture
def page(driver, site_url):
    return PortfolioPage(driver, site_url).open()


@pytest.mark.smoke
def test_homepage_has_expected_content_and_navigation(page):
    assert page.driver.title == "Shubham Kadam — Scientific Computing & AI Evaluation"
    assert len(page.driver.find_elements(By.CSS_SELECTOR, ".project-card")) == 4
    assert page.driver.find_element(By.CSS_SELECTOR, 'a.skip[href="#main"]').is_displayed()


@pytest.mark.regression
@pytest.mark.parametrize("category,expected", [
    ("all", 4), ("science", 2), ("evaluation", 1), ("engineering", 2)
])
def test_project_filters_show_expected_cards(page, category, expected):
    assert page.filter(category) == expected
    assert page.driver.find_element(By.ID, "filter-status").text.startswith(str(expected))


@pytest.mark.regression
def test_project_dialog_opens_and_escape_closes_it(page):
    page.click('[data-open-project="evalforge"]')
    WebDriverWait(page.driver, 5).until(lambda _: page.dialog_is_open())
    assert page.driver.find_element(By.ID, "project-title").text == "EvalForge"
    page.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    WebDriverWait(page.driver, 5).until(lambda _: not page.dialog_is_open())


@pytest.mark.regression
def test_light_dark_preference_survives_reload(page):
    initial = page.driver.find_element(By.TAG_NAME, "html").get_attribute("data-theme")
    page.click("#theme-toggle")
    changed = page.driver.find_element(By.TAG_NAME, "html").get_attribute("data-theme")
    assert changed != initial
    page.driver.refresh()
    assert page.driver.find_element(By.TAG_NAME, "html").get_attribute("data-theme") == changed


@pytest.mark.regression
def test_deterministic_zero_noise_fit_converges(page):
    page.driver.execute_script(
        "let n=document.querySelector('#noise'); n.value='0'; "
        "n.dispatchEvent(new Event('input',{bubbles:true}));"
    )
    page.click("#fit")
    WebDriverWait(page.driver, 15).until(lambda _: "Converged" in page.status_text())
    k = float(page.driver.find_element(By.ID, "parameter").text)
    rmse = float(page.driver.find_element(By.ID, "rmse").text)
    assert abs(k - 0.64) <= 0.002
    assert rmse < 0.001


@pytest.mark.regression
def test_csv_export_has_expected_header_and_row_count(page, tmp_path):
    # Configure Chrome's downloads into the isolated pytest temp directory.
    page.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow", "downloadPath": str(tmp_path)
    })
    page.click("#export")
    target = tmp_path / "shubham-kadam-synthetic-model-fit.csv"
    WebDriverWait(page.driver, 10).until(lambda _: target.exists())
    with target.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 28
    assert set(("time", "observation", "model_prediction", "residual",
                "rate_constant", "noise_sigma")) <= set(rows[0])
    assert all(0.0 <= float(row["noise_sigma"]) <= 0.12 for row in rows)


@pytest.mark.regression
def test_search_palette_keyboard_navigation(page):
    page.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL, "k")
    search = WebDriverWait(page.driver, 5).until(
        lambda d: d.find_element(By.ID, "command-search")
    )
    assert search.is_displayed()
    search.send_keys("Thermal")
    buttons = page.driver.find_elements(By.CSS_SELECTOR, "#command-results button")
    assert len(buttons) == 1
    search.send_keys(Keys.ENTER)
    WebDriverWait(page.driver, 5).until(lambda _: page.dialog_is_open())
    assert page.driver.find_element(By.ID, "project-title").text == "Thermal Reactor Twin"


@pytest.mark.regression
@pytest.mark.parametrize("width", [320, 375, 768, 1024, 1440])
def test_layout_does_not_overflow_viewport(page, width):
    page.driver.set_window_size(width, 1000)
    WebDriverWait(page.driver, 5).until(lambda d: d.execute_script(
        "return document.readyState") == "complete")
    dimensions = page.driver.execute_script(
        "return [document.documentElement.scrollWidth, window.innerWidth]")
    assert dimensions[0] <= dimensions[1] + 1, dimensions


@pytest.mark.regression
def test_mobile_navigation_opens_and_closes(page):
    page.driver.set_window_size(375, 850)
    page.click("#menu-toggle")
    assert page.driver.find_element(By.ID, "mobile-nav").is_displayed()
    page.click('#mobile-nav a[href="#lab"]')
    assert not page.driver.find_element(By.ID, "mobile-nav").is_displayed()


@pytest.mark.smoke
def test_printable_resume_route_is_available(page):
    page.driver.get(page.base_url + "/resume.html")
    assert page.driver.find_element(By.TAG_NAME, "h1").text == "SHUBHAM KADAM"
