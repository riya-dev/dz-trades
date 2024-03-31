# riya dev & luke zhu
# luke is a bba who got that options knowledge
# riya is a cs engr who got that coding knowledge
import math
from scipy.stats import norm
import requests
from urllib.parse import quote
import os
from dotenv import load_dotenv
from datetime import datetime, date


load_dotenv()
# polygon_api_key = os.getenv('POLYGON_API_KEY')
# polygon_key_id = os.getenv('POLYGON_KEY_ID')
marketdata_api_token = os.getenv('MARKETDATA_API_TOKEN')


def api_interest_rate():
   """ API Call for risk-free rate. """
   # https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates
   base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
   endpoint = "/v2/accounting/od/avg_interest_rates"
   params = {
       "fields": "avg_interest_rate_amt, record_date",
       "filter": "security_desc:eq:" + quote("Treasury Bills"),
       "sort": "-record_date",
   }
   full_url = f"{base_url}{endpoint}"
   response = requests.get(full_url, params=params)

   if response.status_code == 200:
       data = response.json()
       return data["data"][0]["avg_interest_rate_amt"]

   else:
       return f"Error: {response.status_code}"


def api_marketdata_expiration(ticker, headers):
   """MarketData API Call for expiration dates."""
   base_url = "https://api.marketdata.app/v1/options/expirations"
   endpoint = f"/{ticker}"
   full_url = f"{base_url}{endpoint}"

   response = requests.get(full_url, headers=headers)

   if response.status_code in (200, 203):
       data = response.json()
       expiration_dates = data["expirations"]
       print("Expiration date:", expiration_dates[0])
       print()
        # print("Expiration dates:")
        # print(expiration_dates)
        # print()
       return expiration_dates[0]
   else:
       return f"Error: {response.status_code}"


def api_marketdata_strikes(ticker, expiration_date, headers):
   """MarketData API Call for expiration dates."""
    # expiration_date = input("Enter expiration date: ")
    # print()
   # TODO error checking for expiration date formatting
   base_url = "https://api.marketdata.app/v1/options/strikes"
   params = {
       'expiration': expiration_date
   }
   response = requests.get(f"{base_url}/{ticker}", params=params, headers=headers)

   if response.status_code in (200, 203):
       data = response.json()
       strike_prices = data[f"{expiration_date}"]
        # print("Strike prices:", strike_prices)
        # print()
       return strike_prices
   else:
       return f"Error: {response.status_code}"


def api_marketdata_lookup(strike_price, ticker, expiration, headers):
   """MarketData API Call for option symbol lookup."""
   # strike_price = input("Enter strike price: ")
   # print()
   option_side = "call"

   user_input = f"{ticker} {expiration} ${strike_price} {option_side}"
   encoded_user_input = quote(user_input)

   url = f"https://api.marketdata.app/v1/options/lookup/{encoded_user_input}"
   response = requests.get(url, headers=headers)

   if response.status_code in (200, 203):
       data = response.json()
       option_symbol = data['optionSymbol']
      #  print("Option symbol:", option_symbol)
      #  print()
       return option_symbol, float(strike_price)
   else:
       return f"Error: {response.status_code}"


def api_marketdata_quotes(option_symbol, headers):
   """MarketData API Call for underlyingPrice, iv, vega values."""
   # user_input = f"{ticker} {expiration} ${strike_price} {option_side}"
   # encoded_user_input = quote(user_input)

   url = f"https://api.marketdata.app/v1/options/quotes/{option_symbol}/"

   response = requests.get(url, headers=headers)

   if response.status_code in (200, 203):
       data = response.json()
       underlying_price = data["underlyingPrice"][0]
       iv = data["iv"][0]
       return underlying_price, iv
   else:
       return f"Error: {response.status_code}"


def strike_price_loop_calls():
   """Calling black-schole on several strike prices."""
   ticker = input("Enter a ticker: ")
   print()

   headers = {
       'Accept': 'application/json',
       'Authorization': f'Bearer {marketdata_api_token}'
   }

   # response -> option ticker expiration
   expiration_date = api_marketdata_expiration(ticker, headers)

   # response -> available strike prices
   strike_prices = api_marketdata_strikes(ticker, expiration_date, headers)
   
   # t_m calculation
   today = datetime.combine(date.today(), datetime.min.time())
   date_format = "%Y-%m-%d"
   expiration_date_object = datetime.strptime(expiration_date, date_format)
   t_m = (expiration_date_object - today).days / 365

   middle_index = (len(strike_prices) - 16) // 2
   end_index = middle_index + 15

   for i in range(middle_index, end_index + 1):
       strike_price = strike_prices[i]

       # response -> option symbol
       option_symbol, strike_price = api_marketdata_lookup(strike_price, ticker, expiration_date, headers)

       # quotes
       underlyingPrice, iv = api_marketdata_quotes(option_symbol, headers)

       if iv == 0:
           continue
        
       print("strike price:", strike_prices[i])

       option_price = black_scholes(underlyingPrice, strike_price, interest_rate, t_m, iv)
       print("---")
       print(f"Black-Scholes Call Option Price: {option_price}")
       print()

   return


def api_marketdata():
   """MarketData api calls."""
   ticker = input("Enter a ticker: ")
   print()
   headers = {
       'Accept': 'application/json',
       'Authorization': f'Bearer {marketdata_api_token}'
   }

   # response -> option ticker expiration
   api_marketdata_expiration(ticker, headers)

   # response -> available strike prices
   expiration, strike_prices = api_marketdata_strikes(ticker, headers)

   # response -> option symbol
   option_symbol, strike_price = api_marketdata_lookup(ticker, expiration, headers)
  
   # quotes
   underlyingPrice, iv = api_marketdata_quotes(option_symbol, headers)

   return expiration, option_symbol, strike_price, underlyingPrice, iv


def black_scholes(S_t, K, r, t, iv):
   """Black_scholes algorithm."""
   # C = call option price
   # S_t = spot price
   # K = strike price
   # r = risk-free interest rate
   # t = time to maturity (3/365)
   # sigma = volatility of the asset

   # C = N(d_1)S_t - N(d_2)Ke^{-rt}
   # d_1 = (ln (S_t / K) + (r + (sigma^2 / 2))t) / (sigma sqrt(t))
   # d_2 = d_1 - \sigma \sqrt(t)

   print("spot price (S_t):\t\t", S_t, "\nstrike price (K):\t\t", K, "\nrisk-free interest rate (r):\t", r, "\ntime to maturity (t):\t\t", t, "\nimplied volatility (iv):\t", iv)

   d1 = (math.log(S_t / K) + (t * (r + 0.5 * iv**2))) / (iv * math.sqrt(t))
   d2 = d1 - iv * math.sqrt(t)
   C = norm.cdf(d1) * S_t - norm.cdf(d2) * K * math.e**(-r * t)
   return C


if __name__ == "__main__":
   interest_rate = float(api_interest_rate())

   # api_marketdata()
   strike_price_loop_calls()

   # expiration, option_symbol, strike_price, underlyingPrice, iv = api_marketdata()

   # t_m = 1 / 365 # TODO: fix the time to maturity
   # option_price = black_scholes(underlyingPrice, strike_price, interest_rate, t_m, iv)
   # print("---")
   # print(f"Black-Scholes Call Option Price: {option_price}")