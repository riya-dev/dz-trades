import math
from scipy.stats import norm
import requests
from urllib.parse import quote
import os
from dotenv import load_dotenv


# polygon api keys
load_dotenv()
api_key = os.getenv('API_KEY')
key_id = os.getenv('KEY_ID')


def api_all_tickers():
    """ API Call for all etf stock option tickers. """
    base_url = "https://api.polygon.io"
    endpoint = "/v3/reference/tickers?type=ETF&market=stocks&active=true&apiKey="
    full_url = f"{base_url}{endpoint}{api_key}"

    response = requests.get(full_url)

    if response.status_code == 200:
        data = response.json()["results"]
        ticker_list = [entry['ticker'] for entry in data]
        print(ticker_list)
        return ticker_list[0]
    else:
        return f"Error: {response.status_code}"


def api_call_interest_rate():
    """ API Call for risk-free rate. """
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

    # https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates


def api_call_spot_price():
    url = "https://api.polygon.io/v2/aggs/ticker/O:TSLA230113C00015000/range/1/day/2023-01-01/2023-01-11"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return


def api_call_strike_price():
    """ API Call for strike price """
    base_url = "https://api.polygon.io"
    endpoint = "v3/reference/options/contracts/"
    params = {
        "fields": "strike_price",
        # "filter": "ticker:eq:" + quote("O:AAPL211119C00085000") + quote(", ") + "contract_type:eq:"),
        "sort": "-record_date",
    }
    return


def black_scholes(S_t, K, r, t, sigma):
    """ black_scholes algorithm """
    # C = call option price
    # S_t = spot price
    # K = strike price
    # r = risk-free interest rate
    # t = time to maturity (3/365)
    # sigma = volatility of the asset

    # C = N(d_1)S_t - N(d_2)Ke^{-rt}
    # d_1 = (ln (S_t / K) + (r + (sigma^2 / 2))t) / (sigma sqrt(t))
    # d_2 = d_1 - \sigma \sqrt(t)

    print("spot price (S_t):\t\t", S_t, "\nstrike price (K):\t\t", K, "\nrisk-free interest rate (r):\t", r, "\ntime to maturity (t):\t\t", t, "\nsigma:\t\t\t\t", sigma)

    d1 = (math.log(S_t / K) + (t * (r + 0.5 * sigma**2))) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    C = norm.cdf(d1) * S_t - norm.cdf(d2) * K * math.e**(-r * t)
    return C


if __name__ == "__main__":
    interest_rate = float(api_call_interest_rate())
    print(api_all_tickers())

    t_m = 3 / 365
    # option_price = black_scholes(20, 18, interest_rate, t_m, 0.5)
    # print("---")
    # print(f"Black-Scholes Call Option Price: {option_price}")
