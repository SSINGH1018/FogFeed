import asyncio
import csv
from playwright.sync_api import sync_playwright
import os
import time

def coinlanderurls(csv_filename="coinlander_urls.csv"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://coinlander.com/projects")
        page.wait_for_selector("button:has-text('Invest')")
        properties = page.locator("button:has-text('Invest')")
        property_count = properties.count()
        print("Total buttons found:", property_count)
        url = []

        for i in range(property_count):
            prop = properties.nth(i)
            # Get text to identify it
            text = prop.text_content()
            print(f"Clicking button {i+1}/{property_count}: {text}")
            prop.click()

            # Wait or scrape data from new page
            page.wait_for_selector("a") 
            print("Current URL:", page.url)
            url.append([page.url])

            # You could extract info here, then go back
            # Go back if needed
            page.go_back()
        browser.close()

    # Define the root directory for saving the CSV file.
    root = os.path.dirname(os.path.abspath(__file__))    

    # Check if the file already exists
    file_exists = os.path.isfile(os.path.join(root, csv_filename))

    # Append the data to the CSV file.
    with open(os.path.join(root, csv_filename), "a+", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writerow(["URL"])
        writer.writerows(url)  

if __name__ == "__main__":
    coinlanderurls()