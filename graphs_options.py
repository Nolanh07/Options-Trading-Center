from cmu_graphics import *
import math
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm


#where I learned how to use the getattr and raise value error
#https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python/24065533#24065533

# where I learned to fix the digits using .f
#https://stackoverflow.com/questions/45310254/fixed-digits-after-decimal-with-f-strings

#help with axis
#https://stackoverflow.com/questions/52077048/python-numpy-linspace-behaves-strangely-with-floats


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
        self.data = yf.download(symbol, start=start_date, end=end_date)
        
        self.data['Returns'] = self.data['Adj Close'].pct_change()
        self.sigma = self.data['Returns'].std() * np.sqrt(252)

        treasury_yield_data = yf.download("^IRX", period="1d")
        three_month_yield = treasury_yield_data['Close'].iloc[-1] / 100
        self.r = three_month_yield

        self.T = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
        self.S = self.data['Adj Close'].iloc[-1]

        return (self.S, self.sigma, self.r, self.T, self.data)

class optionsGreeks: 
    def __init__(self, S, K, T, r, sigma):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def d1(self, S):
        return (math.log(S / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / (self.sigma * math.sqrt(self.T))
    
    def d2(self, S):
        return self.d1(S) - self.sigma * math.sqrt(self.T)

    def call_price(self, S):
        d1 = self.d1(S)
        d2 = self.d2(S)
        return S * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)

    def put_price(self, S):
        d1 = self.d1(S)
        d2 = self.d2(S)
        return self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    def call_delta(self, S):
        d1 = self.d1(S)
        return norm.cdf(d1)

    def put_delta(self, S):
        d1 = self.d1(S)
        return norm.cdf(d1) - 1

    def gamma(self, S):
        d1 = self.d1(S)
        return norm.pdf(d1) / (S * self.sigma * math.sqrt(self.T))

    def vega(self, S):
        d1 = self.d1(S)
        return S * norm.pdf(d1) * math.sqrt(self.T)

    def call_theta(self, S):
        d1 = self.d1(S)
        d2 = self.d2(S)
        theta = (-S * norm.pdf(d1) * self.sigma / (2 * math.sqrt(self.T)) - self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(d2))
        return theta / 252
    
    def put_theta(self, S):
        d1 = self.d1(S)
        d2 = self.d2(S)
        theta = (-S * norm.pdf(d1) * self.sigma / (2 * math.sqrt(self.T)) + self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-d2))
        return theta / 252

    def call_rho(self, S):
        d2 = self.d2(S)
        return self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(d2)

    def put_rho(self, S):
        d2 = self.d2(S)
        return -self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(d2)

def onAppStart(app):
    app.width = 800
    app.height = 800
    app.num_points = 20
    app.selected_greek = 'put theta'  # intitial Greek, you can change this to other Greeks

    app.x_values = []
    app.y_values = []

    app.strike_price = 100

    # Initialize market data
    app.market_data = marketData()
    app.S, app.sigma, app.r, app.T, app.data = app.market_data.grab_data('GOOGL', '2021-01-01', '2024-01-01')

    # Initialize option greeks
    app.greeks = optionsGreeks(app.S, app.strike_price, app.T, app.r, app.sigma)

    # Store the values for plotting
    app.spot_prices = np.linspace(0.5 * app.S, 1.5 * app.S, app.num_points)
    app.x_values = 100 + (app.spot_prices - min(app.spot_prices)) * 600 / (max(app.spot_prices) - min(app.spot_prices))
    
    greek_function = getattr(app.greeks, app.selected_greek, None)  #  get the function for the selected Greek
    if greek_function is None:
        raise ValueError(f"Invalid Greek function: {app.selected_greek}")
    
    raw_y_values = [greek_function(sp) for sp in app.spot_prices]
    min_y, max_y = min(raw_y_values), max(raw_y_values)
    
    # Avoid division by zero in case all y-values are the same
    if min_y == max_y:
        scaled_y_values = [400] * app.num_points
    else:
        scaled_y_values = 400 - 300 * (np.array(raw_y_values) - min_y) / (max_y - min_y)
    
    app.y_values = scaled_y_values
    app.raw_y_values = raw_y_values  # Store raw_y_values for later use

    app.greek_value = None
    app.underlying_price = None
    app.selected_dot = False
    app.dot_not_selected = True
    
def redrawAll(app):
    drawLine(100, 100, 100, 700)  # y-axis
    drawLine(100, 400, 700, 400)  # x-axis
    
    if app.selected_dot:
        drawLabel(f'Underlying Price: {app.underlying_price:.2f}', 400, 50, size=16)
        drawLabel(f'{app.selected_greek}: {app.greek_value:.2f}', 400, 70, size=16)

    elif app.dot_not_selected:
        drawLabel(f'Click on a dot to see the value of {app.selected_greek}', 400, 50, size=16)
        
    greek_labels = {
        'call_price': 'Call Price',
        'put_price': 'Put Price',
        'call_delta': 'Call Delta',
        'put_delta': 'Put Delta',
        'gamma': 'Gamma',
        'vega': 'Vega',
        'call_theta': 'Call Theta',
        'put_theta': 'Put Theta',
        'call_rho': 'Call Rho',
        'put_rho': 'Put Rho'
    }
    
    selected_greek = app.__dict__.get("selected_greek")
    if selected_greek is None:
        selected_greek = 'call_price'  # Set a default Greek if None

    drawLabel(f'{greek_labels[selected_greek]}', 50, 50, size=16)
    drawLabel('Underlying Price', 710, 370, size=16)

    # Draw x axis labels (spot prices)
    for i in range(app.num_points):
        if i % 2 == 0:  # Only plot every other point
            x = int(app.x_values[i])
            label = f'{app.spot_prices[i]:.2f}'
            drawLabel(label, x, 710, size=10, align='center')
    
    # Draw y axis labels (Greek values)
    for i in range(app.num_points):
        if i % 2 == 0:  # Only plot every other point so the labels don't get too crowded
            y = int(app.y_values[i])
            label = f'{app.raw_y_values[i]:.6f}'  # Adjust precision for small values
            drawLabel(label, 70, y, size=10, align='right')

    # Draw the plot points and connecting lines
    for i in range(app.num_points):
        if i % 2 == 0:  # Only plot every other point
            x = int(app.x_values[i])
            y = int(app.y_values[i])
            drawCircle(x, y, 5, fill='red')
            if i > 1:
                prev_x = int(app.x_values[i-2])
                prev_y = int(app.y_values[i-2])
                drawLine(prev_x, prev_y, x, y)

def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def onMousePress(app, mouseX, mouseY):
    for i in range(app.num_points):
        if i % 2 == 0:  # Only check every other point
            cx = int(app.x_values[i])
            cy = int(app.y_values[i])
            if distance(mouseX, mouseY, cx, cy) <= 5:
                app.greek_value = app.raw_y_values[i] 
                app.underlying_price = app.spot_prices[i]
                app.selected_dot = True
                app.dot_not_selected = False
                break

def onMouseRelease(app, mouseX, mouseY):
    app.selected_dot = False
    app.dot_not_selected = True

runApp(width=800, height=800)
