#intraday check at the end of the day

import yfinance as yf
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings('ignore')

#fetching stock list from excel
excel_data_df = pd.read_excel('.\Monitored_Tickers.xlsx', sheet_name='Sheet1')
indian_tickers = excel_data_df['Ticker'].tolist()

# Function to check if the stock meets the criteria
def check_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="max", interval="1d")
    #hist = stock.history(period="1y", interval="1d")
    
    if hist.empty or len(hist) < 2:
        return None
    
    current_price = hist['Close'][-1]
    all_time_high_till_yesterday = hist['High'][:-1].max()  # All-time high till yesterday
    todays_high = hist['High'][-1]
    todays_open = hist['Open'][-1]
    #breakout = FTweekhigh if all_time_high_till_yesterday > FTweekhigh else all_time_high_till_yesterday    
    
    if 50 < current_price < 3000:
        if current_price >= all_time_high_till_yesterday * 0.80:
        #if todays_high >= all_time_high_till_yesterday:# * 0.98:
            #volume = hist['Volume'][-1]
            #cmp_ath = current_price - all_time_high_till_yesterday
            #todays_high_cmp = todays_high - current_price

            return {
                'Ticker': ticker,
            }
    
    return None

# List to store the stocks that meet the criteria
filtered_stocks = []

# Loop through the tickers and apply the filter
for ticker in indian_tickers:
    result = check_stock(ticker)
    if result:
        filtered_stocks.append(result)

# Create a DataFrame from the results
filtered_stocks_df = pd.DataFrame(filtered_stocks)

# Sort the DataFrame by Volume in descending order and get the top 25 stocks
#filtered_stocks_df = filtered_stocks_df.sort_values(by='Volume', ascending=False)#.head(25)

# Calculate the sum of the 'CMP-ATH' column
#sum_cmp_ath = filtered_stocks_df['Profit'].sum()

# Print the DataFrame and the sum of 'CMP-ATH'
if not filtered_stocks_df.empty:
    print(filtered_stocks_df)
    #print(f"\nSum of 'CMP-ATH' column: {sum_cmp_ath}")
    filtered_stocks_df.to_csv('Short_List_Twenty.csv', index=False)
else:
    print("No stocks meet the criteria.")