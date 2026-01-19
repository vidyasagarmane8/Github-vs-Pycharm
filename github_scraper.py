import pandas as pd
from google_play_scraper import reviews, Sort
import time

# ==========================================
# CONFIGURATION
# ==========================================
APP_ID = 'com.whizdm.moneyview.loans'  # The app you are targeting
TARGET_YEAR = 2025
TARGET_MONTH = 12
OUTPUT_FILE = 'MoneyView_Dec25_Data.xlsx'
# ==========================================

def fetch_github_data():
    print(f"--- GITHUB SCRAPER STARTED ---")
    print(f"Target App: {APP_ID}")
    print(f"Target Date: {TARGET_MONTH}-{TARGET_YEAR}")

    collected_data = []
    continuation_token = None
    batch_num = 0
    keep_scraping = True

    while keep_scraping:
        # Fetch batch of 200 reviews
        result, continuation_token = reviews(
            APP_ID,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )

        if not result:
            break

        batch_num += 1
        newest = result[0]['at']
        oldest = result[-1]['at']
        print(f"Processing Batch {batch_num} | Date Range: {newest.date()} to {oldest.date()}")

        for review in result:
            r_date = review['at']

            # 1. Skip if date is in the future (Jan 2026+)
            if r_date.year > TARGET_YEAR or (r_date.year == TARGET_YEAR and r_date.month > TARGET_MONTH):
                continue

            # 2. Collect if date is December 2025
            if r_date.year == TARGET_YEAR and r_date.month == TARGET_MONTH:
                collected_data.append({
                    'Review_Id': review['reviewId'],
                    'App_Name': APP_ID,
                    'Review_Date': r_date.date(),
                    'Rating': review['score'],
                    'Review_Text': review['content']
                })

            # 3. Stop if we went past December (into Nov 2025 or earlier)
            if r_date.year < TARGET_YEAR or (r_date.year == TARGET_YEAR and r_date.month < TARGET_MONTH):
                keep_scraping = False
                break

        # Stop if no more token or flag is set
        if not continuation_token:
            keep_scraping = False
        
        # Polite pause
        time.sleep(0.5)

    # Export
    df = pd.DataFrame(collected_data)
    
    if not df.empty:
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\n[SUCCESS] Saved {len(df)} rows to '{OUTPUT_FILE}'")
    else:
        print("\n[INFO] No data found for the specified month.")

if __name__ == '__main__':
    fetch_github_data()
