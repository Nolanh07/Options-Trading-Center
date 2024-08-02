from cmu_graphics import *
from PIL import Image
import os, pathlib
import numpy as np
from BlackScholes_Greeks import *
from trading_strategies import *



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


        treasury_yield_data = yf.download("^IRX", period="1d")
        three_month_yield = treasury_yield_data['Close'].iloc[-1] / 100
        self.r = three_month_yield

        self.T = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
        self.sigma = float(self.data['Returns'].std() * np.sqrt(252))
        self.S = float(self.data['Adj Close'].iloc[-1])

        return (self.S, self.sigma, self.r, self.T, self.data)

class optionsGreeks: 

    def __init__(self, S, K, T, r, sigma):
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)

    def d1(self, S):
        S = float(S)
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


# Used 15-112 Thonny files for helping insert the images
def openImage(fileName):
    return Image.open(os.path.join(pathlib.Path(__file__).parent, fileName))






def onAppStart(app):
    #same for all screens
    app.width = 800
    app.height = 800
    app.buttonWidth = 350
    app.buttonHeight = 150
    app.cx = app.width // 2
    app.cy = app.height // 2
    app.buttonX = app.cx - app.buttonWidth // 2
    app.buttonY = app.cy - app.buttonHeight // 2
    app.todays_date = 'todays date' 

    # Different screens
    app.screen1 = True
    app.screen2 = False
    app.screen3 = False
    app.screen4 = False
    app.screen5 = False
    app.screen6 = False
    app.screen7 = False
    app.screen8 = False
    app.screen9 = False
    app.screen10 = False
    app.screen11 = False
    app.screen12 = False
    app.screen13 = False
    app.screen14 = False
    app.screen20 = False



    app.risk_tolerance_BCS = '0.1'  
    app.portfolio_size_BCS = '100000'  
    app.contract_quantity_BCS = '10' 
    app.selected_period_BCS = '30'  
    app.holding_period_days_BCS = '30' 
    app.sell_percentage_BCS = '0.25'  

    app.list_of_holdings_BCS = []  
    app.simulate_trades_BCS = False  

    app.company_to_add_5 = ''  
    app.company_to_remove_5 = '' 
    app.not_in_holdings_bool_5 = False 
    app.not_in_holdings_statement_5 = '' 
    app.adding_to_holdings_5 = False
    app.removing_from_holdings_5 = False
    app.error_occurred_BCS = False 
    app.error_message_BCS = ''  


    
    app.adding_to_holdings_6 = False
    app.removing_from_holdings_6 = False
    app.risk_tolerance_BPS = '0.1'  
    app.portfolio_size_BPS = '100000'  
    app.contract_quantity_BPS = '10' 
    app.selected_period_BPS = '30'  
    app.holding_period_days_BPS = '30' 
    app.sell_percentage_BPS = '0.25'  

    app.list_of_holdings_BPS = []  
    app.simulate_trades_BPS = False  

    app.company_to_add_6 = ''  
    app.company_to_remove_6 = '' 
    app.not_in_holdings_bool_6 = False 
    app.not_in_holdings_statement_6 = '' 

    app.error_occurred_BPS = False 
    app.error_message_BPS = '' 


    # input variables for options pricing tool
    app.strike_price = ''
    app.risk_free_rate = ''
    app.time_to_maturity = ''
    app.volatility = ''
    app.underlying_price = ''
    app.contract_type = ''
    app.active_input_price_model = None

    #input for underlying graph
    app.show_enter_statement = True
    app.show_restart_statement = False
    app.border_screen9_1 = 'black'
    app.border_screen9_2 = 'black'
    app.border_screen9_3 = 'black'
    app.underlying_symbol = ''
    app.start_date = ''
    app.end_date = ''

  


    #input for options graph menu
    app.display_greek = False
    app.call_price = False
    app.put_price = False
    app.call_delta = False
    app.put_delta = False
    app.gamma = False
    app.vega = False
    app.call_theta = False
    app.put_theta = False
    app.call_rho = False
    app.put_rho = False

    app.current_greek = None

    #input for options graph display: screen 11
    app.show_enter_statement_O = True
    app.show_restart_statement_O = False
    app.border_screen11_1 = 'black'
    app.border_screen11_2 = 'black'
    app.border_screen11_3 = 'black'
    app.type_stock_O = False
    app.type_start_date_O = False
    app.type_end_date_O = False
    # initialized parameters
    app.start_date_O = '2021-01-01'
    app.end_date_O = '2024-02-19'
    app.stock_O = 'AAPL'
    app.num_points_O = 20
    app.current_greek = 'call_theta'



    app.x_values = []
    app.y_values = []

    app.strike_price_O = '100'


    # variables for graphs of greeks and options

    # Initialize market data
    app.market_data = marketData()
    app.S, app.sigma, app.r, app.T, app.data = app.market_data.grab_data(app.stock_O, app.start_date_O, app.end_date_O)
    
    # Initialize option greeks
    app.greeks = optionsGreeks(app.S, app.strike_price_O, app.T, app.r, app.sigma)

    # Store the values for plotting
    app.spot_prices = np.linspace(0.5 * app.S, 1.5 * app.S, app.num_points_O)
    app.x_values = 100 + (app.spot_prices - min(app.spot_prices)) * 600 / (max(app.spot_prices) - min(app.spot_prices))
    
    

    
    
    
    app.greek_value = None
    app.underlying_price = ''
    app.selected_dot = False
    app.dot_not_selected = True




   #black scholes explanation screen
    app.latex_black_scholes = openImage('latex_black_scholes.png')
    app.imageWidth, app.imageHeight = app.latex_black_scholes.size
    app.latex_black_scholes = CMUImage(app.latex_black_scholes)
    app.how_options_work_1 = openImage('how_options_work_1.png')
    app.imageWidth1, app.imageHeight1 = app.how_options_work_1.size
    app.how_options_work_1 = CMUImage(app.how_options_work_1)
    app.how_options_work_2 = openImage('how_options_work_2.png')
    app.imageWidth2, app.imageHeight2 = app.how_options_work_2.size
    app.how_options_work_2 = CMUImage(app.how_options_work_2)


    #variables for long call strategy portfolio and trading window
    app.number_of_trades_LC = 0
    app.potfolio_returns_LC = []
    app.list_of_holdings_LC = []
    app.adding_to_holdings_1 = False
    app.removing_from_holdings_1 = False
    app.company_to_add_1= ''
    app.company_to_remove_1= ''
    app.not_in_holdings_bool_1 = False
    app.simulate_trades_LC = False
    app.not_in_holdings_statement_1 = ''
    app.portfolio_size_LC = '100000'  
    app.risk_tolerance_LC = '0.12'
    app.contract_quantity_LC = '100'
    app.selected_period_LC = '30'    
    app.holding_period_days_LC = '30'
    app.sell_percentage_LC = '0.25'
    app.active_input = None
    app.input_fields = ['portfolio_size', 'risk_tolerance', 'contract_quantity', 'selected_period', 'holding_period_days', 'sell_percentage']
    app.error_occurred_LC = False
    app.error_message_LC = " "
    app.error_occurred = False
    #variables for strategy y portfolio and trading window


#function for toggling and resetting screens


