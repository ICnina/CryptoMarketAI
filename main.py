import os
import requests
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Adress to CoinGecko database
url ="https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 30,
    "page": 1,
    "sparkline": False
}

print("\nKnocking at CoinGecko server...\n")
response = requests.get(url, params=params)

if response.status_code == 200:
    raw_data = response.json()

    # Clean and etract data
    print("Data received, start cleaning...\n")

    # Empty list to store clean infromation
    clean_data = []

    # Loop through every coin in the raw data
    coin_list = []
    for coin in raw_data:
        coin_list.append({
            "Name": coin["name"],
            "Price_USD": coin["current_price"],
            "Change_24h_%": coin["price_change_percentage_24h"],
            "Market_Cap": coin["market_cap"]
        })
    
    # Convert to Pandas DataFrame
    df = pd.DataFrame(coin_list)

    # Filter out stable coins
    stablecoins = [
        "Tether", "USDC", "USDS", "Dai", "TrueUSD", 
        "First Digital USD", "Figure Heloc", 
        "Ethena USDe", "USD1", "Global Dollar" # <-- De nya vi hittade idag
    ]
    df = df[~df["Name"].isin(stablecoins)]

    # Sort after highest %-increase
    df_sorted = df.sort_values(by="Change_24h_%", ascending=False)

    # Save to csv with pathlib (located in same folder as the script)
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / "Crypto_top20.csv"

    # index=Fales (No extra column with row numbers)
    df_sorted.to_csv(csv_path, index=False)

    print(df_sorted.head())
    print(f"\nData saved to: {csv_path}")

else:
    print(f"Something went wrong! Statuscode: {response.status_code}") 
