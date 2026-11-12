# Test automation portfolio: Selenium + Python + pytest

A working, reviewable quality-engineering project targeting this repository's real interactive website. It demonstrates the skills commonly evaluated for **Associate Test Automation Engineer** roles: test planning, Python automation, Selenium WebDriver, pytest, maintainable locators, regression testing, defect evidence, and CI/CD.

This is a public, synthetic demo portfolio — **not** Oracle/Cerner code or confidential client work.

## Architecture

```text
qa-automation/
├── conftest.py               # Local HTTP fixture, Chrome lifecycle, failure screenshots
├── pages/portfolio.py        # Page Object Model for stable Selenium interactions
├── tests/test_ui.py          # Browser smoke and regression scenarios
├── tests/test_http.py        # HTTP response and asset contract checks
├── pytest.ini                # Test categories
├── requirements.txt          # Python dependencies
└── README.md                 # Runbook and evidence map
.github/workflows/selenium-qa.yml
```

## Covered scenarios and expected results

| Suite | Evidence |
| --- | --- |
| Smoke | Homepage and navigation load; resume route works |
| Functional | Project filtering matches expected categories; dialogs open/close |
| State | Theme preferences persist across refresh |
| Numerical regression | Noise-free fit recovers k ≈ 0.640 with low error |
| Data integrity | CSV export includes 28 rows and schema columns |
| Keyboard | Command palette filters and opens a project |
| Responsive | 320, 375, 768, 1024, 1440 px widths have no overflow |
| Mobile | Navigation opens, follows links, and closes |
| HTTP | Main assets respond 200 and missing resources return 404 |

The suite runs a **local HTTP server** over checked-in files. No production dependencies, accounts, external API keys, or live cloud resources are needed. Tests are deterministic, parameterized and isolated with a fresh Chrome session per browser case.

## Run locally (free)

Prerequisites: Python 3.10+, Chrome/Chromium and a compatible ChromeDriver.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r qa-automation/requirements.txt
python -m pytest qa-automation/tests -v \
  --junitxml=qa-automation/junit.xml \
  --html=qa-automation/report.html --self-contained-html
```

On Windows, activate with `.venv\Scripts\activate`.

For custom Chrome/ChromeDriver paths, set `CHROME_BIN` and `CHROMEDRIVER`.

## Continuous integration

[GitHub Actions workflow](../.github/workflows/selenium-qa.yml) runs on relevant pushes, pull requests and manual dispatch. CI installs Python and ChromeDriver, runs both test suites, and uploads an HTML report, JUnit XML, and failure screenshots as downloadable artifacts. A passing badge reflects a real run, not an assertion made in this README.

## Quality and defect workflow

1. Reproduce the issue with a named pytest case and a stable input.
2. Preserve a failure screenshot under `qa-automation/artifacts/`.
3. Record expected vs. observed behavior, reproduction steps and impacted build.
4. Fix the code or test, then rerun the affected case and full regression suite.
5. Review CI artifacts before merging.

### Known limitations

- Chrome-only in CI; no real device or cross-browser coverage.
- No accessibility audit tooling or performance/load SLA is claimed.
- The project is a portfolio demonstration, not professional tenure evidence.
- Test count is intentionally bounded rather than inflated.
