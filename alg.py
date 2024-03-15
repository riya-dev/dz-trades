import math
from scipy.stats import norm

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

    d1 = (math.log(S_t / K) + (t * (r + 0.5 * sigma**2))) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    C = norm.cdf(d1) * S_t - norm.cdf(d2) * K * math.e**(-r * t)
    return C


t_m = 3/365
b_s = black_scholes(20, 18, 0.04, t_m, 0.5)
print("black scholes call option price: ", b_s)
