from playwright.sync_api import sync_playwright

# Set up Playwright
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
# Go to Google Maps
    page.goto('https://www.google.com/maps')
    # Enter the location in the search box
    page.fill('input[aria-label="Search Google Maps"]', 'New York')
    page.press('input[aria-label="Search Google Maps"]', 'Enter')
    page.wait_for_selector('.section-result')
    # Wait for the map to load
    page.wait_for_selector('#pane > div > div.widget-pane-content.scrollable-y > div > div.widget-pane-content-holder.widget-pane-content-scroll-wrapper > div > div > div:nth-child(7) > div > div.section-layout.section-layout-root > div.section-result-content > div.section-result-text-content > div.section-result-location > span > span')

    # Get the coordinates from the map
    coordinates = page.text_content('#pane > div > div.widget-pane-content.scrollable-y > div > div.widget-pane-content-holder.widget-pane-content-scroll-wrapper > div > div > div:nth-child(7) > div > div.section-layout.section-layout-root > div.section-result-content > div.section-result-text-content > div.section-result-location > span > span')

    print('Coordinates:', coordinates)
