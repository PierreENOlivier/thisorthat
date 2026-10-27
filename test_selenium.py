from thisorthat import ClassicAPI, TraitScrapper
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()

try:
    driver.get("https://eol.org/pages/45514192/data")

    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    print("Title:", driver.title)
    print("URL:", driver.current_url)
    print(driver.find_element("tag name", "body").text)

finally:
    driver.quit()