def updateGraphVariables(app):
    app.x_values = []
    app.y_values = []

    app.strike_price_O = '100'


    # variables for graphs of greeks and options

    # Initialize market data
    app.market_data = marketData()
    app.S, app.sigma, app.r, app.T, app.data = app.market_data.grab_data(app.stock_O, app.start_date_O, app.end_date_O)
    
    # Initialize option greeks
    app.greeks = optionsGreeks(app.S, app.strike_price_O, app.T, app.r, app.sigma)
    #where I learned to use the np.linspace cited at the top of the file
    # Store the values for plotting
    app.spot_prices = np.linspace(0.5 * app.S, 1.5 * app.S, app.num_points_O)
    app.x_values = 100 + (app.spot_prices - min(app.spot_prices)) * 600 / (max(app.spot_prices) - min(app.spot_prices))
    # where I learned to do this cited at the top of the file
    greek_function = getattr(app.greeks, app.current_greek, None)
    if greek_function is None:
        raise ValueError(f"Invalid Greek function: {app.current_greek}")

    # Calculate raw y-values using the Greek function
    app.y_values = [greek_function(sp) for sp in app.spot_prices]

    # Map raw y-values to the canvas space (invert y-axis for correct graph orientation)
    canvas_min_y, canvas_max_y = 700, 100  # Inverted y-axis: lower values are higher on the screen

    # Find the minimum and maximum of y_values
    min_y = min(app.y_values)
    max_y = max(app.y_values)

    # Normalize and scale y-values to fit within the canvas range
    if max_y != min_y:
        app.y_values = [
            canvas_max_y + (y - min_y) * (canvas_min_y - canvas_max_y) / (max_y - min_y)
            for y in app.y_values
        ]
    else:
        app.y_values = [(canvas_min_y + canvas_max_y) / 2] * len(app.y_values)
def setScreen(app, screenNumber):
    app.screen1 = (screenNumber == 1)
    app.screen2 = (screenNumber == 2)
    app.screen3 = (screenNumber == 3)
    app.screen4 = (screenNumber == 4)
    app.screen5 = (screenNumber == 5)
    app.screen6 = (screenNumber == 6)
    app.screen7 = (screenNumber == 7)
    app.screen8 = (screenNumber == 8)
    app.screen9 = (screenNumber == 9)
    app.screen10 = (screenNumber == 10)
    app.screen11 = (screenNumber == 11)
    app.screen12 = (screenNumber == 12)
    app.screen13 = (screenNumber == 13)
    app.screen14 = (screenNumber == 14)
    
    app.screen20 = (screenNumber == 20)

