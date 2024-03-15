import math
from scipy.stats import norm
import requests
from urllib.parse import quote


def api_call():
    """ API Call. """
    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    endpoint = "/v2/accounting/od/avg_interest_rates"
    params = {
        "fields": "avg_interest_rate_amt", # record_date
        "filter": "security_desc:eq:" + quote("Treasury Bills"),
        "sort": "-record_date",
        # "format": "json",
        # "pagesize": "1",
    }
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url, params=params)

    if response.status_code == 200:
        return response.json()
        # data = response.json()
        # return data["data"][0]
    else:
        return f"Error: {response.status_code}"

    # https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates

# def api_call_():


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
    print(api_call())

    # t_m = 3 / 365
    # option_price = black_scholes(20, 18, 0.04, t_m, 0.5)
    # print("---")
    # print(f"Black-Scholes Call Option Price: {option_price}")
