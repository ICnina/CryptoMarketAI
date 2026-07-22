import os
from pathlib import Path
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Find correct folder and load env
script_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=script_dir / ".env")

API_key = os.getenv("GROQ_API_KEY")

if not API_key:
    raise ValueError("Could not find GROQ_API_KEY. Check your .env-file")

# Setup groq client
client = Groq(api_key=API_key)

# Read crypto data
csv_path = script_dir / "Crypto_top20.csv"
df = pd.read_csv(csv_path)

# Top 3 and bottom 3 coins
top_3_winners = df.head(3)
top_3_losers = df.tail(3)

# Format data för AI-prompt
# Only 20 rows so one string is ok
market_data_string = "TOP 3 WINNERS (24h):\n"
market_data_string += top_3_winners.to_string(index=False) + "\n\n"
market_data_string += "TOP 3 LOSERS (24h):\n"
market_data_string += top_3_losers.to_string(index=False)

print("Sending crypto-data to Groq (LLama 3.1) for analysis...")

# Strict System prompt for AI
system_prompt = (
    "You are a Senior Crypto Market Analyst. Write a short, sharp, and professional 'Morning Brief' market report. "
    "Identify the overall market trend based on the provided winners and losers. "
    "STRICT RULES: "
    "1. Do NOT invent reasons, news, upgrades (e.g., Vasil, ETH 2.0), or events to explain the price action. "
    "2. Only report the numbers, trends, and percentages explicitly provided in the data. "
    "3. Maintain a strictly factual and objective tone."
)

# Call to Groq and Llama 3.1
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Here is today's pre-calculated data for the top market movers:\n\n{market_data_string}\n\nPlease write your strictly factual market report."
        }
    ],
    temperature=0.1
)

# Extract the AI's response
ai_report = completion.choices[0].message.content

# Save the report into a text file
report_path = script_dir / "crypto_morning_report.txt"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(ai_report)

print(f"Done! AI-report saved to: {report_path}")


print("\n--- TODAY'S CRYPTO MORNING BRIEF ---")
print(ai_report)
print("---------------------------------------\n")