def redrawAll(app):
    # Screen 1: Home Screen ###################################################################################################################
    if app.screen1:
        drawLabel('Research Tools', app.cx, app.cy, size=16)
        drawRect(app.buttonX, app.buttonY, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawLabel('Simulate Trades', app.cx, app.cy - 200, size=16)
        drawRect(app.buttonX, app.buttonY - 200, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawLabel('What are Options?', app.cx, app.cy +200, size=16)
        drawRect(app.buttonX, app.buttonY +200, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)


        drawLabel('Options Trading Center', app.cx, app.cy - 350, size=30)

    # Screen 2: Research Tools || Previous Screen = Screen 1 ###################################################################################################################
    elif app.screen2:
        drawLabel('Research Tools', app.cx, app.cy - 350, size=30)

        drawLabel('Graphs', app.cx, app.cy, size=16)
        drawRect(app.buttonX, app.buttonY, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawLabel('Pricing Tool', app.cx, app.cy - 200, size=16)
        drawRect(app.buttonX, app.buttonY - 200, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawLabel('How Pricing with Black Scholes Works', app.cx, app.cy+200, size=16)
        drawRect(app.buttonX, app.buttonY+200, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)


        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

    # Screen 3: My Portfolios || Previous Screen = Screen 1 ###################################################################################################################
    elif app.screen3: 
        drawLabel('Trading Strategies', app.cx, app.cy - 350, size=30)

        rectWidth = 150
        rectHeight = 50


        x1 = app.cx - rectWidth // 2 - 250  
        x2 = app.cx - rectWidth // 2        
        x3 = app.cx - rectWidth // 2 + 250  


        drawRect(x1, app.cy, rectWidth, rectHeight, fill=None, border="black", borderWidth=2)
        drawLabel('Long Call Strategy', app.cx - 250, app.cy+20, size=16)


        drawRect(x2, app.cy, rectWidth, rectHeight, fill=None, border="black", borderWidth=2)
        drawLabel('Bull Call Strategy', app.cx, app.cy+20, size=16)


        drawRect(x3, app.cy, rectWidth, rectHeight, fill=None, border="black", borderWidth=2)
        drawLabel('Bear Put Strategy', app.cx + 250, app.cy+20, size=16)



        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)


    # Screen 4: Long Call Strategy Portfolio || Previous Screen = Screen 3  ###################################################################################################################
    if app.screen4:
        risk_tolerance = float(app.risk_tolerance_LC)
        portfolio_size = int(app.portfolio_size_LC)
        contract_quantity = int(app.contract_quantity_LC)
        selected_period = int(app.selected_period_LC)
        holding_period_days = int(app.holding_period_days_LC)
        sell_percentage = float(app.sell_percentage_LC)

        # Simulate trades if the flag is set
        if app.simulate_trades_LC:
            transactions, symbols, selected_period, start_date, end_date, holdings, total_profits = longCall.run_long_call_strategy(
                app.list_of_holdings_LC, portfolio_size, risk_tolerance, contract_quantity, selected_period, holding_period_days, sell_percentage
            )

            # Display each transaction
            y_start_val = app.height - 220  # Start near the bottom

            # Display summary results in the bottom-right corner
            padding_x = 20
            x_position = app.width - padding_x

            drawLabel(f"Total Transactions: {transactions}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"Results for {symbols}:", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"symbol: {symbols}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"period: {selected_period}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"start_date: {start_date}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"end_date: {end_date}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"holdings: {holdings}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20
            drawLabel(f"total profits: {total_profits:.2f}", x_position, y_start_val, size=14, align='right')
            y_start_val -= 20

        # Define the input labels and fields for the parameters
        labels = ['Portfolio Size', 'Risk Tolerance', 'Contract Quantity', 'Selected Period', 'Holding Period Days', 'Sell Percentage']
        values = [app.portfolio_size_LC, app.risk_tolerance_LC, app.contract_quantity_LC, app.selected_period_LC, app.holding_period_days_LC, app.sell_percentage_LC]
        input_fields = ['portfolio_size', 'risk_tolerance', 'contract_quantity', 'selected_period', 'holding_period_days', 'sell_percentage']

        for i in range(len(labels)):
            drawLabel(f'{labels[i]}:', app.cx + 200, 100 + 50 * i, size=12)
            drawRect(app.cx + 100, 140 + 50 * i - 30, 200, 30, fill=None, border="black", borderWidth=2)
            drawLabel(f'{values[i]}', app.cx + 200, 125 + 50 * i, size=16)

        # Display the portfolio holdings
        drawLabel('Companies in Portfolio', 200, 275, size=16, bold=True)
        currentHoldings = app.list_of_holdings_LC
        drawRect(100, 300, 200, 300, fill=None, border="black", borderWidth=2)
        for i in range(len(currentHoldings)):
            drawLabel(f'{currentHoldings[i]}', 200, 315 + 25 * i, size=14)
            drawLine(100, 325 + 25 * i, 300, 325 + 25 * i, fill='black')

        # Display input boxes and labels for adding/removing companies
        drawRect(125, 100, 150, 50, fill=None, border='black', borderWidth=2)
        drawLabel('To add to holdings, type company ticker and press enter:', 200, 85, size=12)
        drawLabel(f'{app.company_to_add_1}', 200, 125, size=14)

        drawRect(125, 200, 150, 50, fill=None, border='black', borderWidth=2)
        drawLabel('To remove from holdings, type company ticker and press enter:', 200, 185, size=12)
        drawLabel(f'{app.company_to_remove_1}', 200, 225, size=14)

        if app.not_in_holdings_bool_1:
            line = app.not_in_holdings_statement_1.split(', ')
            drawLabel(line[0] + ',', 200, 220, size=10, fill='red')
            drawLabel(line[1], 200, 240, size=10, fill='red')

        # Display the back button
        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

        if not app.simulate_trades_LC:
            drawLabel('run simulation', 600, 445, size=16)
            drawRect(525, 420, 150, 50, fill=None, border='black', borderWidth=2)
            
            drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
            drawLabel('Back', 55, 35, size=16)

        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)


            

    # Screen 5: Strategy y|| Previous Screen = Screen 3 ###################################################################################################################

    if app.screen5:
        # Convert app variables to the appropriate types
        risk_tolerance = float(app.risk_tolerance_BCS)
        portfolio_size = int(app.portfolio_size_BCS)
        contract_quantity = int(app.contract_quantity_BCS)
        selected_period = int(app.selected_period_BCS)
        holding_period_days = int(app.holding_period_days_BCS)
        sell_percentage = float(app.sell_percentage_BCS)

        # Simulate trades if the flag is set
        if app.simulate_trades_BCS:
            # Using the updated run_bull_call_spread_strategy method
            transactions, symbols, period, start_date, end_date, holdings, total_profits, current_portfolio_value = bullCallSpread.run_bull_call_spread_strategy(
                app.list_of_holdings_BCS, portfolio_size, risk_tolerance, contract_quantity, selected_period, holding_period_days, sell_percentage
            )


            y_start_val = app.height - 220  # Start near the bottom

            # Display summary results in the bottom-right corner
            padding_x = 20
            x_position = app.width - padding_x
            # Display summary results
            drawLabel(f"Results for {symbols}:", app.cx+150, y_start_val , size=14)
            drawLabel(f"symbol: {symbols}", app.cx+150, y_start_val + 20, size=14)
            drawLabel(f"period: {period}", app.cx+150, y_start_val + 40, size=14)
            drawLabel(f"start_date: {start_date}", app.cx+150, y_start_val + 60, size=14)
            drawLabel(f"end_date: {end_date}", app.cx+150, y_start_val + 80, size=14)
            drawLabel(f"transactions: {transactions}", app.cx+150, y_start_val + 100, size=14)
            drawLabel(f"holdings: {holdings}", app.cx+150, y_start_val + 120, size=14, align='center')
            drawLabel(f"total profits: {total_profits:.2f}", app.cx+150, y_start_val + 140, size=14)
            drawLabel(f"current portfolio value: {current_portfolio_value:.2f}", app.cx+150, y_start_val + 160, size=14)

        # Handle errors if they occur (optional)
        if app.error_occurred:
            drawLabel(app.error_message_BCS, app.cx, app.cy - 300, size=16, fill='red')

        # Define the input labels and fields for the parameters
        labels = ['Portfolio Size', 'Risk Tolerance', 'Contract Quantity', 'Selected Period', 'Holding Period Days', 'Sell Percentage']
        values = [app.portfolio_size_BCS, app.risk_tolerance_BCS, app.contract_quantity_BCS, app.selected_period_BCS, app.holding_period_days_BCS, app.sell_percentage_BCS]
        input_fields = ['portfolio_size', 'risk_tolerance', 'contract_quantity', 'selected_period', 'holding_period_days', 'sell_percentage']
        
        for i in range(len(labels)):
            drawLabel(f'{labels[i]}:', app.cx + 200, 100 + 50 * i, size=12)
            drawRect(app.cx + 100, 140 + 50 * i - 30, 200, 30, fill=None, border="black", borderWidth=2)
            drawLabel(f'{values[i]}', app.cx + 200, 125 + 50 * i, size=16)

        # Display the portfolio holdings
        drawLabel('Companies in Portfolio', 200, 275, size=16, bold=True)
        currentHoldings = app.list_of_holdings_BCS
        drawRect(100, 300, 200, 300, fill=None, border="black", borderWidth=2)
        for i in range(len(currentHoldings)):
            drawLabel(f'{currentHoldings[i]}', 200, 315 + 25 * i, size=14)
            drawLine(100, 325 + 25 * i, 300, 325 + 25 * i, fill='black')

        # Display input boxes and labels for adding/removing companies
        drawRect(125, 100, 150, 50, fill=None, border='black', borderWidth=2)
        drawLabel('To add to holdings, type company ticker and press enter:', 200, 85, size=12)
        drawLabel(f'{app.company_to_add_5}', 200, 125, size=14)

        drawRect(125, 200, 150, 50, fill=None, border='black', borderWidth=2)
        drawLabel('To remove from holdings, type company ticker and press enter:', 200, 185, size=12)
        drawLabel(f'{app.company_to_remove_5}', 200, 225, size=14)

        if app.not_in_holdings_bool_5:
            line = app.not_in_holdings_statement_5.split(', ')
            drawLabel(line[0] + ',', 200, 220, size=10, fill='red')
            drawLabel(line[1], 200, 240, size=10, fill='red')

        # Display the back button
        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

        if not app.simulate_trades_BCS:
            drawLabel('run simulation', 600,445, size=16)
            drawRect(525, 420, 150, 50, fill=None, border='black', borderWidth=2)
            
            drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
            drawLabel('Back', 55, 35, size=16)

    
    # Screen 6: Strategy z|| Previous Screen = Screen 3 ###################################################################################################################

    if app.screen6:
            risk_tolerance = float(app.risk_tolerance_BPS)
            portfolio_size = int(app.portfolio_size_BPS)
            contract_quantity = int(app.contract_quantity_BPS)
            selected_period = int(app.selected_period_BPS)
            holding_period_days = int(app.holding_period_days_BPS)
            sell_percentage = float(app.sell_percentage_BPS)

            # Simulate trades if the flag is set
            if app.simulate_trades_BPS:
                transactions, symbols, selected_period, start_date, end_date, holdings, total_profits = bearPutSpread.run_bear_put_spread_strategy(
                app.list_of_holdings_BPS, portfolio_size, risk_tolerance, contract_quantity, selected_period, holding_period_days, sell_percentage
                )

                # Display each transaction
                y_start_val = app.height - 220  # Start near the bottom

                # Display summary results in the bottom-right corner
                padding_x = 20
                x_position = app.width - padding_x

                drawLabel(f"Total Transactions: {transactions}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"Results for {symbols}:", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"symbol: {symbols}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"period: {selected_period}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"start_date: {start_date}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"end_date: {end_date}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"holdings: {holdings}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20
                drawLabel(f"total profits: {total_profits:.2f}", x_position, y_start_val, size=14, align='right')
                y_start_val -= 20

              
            # Define the input labels and fields for the parameters
            labels = ['Portfolio Size', 'Risk Tolerance', 'Contract Quantity', 'Selected Period', 'Holding Period Days', 'Sell Percentage']
            values = [app.portfolio_size_BPS, app.risk_tolerance_BPS, app.contract_quantity_BPS, app.selected_period_BPS, app.holding_period_days_BPS, app.sell_percentage_BPS]
            input_fields = ['portfolio_size', 'risk_tolerance', 'contract_quantity', 'selected_period', 'holding_period_days', 'sell_percentage']
            
            for i in range(len(labels)):
                drawLabel(f'{labels[i]}:', app.cx + 200, 100 + 50 * i, size=12)
                drawRect(app.cx + 100, 140 + 50 * i - 30, 200, 30, fill=None, border="black", borderWidth=2)
                drawLabel(f'{values[i]}', app.cx + 200, 125 + 50 * i, size=16)

            # Display the portfolio holdings
            drawLabel('Companies in Portfolio', 200, 275, size=16, bold=True)
            currentHoldings = app.list_of_holdings_BPS
            drawRect(100, 300, 200, 300, fill=None, border="black", borderWidth=2)
            for i in range(len(currentHoldings)):
                drawLabel(f'{currentHoldings[i]}', 200, 315 + 25 * i, size=14)
                drawLine(100, 325 + 25 * i, 300, 325 + 25 * i, fill='black')

            # Display input boxes and labels for adding/removing companies
            drawRect(125, 100, 150, 50, fill=None, border='black', borderWidth=2)
            drawLabel('To add to holdings, type company ticker and press enter:', 200, 85, size=12)
            drawLabel(f'{app.company_to_add_6}', 200, 125, size=14)

            drawRect(125, 200, 150, 50, fill=None, border='black', borderWidth=2)
            drawLabel('To remove from holdings, type company ticker and press enter:', 200, 185, size=12)
            drawLabel(f'{app.company_to_remove_6}', 200, 225, size=14)

            if app.not_in_holdings_bool_6:
                line = app.not_in_holdings_statement_6.split(', ')
                drawLabel(line[0] + ',', 200, 220, size=10, fill='red')
                drawLabel(line[1], 200, 240, size=10, fill='red')

            # Display the back button
            drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
            drawLabel('Back', 55, 35, size=16)

            if not app.simulate_trades_BPS:
                drawLabel('run simulation', 600,445, size=16)
                drawRect(525, 420, 150, 50, fill=None, border='black', borderWidth=2)
                
                drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
                drawLabel('Back', 55, 35, size=16)

            drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
            drawLabel('Back', 55, 35, size=16)

    # Screen 7: Graphs || Previous Screen = Screen 2 ###################################################################################################################
    if app.screen7:
        drawLabel('Graphs', app.cx, app.cy - 350, size=30)

        # drawLabel('Underlying', app.cx, app.cy, size=16)
        # drawRect(app.buttonX, app.buttonY, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawLabel('Greeks', app.cx, app.cy - 200, size=16)
        drawRect(app.buttonX, app.buttonY - 200, app.buttonWidth, app.buttonHeight, fill=None, border="black", borderWidth=2)

        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

    # Screen 8: Pricing Tool || Previous Screen = Screen 2 ###################################################################################################################

    if app.screen8:
        drawLabel('Pricing Tool', app.cx, app.cy - 350, size=30)

        labels = ['Strike Price', 'Risk Free Rate', 'Time to Maturity', 'Volatility', 'Underlying Price', 'Contract Type (enter call or put)']
        values = [app.strike_price, app.risk_free_rate, app.time_to_maturity, app.volatility, app.underlying_price, app.contract_type]

        for i in range(6):
            drawLabel(f'Enter {labels[i]}:', app.cx - 200, app.cy - 200 + 70 * i, size=16)
            drawRect(app.cx + 100, app.cy - 220 + 70 * i, 200, 30, fill=None, border="black", borderWidth=2)
            drawLabel(values[i], app.cx + 200, app.cy - 205 + 70 * i, size=16)

        drawRect(app.cx + 100, app.cy + 300, 200, 30, fill=None, border="black", borderWidth=2)
        drawLabel(f'Value of {app.contract_type} option', app.cx-200, app.cy + 320, size=16)

        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

    # Screen 9: Underlying Asset Graph || Previous Screen = Screen 7 ###################################################################################################################
    # if app.screen9:

    #     if app.show_enter_statement:
    #         drawLabel('Underlying Graph', app.cx, app.cy - 350, size=30)

    #         # Box 1 for stock ticker
    #         drawRect(150, 140, 100, 40, fill=None, border=app.border_screen9_1, borderWidth=2)
    #         drawLabel('Click box to enter stock ticker ', 200, 120, size=12)
    #         drawLabel(app.underlying_symbol, 200, 160, size=16)

    #         # Box 2 for start date
    #         drawRect(350, 140, 100, 40, fill=None, border=app.border_screen9_2, borderWidth=2)
    #         drawLabel('Click box to enter start date ', 400, 100, size=12)
    #         drawLabel('Format: YYYY-MM-DD', 400, 120, size=12)
    #         drawLabel(app.start_date, 400, 160, size=16)

    #         # Box 3 for end date
    #         drawRect(550, 140, 100, 40, fill=None, border=app.border_screen9_3, borderWidth=2)
    #         drawLabel('Click box to enter end date ', 600, 100, size=12)
    #         drawLabel('Format: YYYY-MM-DD', 600, 120, size=12)
    #         drawLabel(app.end_date, 600, 160, size=16)

    #     elif app.show_restart_statement:
    #         drawLabel('Underlying Graph', app.cx, app.cy - 350, size=30)
    #         drawLabel('Press r to restart', app.cx, app.cy - 300, size=14)

          
                
    #     drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
    #     drawLabel('Back', 55, 35, size=16)

    #Screen 10: Graph Options Menu || Previous Screen = Screen 7 ###################################################################################################################
    if app.screen10:
        drawLabel('Graph Options', app.cx, app.cy - 350, size=30)

        labels = ['Call Price', 'Put Price', 'Call Delta', 'Put Delta', 'Gamma', 'Vega', 'Call Theta', 'Put Theta', 'Call Rho', 'Put Rho']
        values = [app.call_price, app.put_price, app.call_delta, app.put_delta, app.gamma, app.vega, app.call_theta, app.put_theta, app.call_rho, app.put_rho]

        for i in range(10): 
            row = i // 2
            col = i % 2
            x_offset = 400 * col
            y_start_val = 100 * row
            
            drawLabel(f'{labels[i]}', app.cx - 200 + x_offset, app.cy - 250 + y_start_val, size=16)
            drawRect(app.cx - 300 + x_offset, app.cy - 265 + y_start_val , 200, 30, fill=None, border="black", borderWidth=2)
        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

    #Screen 11: Display Graph Options || Previous Screen = Screen 10 ###################################################################################################################

    if app.screen11:
        if app.show_enter_statement_O:
            drawLabel('press enter after typing in each box, once all boxes are green you will see graph', app.cx, app.cy , size=12)
            # Box 1 for stock ticker
            drawRect(150, 140, 100, 40, fill=None, border=app.border_screen11_1, borderWidth=2)
            drawLabel('Click box to enter stock ticker ', 200, 120, size=12)
            drawLabel(app.stock_O, 200, 160, size=16)

            # Box 2 for start date
            drawRect(350, 140, 100, 40, fill=None, border=app.border_screen11_2, borderWidth=2)
            drawLabel('Click box to enter start date ', 400, 100, size=12)
            drawLabel('Format: YYYY-MM-DD', 400, 120, size=12)
            drawLabel(app.start_date_O, 400, 160, size=16)

            # Box 3 for end date
            drawRect(550, 140, 100, 40, fill=None, border=app.border_screen11_3, borderWidth=2)
            drawLabel('Click box to enter end date ', 600, 100, size=12)
            drawLabel('Format: YYYY-MM-DD', 600, 120, size=12)
            drawLabel(app.end_date_O, 600, 160, size=16)

        elif app.show_restart_statement_O:
            drawLabel(f'{app.current_greek} graph', app.cx, app.cy - 350, size=30)
            drawLabel('Press g to see graph', app.cx, app.cy - 300, size=14)

        

        
        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

        
    
   

    #Screen 13: How Pricing with Black Scholes Works || Previous Screen = Screen 2 ###################################################################################################################
    if app.screen13:
        
        newWidth, newHeight = (app.imageWidth/1.5, app.imageHeight/1.5)
        drawImage(app.latex_black_scholes, 50,90 , width=newWidth, height=newHeight)

        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)

    
    if app.screen20:


        newWidth, newHeight = (app.imageWidth1/2.75, app.imageHeight1/2.5)
        drawImage(app.how_options_work_1, 25,90 , width=newWidth, height=newHeight)

        newWidth1, newHeight1 = (app.imageWidth2/2.75, app.imageHeight2/2.5)
        drawImage(app.how_options_work_2, 425,90 , width=newWidth1, height=newHeight1)

        drawRect(20, 20, 70, 30, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 35, size=16)
        
    if app.screen14:
        drawLine(100, 100, 100, 700)  # y-axis
        drawLine(100, 400, 700, 400)  # x-axis
        
        if app.selected_dot:
            drawLabel(f'Underlying Price: {app.underlying_price:.2f}', 400, 50, size=16)
            drawLabel(f'{app.current_greek}: {app.greek_value:.2f}', 400, 70, size=16)

        elif app.dot_not_selected:
            drawLabel(f'Click on a dot to see the value of {app.current_greek}', 400, 50, size=16)
            
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
        


        
        drawLabel(f'{app.current_greek} value', 70, 50, size=16)
        drawLabel('Underlying Price', 710, 370, size=16)

        # Draw x axis labels (spot prices)
        for i in range(app.num_points_O):
            if i % 2 == 0:  # Only plot every other point
                x = int(app.x_values[i])
                label = f'{app.spot_prices[i]:.2f}'
                drawLabel(label, x, 710, size=10, align='center')
        
        # Draw y axis labels (Greek value# s)
        print(app.y_values)
        print(app.num_points_O)
        for i in range(app.num_points_O):
            if i % 2 == 0:  # Only plot every other point so the labels don't get too crowded
                y = int(app.y_values[i])
                for y in app.y_values:
                
                    label = f'{app.y_values[i]:.6f}'  # Adjust precision for small values
                    drawLabel(label, 70, float(y), size=10, align='right')
        if not (0 <= y <= app.height):
                print(f"Out of bounds y value: {y}")
        # Draw the plot points and connecting lines
        for i in range(app.num_points_O):
            if i % 2 == 0:  # Only plot every other point
                x = int(app.x_values[i])
                y = int(app.y_values[i])
                drawCircle(x, y, 5, fill='red')
                if i > 1:
                    prev_x = int(app.x_values[i-2])
                    prev_y = int(app.y_values[i-2])
                    drawLine(prev_x, prev_y, x, y)

        
        drawRect(20, 10, 70, 20, fill=None, border="black", borderWidth=2)
        drawLabel('Back', 55, 20, size=12)
        
def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5



def onMousePress(app, mouseX, mouseY):

    
    # Screen 1: Home Screen toggles
    if app.screen1:
        if app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY <= mouseY <= app.buttonY + app.buttonHeight:
            setScreen(app, 2)
        elif app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY - 200 <= mouseY <= app.buttonY - 200 + app.buttonHeight:
            setScreen(app, 3)

        elif app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY + 200 <= mouseY <= app.buttonY + 200 + app.buttonHeight:
            setScreen(app, 20)

    # Screen 2: Research Tools toggles
    elif app.screen2:
        if app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY <= mouseY <= app.buttonY + app.buttonHeight:
            setScreen(app, 7)
        elif app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY - 200 <= mouseY <= app.buttonY - 200 + app.buttonHeight:
            setScreen(app, 8)
        elif app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY + 200 <= mouseY <= app.buttonY + 200 + app.buttonHeight:
            setScreen(app, 13)
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 1)

    # Screen 3: Portfolio menu toggles
    elif app.screen3:
        if 75 <= mouseX <= 225 and 400 <= mouseY <= 450:
            setScreen(app, 4)
        elif 325 <= mouseX <= 475 and 400 <= mouseY <= 450:
            setScreen(app, 5)
        elif 575 <= mouseX <= 725 and 400 <= mouseY <= 450:
            setScreen(app, 6)
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 1)

    # Screen 7: Graph menu toggles
    elif app.screen7:
        if app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY <= mouseY <= app.buttonY + app.buttonHeight:
            setScreen(app, 9)
        elif app.buttonX <= mouseX <= app.buttonX + app.buttonWidth and app.buttonY - 200 <= mouseY <= app.buttonY - 200 + app.buttonHeight:
            setScreen(app, 10)
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 2)

    # Screen 8 Pricing Tool button toggles
    elif app.screen8:
        if app.cx + 100 <= mouseX <= app.cx + 300 and app.cy - 220 <= mouseY <= app.cy - 190:
            app.active_input_price_model = 'strike_price'
        elif app.cx + 100 <= mouseX <= app.cx + 300 and app.cy - 150 <= mouseY <= app.cy - 120:
            app.active_input_price_model = 'risk_free_rate'
        elif app.cx + 100 <= mouseX <= app.cx + 300 and app.cy - 80 <= mouseY <= app.cy - 50:
            app.active_input_price_model = 'time_to_maturity'
        elif app.cx + 100 <= mouseX <= app.cx + 300 and app.cy - 10 <= mouseY <= app.cy + 20:
            app.active_input_price_model = 'volatility'
        elif app.cx + 100 <= mouseX <= app.cx + 300 and app.cy + 60 <= mouseY <= app.cy + 90:
            app.active_input_price_model = 'underlying_price'
        elif app.cx + 100 <= mouseX <= app.cx + 300 and app.cy + 130 <= mouseY <= app.cy + 160:
            app.active_input_price_model = 'contract_type'
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 2)

    # Screen 9: underlying graph toggles
    # elif app.screen9:
    #     if 150 <= mouseX <= 250 and 140 <= mouseY <= 180:
    #         app.type_stock = True
    #         app.type_start_date = False
    #         app.type_end_date = False
    #     elif 350 <= mouseX <= 450 and 140 <= mouseY <= 180:
    #         app.type_stock = False
    #         app.type_start_date = True
    #         app.type_end_date = False
    #     elif 550 <= mouseX <= 650 and 140 <= mouseY <= 180:
    #         app.type_stock = False
    #         app.type_start_date = False
    #         app.type_end_date = True
    #     if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
    #         setScreen(app, 7)

    # Screen 10: options graph menu toggles
    elif app.screen10:
        if 100 <= mouseX <= 300 and 135 <= mouseY <= 165:
            app.call_price = True
            app.current_greek = 'Call Price'
            setScreen(app, 11)
        elif 500 <= mouseX <= 700 and 135 <= mouseY <= 165:
            app.put_price = True
            app.current_greek = 'Put Price'
            setScreen(app, 11)
        elif 100 <= mouseX <= 300 and 235 <= mouseY <= 265:
            app.call_delta = True
            app.current_greek = 'Call Delta'
            setScreen(app, 11)
        elif 500 <= mouseX <= 700 and 235 <= mouseY <= 265:
            app.put_delta = True
            app.current_greek = 'Put Delta'
            setScreen(app, 11)
        elif 100 <= mouseX <= 300 and 335 <= mouseY <= 365:
            app.gamma = True
            app.current_greek = 'Gamma'
            setScreen(app, 11)
        elif 500 <= mouseX <= 700 and 335 <= mouseY <= 365:
            app.vega = True
            app.current_greek = 'Vega'
            setScreen(app, 11)
        elif 100 <= mouseX <= 300 and 435 <= mouseY <= 465:
            app.call_theta = True
            app.current_greek = 'Call Theta'
            setScreen(app, 11)
        elif 500 <= mouseX <= 700 and 435 <= mouseY <= 465:
            app.put_theta = True
            app.current_greek = 'Put Theta'
            setScreen(app, 11)
        elif 100 <= mouseX <= 300 and 535 <= mouseY <= 565:
            app.call_rho = True
            app.current_greek = 'Call Rho'
            setScreen(app, 11)
        elif 500 <= mouseX <= 700 and 535 <= mouseY <= 565:
            app.put_rho = True
            app.current_greek = 'Put Rho'
            setScreen(app, 11)
        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 7)



    if app.screen20:


        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 1)

    # Screen 11: Display Graph Options toggles
    elif app.screen11:



            

        if 150 <= mouseX <= 250 and 140 <= mouseY <= 180:
            app.type_stock_O = True
            app.type_start_date_O = False
            app.type_end_date_O = False
        elif 350 <= mouseX <= 450 and 140 <= mouseY <= 180:
            app.type_stock_O = False
            app.type_start_date_O = True
            app.type_end_date_O = False
        elif 550 <= mouseX <= 650 and 140 <= mouseY <= 180:
            app.type_stock_O = False
            app.type_start_date_O = False
            app.type_end_date_O = True

        if app.call_price:
            app.current_greek = 'call_price'
        elif app.put_price:
            app.current_greek = 'put_price'
        elif app.call_delta:
            app.current_greek = 'call_delta'
        elif app.put_delta:
            app.current_greek = 'put_delta'
        elif app.gamma:
            app.current_greek = 'gamma'
        elif app.vega:
            app.current_greek = 'vega'
        elif app.call_theta:
            app.current_greek = 'call_theta'
        elif app.put_theta:
            app.current_greek = 'put_theta'
        elif app.call_rho:
            app.current_greek = 'call_rho'
        elif app.put_rho:
            app.current_greek = 'put_rho'

        updateGraphVariables(app)

        

        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 10)

    # Screen 13: How Pricing with Black Scholes Works toggles
    if app.screen13:
        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 2)


    if app.screen14:
        for i in range(app.num_points_O):
            if i % 2 == 0:  # Only check every other point
                cx = int(app.x_values[i])
                cy = int(app.y_values[i])
                if distance(mouseX, mouseY, cx, cy) <= 5:
                    app.greek_value = app.y_values[i]  # Correctly use raw_y_values for display
                    app.underlying_price = app.spot_prices[i]
                    app.selected_dot = True
                    app.dot_not_selected = False
                    break

        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 11)



    ############################################################################################################################################################################
    ############################################################################################################################################################################
    # Individual portfolio toggles
    ############################################################################################################################################################################
    # Screen 4: Long Call Strategy Portfolio

    if app.screen4:
        
        # Add to holdings
        if 125 <= mouseX <= 275 and 100 <= mouseY <= 150:
            app.adding_to_holdings_1 = True
            app.removing_from_holdings_1 = False

        # Remove from holdings
        elif 125 <= mouseX <= 275 and 200 <= mouseY <= 250:
            app.adding_to_holdings_1 = False
            app.removing_from_holdings_1 = True

        # Back button
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 3)

        if 500 <= mouseX <= 650 and 110 <= mouseY <= 140:
            app.active_input = 'portfolio_size'

        elif 500 <= mouseX <= 650 and 160 <= mouseY <= 190:
            app.active_input = 'risk_tolerance'

        elif 500 <= mouseX <= 650 and 210 <= mouseY <= 240:
            app.active_input = 'contract_quantity'
        elif 500 <= mouseX <= 650 and 260 <= mouseY <= 290:
            app.active_input = 'selected_period'
        elif 500 <= mouseX <= 650 and 310 <= mouseY <= 340:
            app.active_input = 'holding_period_days'
        elif 500 <= mouseX <= 650 and 360 <= mouseY <= 390:
            app.active_input = 'sell_percentage'


        if 525 <= mouseX <= 625 and 420 <= mouseY <= 470:
           

                app.simulate_trades_LC = True
                # Run the strategy
                portfolio = longCall.run_long_call_strategy(app.list_of_holdings_LC, int(app.portfolio_size_LC), float(app.risk_tolerance_LC), int(app.contract_quantity_LC), int(app.selected_period_LC), int(app.holding_period_days_LC), float(app.sell_percentage_LC))

           

    # Screen 5: bull call Strategy Portfolio
    elif app.screen5:
          
        # Add to holdings
        if 125 <= mouseX <= 275 and 100 <= mouseY <= 150:
            app.adding_to_holdings_5 = True
            app.removing_from_holdings_5 = False

        # Remove from holdings
        elif 125 <= mouseX <= 275 and 200 <= mouseY <= 250:
            app.adding_to_holdings_5 = False
            app.removing_from_holdings_5 = True

        # Back button
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 3)

        if 500 <= mouseX <= 650 and 110 <= mouseY <= 140:
            app.active_input = 'portfolio_size'

        elif 500 <= mouseX <= 650 and 160 <= mouseY <= 190:
            app.active_input = 'risk_tolerance'

        elif 500 <= mouseX <= 650 and 210 <= mouseY <= 240:
            app.active_input = 'contract_quantity'
        elif 500 <= mouseX <= 650 and 260 <= mouseY <= 290:
            app.active_input = 'selected_period'
        elif 500 <= mouseX <= 650 and 310 <= mouseY <= 340:
            app.active_input = 'holding_period_days'
        elif 500 <= mouseX <= 650 and 360 <= mouseY <= 390:
            app.active_input = 'sell_percentage'


        if 525 <= mouseX <= 625 and 420 <= mouseY <= 470:
            # checkForError(app)


                app.simulate_trades_BCS = True
                # Run the strategy
                portfolio = bullCallSpread.run_bull_call_spread_strategy(app.list_of_holdings_BCS, int(app.portfolio_size_BCS), float(app.risk_tolerance_BCS), int(app.contract_quantity_BCS), int(app.selected_period_BCS), int(app.holding_period_days_BCS), float(app.sell_percentage_BCS))
        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 3)



            
    if app.screen6:

        # Add to holdings
        if 125 <= mouseX <= 275 and 100 <= mouseY <= 150:
            app.adding_to_holdings_6 = True
            app.removing_from_holdings_6 = False

        # Remove from holdings
        elif 125 <= mouseX <= 275 and 200 <= mouseY <= 250:
            app.adding_to_holdings_6 = False
            app.removing_from_holdings_6 = True

        # Back button
        elif 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 3)

        if 500 <= mouseX <= 650 and 110 <= mouseY <= 140:
            app.active_input = 'portfolio_size'

        elif 500 <= mouseX <= 650 and 160 <= mouseY <= 190:
            app.active_input = 'risk_tolerance'

        elif 500 <= mouseX <= 650 and 210 <= mouseY <= 240:
            app.active_input = 'contract_quantity'
        elif 500 <= mouseX <= 650 and 260 <= mouseY <= 290:
            app.active_input = 'selected_period'
        elif 500 <= mouseX <= 650 and 310 <= mouseY <= 340:
            app.active_input = 'holding_period_days'
        elif 500 <= mouseX <= 650 and 360 <= mouseY <= 390:
            app.active_input = 'sell_percentage'


        if 525 <= mouseX <= 625 and 420 <= mouseY <= 470:
            # checkForError(app)


                app.simulate_trades_BPS = True
                # Run the strategy
                portfolio = bearPutSpread.run_bear_put_spread_strategy(app.list_of_holdings_BPS, int(app.portfolio_size_BPS), float(app.risk_tolerance_BPS), int(app.contract_quantity_BPS), int(app.selected_period_BPS), int(app.holding_period_days_BPS), float(app.sell_percentage_BPS))
        if 20 <= mouseX <= 90 and 20 <= mouseY <= 50:
            setScreen(app, 3)



