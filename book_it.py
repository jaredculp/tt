import datetime
import os

from playwright.sync_api import Playwright, sync_playwright

EMAIL = os.environ["TT_EMAIL"]
NAME = os.environ["TT_NAME"]
PHONE = os.environ["TT_PHONE"]
TT_FORMAT = "%m-%d-%Y"
TT_OUTPUT = "latest-tee-time.txt"


def next_thurs():
    return datetime.date(2022, 10, 28)
    day = datetime.date.today()
    while day.weekday() != 3 or day == datetime.date.today():
        day += datetime.timedelta(1)

    return day


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    try:
        context.tracing.start(screenshots=True, snapshots=True)

        page = context.new_page()
        page.goto(
            f"https://jeffersonville-golf-club.book.teeitup.golf/?course=5968&date={next_thurs()}&golfers=4&end=09&start=07&transportation=Riding"
        )

        # grab the earliest tee time
        page.get_by_text("Book Now").first.click()

        # book for 4 people
        page.get_by_test_id("button-value-4").click()
        page.get_by_text("Proceed to Checkout").click()
        page.wait_for_url("https://jeffersonville-golf-club.book.teeitup.golf/login")

        # fill out email as guest
        page.get_by_label("Email Address").click()
        page.get_by_label("Email Address").fill(EMAIL)
        page.get_by_text("Continue as Guest").click()
        page.wait_for_url("https://jeffersonville-golf-club.book.teeitup.golf/checkout")

        # fill out name
        page.locator('input[name="Payment\\.Name"]').click()
        page.locator('input[name="Payment\\.Name"]').fill(NAME)

        # fill out phone
        page.get_by_test_id("mobile-phone-number-component").click()
        page.get_by_test_id("mobile-phone-number-component").fill(PHONE)

        # agree
        page.get_by_text("I agree to the Terms and Conditions").check()

        # book
        # page.get_by_text("Complete your purchase").click()

    finally:
        # TODO guard and move outside finally
        with open(TT_OUTPUT, "w") as f:
            f.write(next_thurs().strftime(TT_FORMAT))

        context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()


with sync_playwright() as playwright:
    # only run if we don't have a tee time for next thursday
    with open(TT_OUTPUT, "r") as f:
        tee_time = f.read()
        if datetime.datetime.strptime(tee_time, TT_FORMAT).date() < next_thurs():
            run(playwright)
