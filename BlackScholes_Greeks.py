import math
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm

# got the equations for black scholes model and greeks https://www.codearmo.com/python-tutorial/options-trading-black-scholes-model

class marketData: 
    def __init__(self): 
        # Stock variables
        self.data = None
        self.ticker = None
        self.start_date = None
        self.end_date = None

        # Option variables
        self.sigma = None
        self.T = None
        self.r = None
        self.S = None
        self.K = None
class marketData: 
    def __init__(self): 
        self.data = None
        self.ticker = None
        self.start_date = None
        self.end_date = None
        self.sigma = None
        self.T = None
        self.r = None
        self.S = None

    def grab_data(self, symbol, start_date, end_date):
        self.ticker = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()

        # Try to download the data
        self.data = yf.download(symbol, start=start_date, end=end_date)

        # Check if the data is empty
        if self.data.empty:
            print(f"No data found for symbol: {symbol} in the date range: {start_date} to {end_date}")
            raise ValueError(f"No data to process for symbol: {symbol}")

        # Calculate the volatility, 252 is the number of trading days in a year
        self.data['Returns'] = self.data['Adj Close'].pct_change()
        self.sigma = self.data['Returns'].std() * np.sqrt(252)

        # 3 month treasury yield as risk free rate
        treasury_yield_data = yf.download("^IRX", period="1d")
        three_month_yield = treasury_yield_data['Close'].iloc[-1] / 100
        self.r = three_month_yield

        # Calculate time to maturity in years
        self.T = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365

        # Spot price
        self.S = self.data['Adj Close'].iloc[-1]

        return (self.S, self.sigma, self.r, self.T, self.data)

class optionsGreeks: 
    def __init__(self, S, K, T, r, sigma):
        if S is None or K is None or T is None or r is None or sigma is None:
            print(f"Initialization failed: S={S}, K={K}, T={T}, r={r}, sigma={sigma}")
            raise ValueError("All parameters (S, K, T, r, sigma) must be provided and non-None.")
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def d1(self,S):
        return (math.log(S / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / (self.sigma * math.sqrt(abs(self.T)))
    
    def d2(self,S):
        return self.d1(S) - self.sigma * math.sqrt(abs(self.T))

    def call_price(self,S):
        d1 = self.d1(S)
        d2 = self.d2(S)

        return self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)

    def put_price(self,S):
        d1 = self.d1(S)
        d2 = self.d2(S)

        return self.S * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
    def call_delta(self):
        d1 = self.d1(s)
        return norm.cdf(d1)

    def put_delta(self):
        d1 = self.d1()
        return norm.cdf(d1) - 1

    def gamma(self):
        d1 = self.d1()
        return norm.pdf(d1) / (self.S * self.sigma * math.sqrt(self.T))

    def vega(self):
        d1 = self.d1()
        return self.S * norm.pdf(d1) * math.sqrt(self.T)

    def call_theta(self):
        d1 = self.d1()
        d2 = self.d2()
        theta = (-self.S * norm.pdf(d1) * self.sigma / (2 * math.sqrt(self.T)) - self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(d2))
        return theta / 252    # 252 is the number of trading days in a year
    
    def put_theta(self):
        d1 = self.d1()
        d2 = self.d2()
        theta = (-self.S * norm.pdf(d1) * self.sigma / (2 * math.sqrt(self.T)) + self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-d2))
        return theta / 252

    def call_rho(self):
        d2 = self.d2()
        return self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(d2)

    def put_rho(self):
        d2 = self.d2()
        return -self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(-d2)
    
    def all_greeks(self):
        return {
            'call_delta': self.call_delta(),
            'put_delta': self.put_delta(),
            'gamma': self.gamma(),
            'vega': self.vega(),
            'call_theta': self.call_theta(),
            'put_theta': self.put_theta(),
            'call_rho': self.call_rho(),
            'put_rho': self.put_rho()
        }
    