def onKeyPress(app, key):
    if app.screen4:
        
        if app.adding_to_holdings_1:
            if key == 'backspace':
                app.company_to_add_1 = app.company_to_add_1[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_add_1 += key.upper()

            if key == 'enter' and app.company_to_add_1 != '':
                app.list_of_holdings_LC.append(app.company_to_add_1)
                app.company_to_add_1 = ''
                app.adding_to_holdings_1 = False

        elif app.removing_from_holdings_1:
            if key == 'backspace':
                app.company_to_remove_1 = app.company_to_remove_1[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_remove_1 += key.upper()

            if key == 'enter' and app.company_to_remove_1 != '':
                if app.company_to_remove_1 in app.list_of_holdings_LC:
                    app.list_of_holdings_LC.remove(app.company_to_remove_1)
                else:
                    app.not_in_holdings_bool_1 = True
                    app.not_in_holdings_statement_1 = 'company not in holdings, click box to try again'
                app.company_to_remove_1 = ''
                app.removing_from_holdings_1 = False


        if app.active_input == 'portfolio_size':
            if key == 'backspace':
                app.portfolio_size_LC = app.portfolio_size_LC[:-1]
            elif key.isdigit():
                app.portfolio_size_LC += key
        elif app.active_input == 'risk_tolerance':
            if key == 'backspace':
                app.risk_tolerance_LC = app.risk_tolerance_LC[:-1]
            elif key.isdigit() or key == '.':
                app.risk_tolerance_LC += key

        elif app.active_input == 'contract_quantity':
            if key == 'backspace':
                app.contract_quantity_LC = app.contract_quantity_LC[:-1]
            elif key.isdigit():
                app.contract_quantity_LC += key
        elif app.active_input == 'selected_period':
            if key == 'backspace':
                app.selected_period_LC = app.selected_period_LC[:-1]
            elif key.isdigit():
                app.selected_period_LC += key

        elif app.active_input == 'holding_period_days':
            if key == 'backspace':
                app.holding_period_days_LC = app.holding_period_days_LC[:-1]
            elif key.isdigit():
                app.holding_period_days_LC += key
        elif app.active_input == 'sell_percentage':
            if key == 'backspace':
                app.sell_percentage_LC = app.sell_percentage_LC[:-1]
            elif key.isdigit() or key == '.':
                app.sell_percentage_LC += key
        

        if app.simulate_trades_LC and key == 'r':
            app.simulate_trades_LC = False
            app.portfolio_size_LC = ''
            app.risk_tolerance_LC = ''
            app.contract_quantity_LC = ''
            app.sell_percentage_LC = ''
            app.holding_period_days_LC = ''
            app.sell_percentage_LC = ''

            

    if app.screen5:

        
        if app.adding_to_holdings_5:
            if key == 'backspace':
                app.company_to_add_5 = app.company_to_add_5[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_add_5 += key.upper()

            if key == 'enter' and app.company_to_add_5 != '':
                app.list_of_holdings_BCS.append(app.company_to_add_5)
                app.company_to_add_5 = ''
                app.adding_to_holdings_5 = False

        elif app.removing_from_holdings_5:
            if key == 'backspace':
                app.company_to_remove_5 = app.company_to_remove_5[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_remove_5 += key.upper()

            if key == 'enter' and app.company_to_remove_5 != '':
                if app.company_to_remove_5 in app.list_of_holdings_BCS:
                    app.list_of_holdings_BCS.remove(app.company_to_remove_5)
                else:
                    app.not_in_holdings_bool_5 = True
                    app.not_in_holdings_statement_5 = 'company not in holdings, click box to try again'
                app.company_to_remove_5 = ''
                app.removing_from_holdings_5 = False


        if app.active_input == 'portfolio_size':
            if key == 'backspace':
                app.portfolio_size_BCS = app.portfolio_size_BCS[:-1]
            elif key.isdigit():
                app.portfolio_size_BCS += key
        elif app.active_input == 'risk_tolerance':
            if key == 'backspace':
                app.risk_tolerance_BCS = app.risk_tolerance_BCS[:-1]
            elif key.isdigit() or key == '.':
                app.risk_tolerance_BCS += key

        elif app.active_input == 'contract_quantity':
            if key == 'backspace':
                app.contract_quantity_BCS = app.contract_quantity_BCS[:-1]
            elif key.isdigit():
                app.contract_quantity_BCS += key
        elif app.active_input == 'selected_period':
            if key == 'backspace':
                app.selected_period_BCS = app.selected_period_BCS[:-1]
            elif key.isdigit():
                app.selected_period_BCS += key

        elif app.active_input == 'holding_period_days':
            if key == 'backspace':
                app.holding_period_days_BCS = app.holding_period_days_BCS[:-1]
            elif key.isdigit():
                app.holding_period_days_BCS += key
        elif app.active_input == 'sell_percentage':
            if key == 'backspace':
                app.sell_percentage_BCS = app.sell_percentage_BCS[:-1]
            elif key.isdigit() or key == '.':
                app.sell_percentage_BCS += key
        

        if app.simulate_trades_BCS and key == 'r':
            app.simulate_trades_BCS = False
            app.portfolio_size_BCS = ''
            app.risk_tolerance_BCS = ''
            app.contract_quantity_BCS = ''
            app.sell_percentage_BCS = ''
            app.holding_period_days_BCS = ''
            app.sell_percentage_BCS = ''


    if app.screen6:
        if app.adding_to_holdings_6:
            if key == 'backspace':
                app.company_to_add_6 = app.company_to_add_6[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_add_6 += key.upper()

            if key == 'enter' and app.company_to_add_6 != '':
                app.list_of_holdings_BPS.append(app.company_to_add_6)
                app.company_to_add_6 = ''
                app.adding_to_holdings_6 = False

        elif app.removing_from_holdings_6:
            if key == 'backspace':
                app.company_to_remove_6 = app.company_to_remove_6[:-1]
            elif key.isalpha() and key != 'enter':
                app.company_to_remove_6 += key.upper()

            if key == 'enter' and app.company_to_remove_6 != '':
                if app.company_to_remove_6 in app.list_of_holdings_BPS:
                    app.list_of_holdings_BPS.remove(app.company_to_remove_6)
                else:
                    app.not_in_holdings_bool_6 = True
                    app.not_in_holdings_statement_6 = 'company not in holdings, click box to try again'
                app.company_to_remove_6 = ''
                app.removing_from_holdings_6 = False


        if app.active_input == 'portfolio_size':
            if key == 'backspace':
                app.portfolio_size_BPS = app.portfolio_size_BPS[:-1]
            elif key.isdigit():
                app.portfolio_size_BPS += key
        elif app.active_input == 'risk_tolerance':
            if key == 'backspace':
                app.risk_tolerance_BPS = app.risk_tolerance_BPS[:-1]
            elif key.isdigit() or key == '.':
                app.risk_tolerance_BPS += key

        elif app.active_input == 'contract_quantity':
            if key == 'backspace':
                app.contract_quantity_BPS = app.contract_quantity_BPS[:-1]
            elif key.isdigit():
                app.contract_quantity_BPS += key
        elif app.active_input == 'selected_period':
            if key == 'backspace':
                app.selected_period_BPS = app.selected_period_BPS[:-1]
            elif key.isdigit():
                app.selected_period_BPS += key

        elif app.active_input == 'holding_period_days':
            if key == 'backspace':
                app.holding_period_days_BPS = app.holding_period_days_BPS[:-1]
            elif key.isdigit():
                app.holding_period_days_BPS += key
        elif app.active_input == 'sell_percentage':
            if key == 'backspace':
                app.sell_percentage_BPS = app.sell_percentage_BPS[:-1]
            elif key.isdigit() or key == '.':
                app.sell_percentage_BPS += key


        if app.simulate_trades_BPS and key == 'r':
            app.simulate_trades_BPS = False
            app.portfolio_size_BPS = ''
            app.risk_tolerance_BPS = ''
            app.contract_quantity_BPS = ''
            app.sell_percentage_BPS = ''
            app.holding_period_days_BPS = ''
            app.sell_percentage_BPS = ''

            
    # Screen 8 key presses
    if app.screen8:
        if app.active_input_price_model == 'strike_price':
            if key == 'backspace':
                app.strike_price = app.strike_price[:-1]
            elif key.isdigit() or key == '.':
                app.strike_price += key

            

        elif app.active_input_price_model == 'risk_free_rate':
            if key == 'backspace':
                app.risk_free_rate = app.risk_free_rate[:-1]
            elif key.isdigit() or key == '.':
                app.risk_free_rate += key

        elif app.active_input_price_model == 'time_to_maturity':
            if key == 'backspace':
                app.time_to_maturity = app.time_to_maturity[:-1]
            elif key.isdigit() or key == '.':
                app.time_to_maturity += key

        elif app.active_input_price_model == 'volatility':
            if key == 'backspace':
                app.volatility = app.volatility[:-1]
            elif key.isdigit() or key == '.':
                app.volatility += key

        elif app.active_input_price_model == 'underlying_price':
            if key == 'backspace':
                app.underlying_price = app.underlying_price[:-1]
            elif key.isdigit() or key == '.':
                app.underlying_price += key

        elif app.active_input_price_model == 'contract_type':
            if key == 'backspace':
                app.contract_type = app.contract_type[:-1]
            elif key.isalpha() and key != 'enter':
                app.contract_type += key.upper()

    # Screen 9 key presses
    
    # if app.screen9:
    #     if app.show_enter_statement:
    #         if app.type_stock:
    #             app.type_start_date = False
    #             app.type_end_date = False
    #             if key == 'backspace':
    #                 app.underlying_symbol = app.underlying_symbol[:-1]
    #             elif key == 'enter' and app.underlying_symbol != '':
    #                 app.border_screen9_1 = 'green'
    #             elif key.isalpha():
    #                 app.underlying_symbol += key.upper()

    #         elif app.type_start_date:
    #             app.type_stock = False
    #             app.type_end_date = False
    #             if key == 'backspace':
    #                 app.start_date = app.start_date[:-1]
    #             elif key.isdigit() or key == '-':
    #                 app.start_date += key
    #             elif key == 'enter' and app.start_date != '':
    #                 app.border_screen9_2 = 'green'

    #         elif app.type_end_date:
    #             app.type_stock = False
    #             app.type_start_date = False
    #             if key == 'backspace':
    #                 app.end_date = app.end_date[:-1]
    #             elif key.isdigit() or key == '-':
    #                 app.end_date += key
    #             elif key == 'enter' and app.end_date != '':
    #                 app.border_screen9_3 = 'green'

    #         if app.border_screen9_1 == 'green' and app.border_screen9_2 == 'green' and app.border_screen9_3 == 'green':
    #             app.show_enter_statement = False
    #             app.show_restart_statement = True

    #     elif app.show_restart_statement:
    #         if key == 'r':
    #             app.show_enter_statement = True
    #             app.show_restart_statement = False
    #             app.underlying_symbol = ''
    #             app.start_date = ''
    #             app.end_date = ''
    #             app.border_screen9_1 = 'red'
    #             app.border_screen9_2 = 'red'
    #             app.border_screen9_3 = 'red'
    #             app.graph_image_path = None


    # Screen 11 key presses
    if app.screen11:
        if app.show_enter_statement_O:
            # Handle input for stock ticker
            if app.type_stock_O:
                if key == 'backspace':
                    app.stock_O = app.stock_O[:-1]
                elif key == 'enter' and app.stock_O != '':
                    app.border_screen11_1 = 'green'
                elif key.isalpha():
                    app.stock_O += key.upper()

            # Handle input for start date
            elif app.type_start_date_O:
                if key == 'backspace':
                    app.start_date_O = app.start_date_O[:-1]
                elif key.isdigit() or key == '-':
                    app.start_date_O += key
                elif key == 'enter' and app.start_date_O != '':
                    app.border_screen11_2 = 'green'

            # Handle input for end date
            elif app.type_end_date_O:
                if key == 'backspace':
                    app.end_date_O = app.end_date_O[:-1]
                elif key.isdigit() or key == '-':
                    app.end_date_O += key
                elif key == 'enter' and app.end_date_O != '':
                    app.border_screen11_3 = 'green'

            # Check if all input fields are filled
            if (app.border_screen11_1 == 'green' and
                app.border_screen11_2 == 'green' and
                app.border_screen11_3 == 'green'):
                app.show_enter_statement_O = False
                app.show_restart_statement_O = True

        elif app.show_restart_statement_O:
            # Transition to screen14 if 'r' is pressed
            app.screen11 = False
            app.screen14 = True
            if key == 'g':
                app.screen11 = False
                app.screen14 = True
                app.show_enter_statement_O = True
                app.show_restart_statement_O = False

                # Reset input fields for the next input cycle
                app.type_stock_O = False
                app.type_start_date_O = False
                app.type_end_date_O = False
                app.stock_O = ''
                app.start_date_O = ''
                app.end_date_O = ''
                app.border_screen11_1 = 'black'
                app.border_screen11_2 = 'black'
                app.border_screen11_3 = 'black'

def onMouseRelease(app, mouseX, mouseY):
    app.selected_dot = False
    app.dot_not_selected = True

    

            

def main():
    runApp(width=800, height=800)

main()
