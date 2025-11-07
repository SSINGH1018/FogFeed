import asyncio
import csv
from playwright.async_api import async_playwright
import os
import time

async def coinlanderurls(csv_filename="coinlander_urls.csv"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://coinlander.com/projects")

        await page.wait_for_selector("button")
        properties = await page.locator("button")
        property_count = await properties.count()
        url = []

        async for i in range(property_count):
            prop = await properties.nth(i)
            # Get text to identify it
            text = await prop.text_content()
            print(f"Clicking button {i+1}/{property_count}: {text}")

            async with page.expect_navigation(timeout=10000):
                prop.click()

            # Wait or scrape data from new page
            time.sleep(2)
            print("Current URL:", page.url)

            # You could extract info here, then go back
            # Go back if needed
            await page.go_back()
            await page.wait_for_selector("button")
        await browser.close()

    # Define the root directory for saving the CSV file.
    root = await os.path.dirname(os.path.abspath(__file__))    

    # Check if the file already exists
    file_exists = await os.path.isfile(os.path.join(root, csv_filename))

    # Append the data to the CSV file.
    async with open(os.path.join(root, csv_filename), "a+", newline="") as csvfile:
        writer = await csv.writer(csvfile)
        # Write the header only if the file doesn't exist
        if not file_exists:
            await writer.writerow(["URL"])
        await writer.writerows(url)  

asyncio.run(coinlanderurls())