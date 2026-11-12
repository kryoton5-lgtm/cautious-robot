"""Page-object methods isolate locators from test assertions."""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PortfolioPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(self.base_url + "/")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".project-card")))
        return self

    def click(self, selector):
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        self.driver.execute_script(
            "document.documentElement.style.setProperty('scroll-behavior','auto','important');"
            "arguments[0].scrollIntoView({block:'center',behavior:'instant'});", element
        )
        self.wait.until(lambda d: d.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return r.top >= 0 && r.bottom <= window.innerHeight;", element
        ))
        element.click()
        return element

    def visible_project_count(self):
        return len([e for e in self.driver.find_elements(By.CSS_SELECTOR, ".project-card")
                    if e.is_displayed()])

    def filter(self, name):
        self.click('[data-filter="' + name + '"]')
        return self.visible_project_count()

    def dialog_is_open(self):
        return self.driver.execute_script("return document.querySelector('#project-dialog').open")

    def status_text(self):
        return self.driver.find_element(By.ID, "solver-status").text
