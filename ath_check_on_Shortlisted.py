#intraday check at the end of the day

import yfinance as yf
import pandas as pd
import warnings
import datetime

# Ignore warnings
warnings.filterwarnings('ignore')

#fetching stock list from excel
excel_data_df = pd.read_excel('C:\\Users\\arvin\\Downloads\\susp\\stocks\\Short_List_Twenty.xlsx', sheet_name='Short_List_Twenty')
indian_tickers = excel_data_df['Ticker'].tolist()

# Function to check if the stock meets the criteria
def check_stock(ticker):
    stock = yf.Ticker(ticker)
    #hist = stock.history(period="1y", interval="1d")
    hist = stock.history(period="max", interval="1d")
    try:
        FTweekhigh = stock.info['fiftyTwoWeekHigh']
    except KeyError as e:
        print(f"KeyError for {ticker}: {e}")
        #return NA value to FTweekhigh
        FTweekhigh = 0
        #return None
    
    
    if hist.empty or len(hist) < 2:
        return None
    
    current_price = hist['Close'][-1]
    all_time_high_till_yesterday = hist['High'][:-1].max()  # All-time high till yesterday
    todays_high = hist['High'][-1]
    todays_open = hist['Open'][-1]
    #sector = stock.info['sector']
    #FTweekhigh = stock.info['fiftyTwoWeekHigh']
    #write the logic to tell ftweekhigh should be equal not to zero in a if else and condition
    breakout = FTweekhigh if all_time_high_till_yesterday > FTweekhigh and FTweekhigh != 0  else all_time_high_till_yesterday
    
    if 50 < current_price < 3000:
        #if current_price >= all_time_high_till_yesterday * 0.98:
        if todays_high >= breakout+1:# * 0.98:
            volume = hist['Volume'][-1]
            cmp_ath = current_price - breakout
            todays_high_cmp = todays_high - current_price


            # Determine entry, exit, and SL prices
            if todays_open > breakout:
                entry = todays_open
                sl = breakout-1
                exit = max(current_price, sl)
            else:
                entry = breakout
                #sl = all_time_high_till_yesterday * 0.98
                sl = max(todays_open, breakout * 0.99)-1
                exit = max(current_price, sl)

            # Determine if SL was hit
            sl_hit = "Yes" if current_price < sl else "No"

            # Calculate profit
            profit = exit - entry
            
            return {
                'Ticker': ticker,
                'ATH': all_time_high_till_yesterday,
                '52WeekHigh': FTweekhigh,
                'Breakout' : breakout,
                'Today\'s High': todays_high,
                'Today High trail SL' : todays_high*0.02,
                'T_open': todays_open,
                'CMP': current_price,
                #'CMP-ATH': cmp_ath,
                #'Today\'s High - CMP': todays_high_cmp,
                'SL': sl,
                'SL Points' : entry-sl,
                'SL-HIT': sl_hit,
                'Volume': volume,
                'Entry': entry,
                'Exit': exit,
                'Profit': profit
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
filtered_stocks_df = filtered_stocks_df.sort_values(by='Volume', ascending=False)#.head(25)

# Calculate the sum of the 'CMP-ATH' column
sum_cmp_ath = filtered_stocks_df['Profit'].sum()

# Print the DataFrame and the sum of 'CMP-ATH'
if not filtered_stocks_df.empty:
    print(filtered_stocks_df)
    print(f"\nToday's Profit : {sum_cmp_ath}")
    print(f"\nTrailig SL high profit : {filtered_stocks_df['Today High trail SL'].sum()}")
    print(f"\nTotal Capital used : {filtered_stocks_df['Entry'].sum()}")
    print(f"\nTotal return for the day : {(sum_cmp_ath/filtered_stocks_df['Entry'].sum())*100}")
    print(f"\nWith leverage of 80% capital used : {filtered_stocks_df['Entry'].sum()*0.2}")
    print(f"\nTotal return for the day with leverage : {(sum_cmp_ath/(filtered_stocks_df['Entry'].sum()*0.2))*100}")
    x = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    #filtered_stocks_df.to_csv('strategy_result_'+x+'.csv', index=False)
    filtered_stocks_df.to_csv('strategy_results_1.csv', index=False)
else:
    print("No stocks meet the criteria.")