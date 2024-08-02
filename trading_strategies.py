import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from BlackScholes_Greeks import optionsGreeks, marketData

# Used ChatGPT to help me understand and implement the modules so I could work with real data from Yahoo Finance

# also used https://pandas.pydata.org/docs/reference/general_functions.html to help me a lot with the data frames
# learned the lambda sorting https://stackoverflow.com/questions/8966538/syntax-behind-sortedkey-lambda






class longCall:
    def __init__(self, symbol, portfolio_size, risk_tolerance, contract_quantity):
        self.symbol = symbol
        self.portfolio_size = portfolio_size
        self.risk_tolerance = risk_tolerance
        self.contract_quantity = contract_quantity
        self.market_data_instance = marketData()
        self.market_data = self.get_market_data(symbol)
        self.expiry = self.get_next_expiry_date(symbol)
        self.expiry_date = datetime.strptime(self.expiry, '%Y-%m-%d').replace(tzinfo=None)
        if self.expiry is None:
            raise ValueError(f"No options expiry dates found for symbol: {symbol}")
        self.strike = self.get_at_the_money_strike(symbol)
        self.quantity = 0
        self.contract_type = 'call'
        self.greeks = None
        self.current_price = None
        self.current_value = 0
        self.total_profits = 0
        self.transactions = 0
        self.holdings = 0
        self.premium_paid = 0
        self.holding_days = 30
        self.long_call_strike = None
        self.long_call_price = 0

        # Calculate initial quantity
        self.calculate_quantity()

    def get_market_data(self, symbol):
        S, sigma, r, T, data = self.market_data_instance.grab_data(symbol, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
        if data.empty:
            raise ValueError(f"Market data for {symbol} is empty.")
        if 'Adj Close' not in data.columns:
            raise KeyError(f"'Adj Close' column is missing in market data for {symbol}.")
        return S, sigma, r, T, data

    def get_next_expiry_date(self, symbol):
        ticker = yf.Ticker(symbol)
        options = ticker.options
        if not options:
            return None
        return options[0]

    def get_options_contracts(self):
        option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
        calls = option_chain.calls
        return calls

    def get_at_the_money_strike(self, symbol):
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period='1d')['Close'].iloc[-1]
        option_chain = ticker.option_chain(self.expiry)
        strikes = option_chain.calls['strike']
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))
        return atm_strike

    def calculate_quantity(self):
        #maximum ivestment of a particular option 
        max_investment = self.portfolio_size * self.risk_tolerance
        # risk tolerance taking into account the volatility which is equal to the standard deviation of the returns over the last year
        volatility_adjusted_risk_tolerance = self.risk_tolerance / (1 + self.market_data[1])
        #new max investment takes into account the volatility adjusted risk tolerance
        adjusted_max_investment = self.portfolio_size * volatility_adjusted_risk_tolerance
        option_price = self.get_option_price(self.strike)
        
        if option_price == 0:
            self.quantity = 1
        else:
            self.quantity = max(1, int(adjusted_max_investment / (option_price * 100)))
        
    #how much is the price of the option contract
    def get_option_price(self, strike, date=None):
        if date is None:
            option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
            option = option_chain.calls[option_chain.calls['strike'] == strike]
            option_price = option['lastPrice'].values[0] if not option.empty else 0
            return option_price
        else:
            if self.current_price is None:
                self.current_price = self.get_current_underlying_price()
            S = self.current_price
            K = strike
            T = (self.expiry_date - date.replace(tzinfo=None)).days / 365
            if T <= 0:
                T = 1/365 
            
            r = self.market_data_instance.r
            sigma = self.market_data_instance.sigma
            bs = optionsGreeks(S, K, T, r, sigma)
            option_price = bs.call_price(self.strike)
            return option_price
    #price of the stock that the option is tied to
    def get_current_underlying_price(self):
        ticker = yf.Ticker(self.symbol)
        self.current_price = ticker.history(period='1d')['Close'].iloc[-1]
        return self.current_price
    #calculate the greeks of the option, equations are in the BlackScholes_Greeks.py file
    def calculate_greeks(self):
        self.greeks = optionsGreeks(self.market_data[0], self.strike, self.market_data[3], self.market_data[2], self.market_data[1])

    #calculate the value of the trade, the price of the option contract times the quantity
    def update_price(self, date):
        self.long_call_price = self.get_option_price(self.long_call_strike, date)
        self.current_value = self.long_call_price * self.quantity * 100
    #calculate the cumulative profits, the value of the final price minus the initial price, calculated daily
    def calculate_profit(self, initial_long_call_price):
        daily_profit = ((self.long_call_price - initial_long_call_price) * self.quantity * 100)
        self.total_profits += daily_profit

    # call the functions to calculate the greeks, update the price, and calculate the profit
    def run(self):
        self.calculate_greeks()
        self.update_price(datetime.now())
        self.calculate_profit()

    
    #call the strategy 
    def execute_long_call_strategy(self):
        
        market_data = self.market_data
        S, sigma, r, T, _ = market_data
        calls = self.get_options_contracts()
        
        current_price = self.get_current_underlying_price()
        calls['expiry'] = pd.to_datetime(calls['lastTradeDate']).dt.tz_localize(None)

        now = pd.to_datetime(datetime.now()).tz_localize(None)
        #options with a maturity date in the desired range
        target_expiries = calls.loc[(calls['expiry'] - now).dt.days.between(30, 60)].copy()
        #if there is none increase the time range
        if target_expiries.empty:
            target_expiries = calls.loc[(calls['expiry'] - now).dt.days.between(0, 90)].copy()
        #if there is still none return
        if target_expiries.empty:
            return

        historical_volatility = sigma

        #the desired range of strike prices is the current price +/- half the historical volatility
        strike_price_range = (self.current_price * 0.95, self.current_price * 1.05) #(current_price * (1 + historical_volatility / 2), current_price * (1 + historical_volatility))
        target_calls = target_expiries.loc[
            (target_expiries['strike'] >= strike_price_range[0]) & 
            (target_expiries['strike'] <= strike_price_range[1])].copy()
        if target_calls.empty:
            return

        target_call_to_buy = target_calls.iloc[(target_calls['strike'] - current_price).abs().argsort()[:1]]
        strike_price_to_buy = target_call_to_buy['strike'].values[0]
        premium_to_buy = target_call_to_buy['lastPrice'].values[0]
        expiry_to_buy = target_call_to_buy['expiry'].values[0]
        self.long_call_strike = strike_price_to_buy
        self.long_call_price = premium_to_buy
        self.log_transaction(self.symbol, 'call', expiry_to_buy, strike_price_to_buy, self.quantity, 'buy', premium_to_buy)
        self.holdings += self.quantity
        self.premium_paid += premium_to_buy * self.quantity * 100

    def simulate_portfolio(self, period, holding_period_days=30, sell_percentage=0.25):
        start_date = datetime.now() - timedelta(days=period)
        end_date = datetime.now()
        self.market_data = self.get_market_data(self.symbol)
        self.simulate_trading(start_date, end_date, holding_period_days, sell_percentage)
        historical_data = yf.Ticker(self.symbol).history(start=start_date, end=end_date)
        initial_long_call_price = self.get_option_price(self.long_call_strike, start_date)
        self.calculate_portfolio_value(historical_data, initial_long_call_price)

        self.total_profits -= self.premium_paid

        result = {
            'symbol': self.symbol,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'transactions': self.transactions,
            'holdings': self.holdings,
            'total profits': float(self.total_profits),
            'current portfolio value': float(self.current_value)
        }

        return result

    def simulate_trading(self, start_date, end_date, holding_period_days=30, sell_percentage=0.25):
        ticker = yf.Ticker(self.symbol)
        historical_data = ticker.history(start=start_date, end=end_date)
        
        current_date = start_date
        while current_date < end_date:
            self.long_call_strike = self.get_at_the_money_strike(self.symbol)
            initial_long_call_price = self.get_option_price(self.long_call_strike, current_date)
            self.log_transaction(self.symbol, 'call', self.expiry, self.long_call_strike, self.quantity, 'buy', initial_long_call_price)
            
            holding_end_date = current_date + timedelta(days=holding_period_days)
            if holding_end_date > end_date:
                holding_end_date = end_date
            
            holding_period_range = pd.date_range(start=current_date, end=holding_end_date, freq='B')
            holding_period_range = holding_period_range.intersection(historical_data.index)
            
            for day in holding_period_range:
                self.current_price = historical_data.loc[day]['Close']
                self.update_price(day)
                self.calculate_profit(initial_long_call_price)

            sell_quantity = max(1, int(self.holdings * sell_percentage))
            final_long_call_price = self.get_option_price(self.long_call_strike, holding_end_date)
            self.log_transaction(self.symbol, 'call', self.expiry, self.long_call_strike, sell_quantity, 'sell', final_long_call_price)
            self.total_profits += ((final_long_call_price - initial_long_call_price) * sell_quantity * 100)
            current_date = holding_end_date + timedelta(days=1)

    def calculate_portfolio_value(self, historical_data, initial_long_call_price):
        self.total_profits = 0
        for index, row in historical_data.iterrows():
            self.current_price = row['Close']
            self.update_price(row.name)
            self.calculate_profit(initial_long_call_price)

    def log_transaction(self, symbol, contract_type, expiry, strike, quantity, action, price):
        self.transactions += 1
        if action == 'buy':
            self.holdings += quantity
            self.premium_paid += price * quantity * 100
            self.current_value -= price * quantity * 100
        elif action == 'sell':
            self.holdings -= quantity
            self.current_value += price * quantity * 100
        print(f"Transaction: {action}, Quantity: {quantity}, Holdings: {self.holdings}")
    @staticmethod
    def format_result(result):
        return (
            f"symbol: {result['symbol']}\n"
            f"period: {result['period']}\n"
            f"start_date: {result['start_date']}\n"
            f"end_date: {result['end_date']}\n"
            f"transactions: {result['transactions']}\n"
            f"holdings: {result['holdings']}\n"
            f"total profits: {result['total profits']}\n"
            f"current portfolio value: {result['current portfolio value']}"
        )
    
    @staticmethod
    def run_long_call_strategy(symbols, portfolio_size, risk_tolerance, contract_quantity, period, holding_period_days, sell_percentage):
        results = []
        total_profits = 0
        total_transactions = 0  # Initialize as an integer
        total_holdings = 0
        final_portfolio_value = 0
        
        for symbol in symbols:
            long_call = longCall(symbol, portfolio_size, risk_tolerance, contract_quantity)
            result = long_call.simulate_portfolio(period, holding_period_days, sell_percentage)
            results.append(result)
            total_profits += result['total profits']
            total_transactions += result['transactions'] 
            total_holdings += result['holdings']

            
            formatted_result = longCall.format_result(result)
            print(f"Results for {symbol}:\n{formatted_result}\n")

        return (
            total_transactions,
            symbols,
            period,
            result['start_date'],
            result['end_date'],
            total_holdings,
            total_profits,

        )




class bullCallSpread:
    def __init__(self, symbol, portfolio_size, risk_tolerance, contract_quantity):
        self.symbol = symbol
        self.portfolio_size = portfolio_size
        self.risk_tolerance = risk_tolerance
        self.contract_quantity = contract_quantity
        self.market_data_instance = marketData()
        self.market_data = self.get_market_data(symbol)
        self.expiry = self.get_next_expiry_date(symbol)
        self.expiry_date = datetime.strptime(self.expiry, '%Y-%m-%d').replace(tzinfo=None)
        if self.expiry is None:
            raise ValueError(f"No options expiry dates found for symbol: {symbol}")
        self.strike = self.get_at_the_money_strike(symbol)
        self.quantity = 0
        self.contract_type = 'call'
        self.greeks = None
        self.current_price = None
        self.current_value = 0
        self.total_profits = 0
        self.transactions = 0
        self.holdings = 0
        self.premium_paid = 0
        self.holding_days = 30
        self.long_call_strike = None
        self.long_call_price = 0

        # Calculate initial quantity
        self.calculate_quantity()

    def get_market_data(self, symbol):
        S, sigma, r, T, data = self.market_data_instance.grab_data(symbol, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
        if data.empty:
            raise ValueError(f"Market data for {symbol} is empty.")
        if 'Adj Close' not in data.columns:
            raise KeyError(f"'Adj Close' column is missing in market data for {symbol}.")
        return S, sigma, r, T, data

    def get_next_expiry_date(self, symbol):
        ticker = yf.Ticker(symbol)
        options = ticker.options
        if not options:
            return None
        return options[0]

    def get_options_contracts(self):
        option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
        calls = option_chain.calls
        return calls

    def get_at_the_money_strike(self, symbol):
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period='1d')['Close'].iloc[-1]
        option_chain = ticker.option_chain(self.expiry)
        strikes = option_chain.calls['strike']
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))
        return atm_strike

    def calculate_quantity(self):
        max_investment = self.portfolio_size * self.risk_tolerance
        volatility_adjusted_risk_tolerance = self.risk_tolerance / (1 + self.market_data[1])
        adjusted_max_investment = self.portfolio_size * volatility_adjusted_risk_tolerance
        option_price = self.get_option_price(self.strike)
        
        if option_price == 0:
            self.quantity = 1
        else:
            self.quantity = max(1, int(adjusted_max_investment / (option_price * 100)))
        print(f"Calculated Quantity: {self.quantity}, Option Price: {option_price}")

    def get_option_price(self, strike, date=None):
        if date is None:
            option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
            option = option_chain.calls[option_chain.calls['strike'] == strike]
            option_price = option['lastPrice'].values[0] if not option.empty else 0
            return option_price
        else:
            if self.current_price is None:
                self.current_price = self.get_current_underlying_price()
            S = self.current_price
            K = strike
            T = (self.expiry_date - date.replace(tzinfo=None)).days / 365
            r = self.market_data_instance.r
            if T <= 0:
                T = 1/365 
            sigma = self.market_data_instance.sigma
            bs = optionsGreeks(S, K, T, r, sigma)
            option_price = bs.call_price(self.strike)
            return option_price

    def get_current_underlying_price(self):
        ticker = yf.Ticker(self.symbol)
        self.current_price = ticker.history(period='1d')['Close'].iloc[-1]
        return self.current_price

    def calculate_greeks(self):
        self.greeks = optionsGreeks(self.market_data[0], self.strike, self.market_data[3], self.market_data[2], self.market_data[1])

    def update_price(self, date):
        self.long_call_price = self.get_option_price(self.long_call_strike, date)
        self.current_value = self.long_call_price * self.quantity * 100

    def calculate_profit(self, initial_long_call_price):
        daily_profit = ((self.long_call_price - initial_long_call_price) * self.quantity * 100)
        self.total_profits += daily_profit

    def run(self):
        self.calculate_greeks()
        self.update_price(datetime.now())
        self.calculate_profit()

    def execute_bull_call_spread_strategy(self):
        market_data = self.market_data
        S, sigma, r, T, _ = market_data
        calls = self.get_options_contracts()
        current_price = self.get_current_underlying_price()
        calls['expiry'] = pd.to_datetime(calls['lastTradeDate']).dt.tz_localize(None)

        now = pd.to_datetime(datetime.now()).tz_localize(None)

        # Calculate days until expiry
        calls['days_until_expiry'] = (calls['expiry'] - now).dt.days

        # Options with a maturity date in the desired range
        target_expiries = calls.loc[calls['days_until_expiry'].between(30, 60)].copy()

        # If there are none, increase the time range
        if target_expiries.empty:
            target_expiries = calls.loc[calls['days_until_expiry'].between(0, 90)].copy()

        # If there are still none, return
        if target_expiries.empty:
            return

        historical_volatility = sigma

        # The desired range of strike prices is the current price +/- half the historical volatility
        strike_price_range = (self.current_price * 0.95, self.current_price * 1.05)
        target_calls = target_expiries.loc[
            (target_expiries['strike'] >= strike_price_range[0]) & 
            (target_expiries['strike'] <= strike_price_range[1])].copy()

        if target_calls.empty:
            return

        # Select the strike price to buy (ATM)
        target_call_to_buy = target_calls.iloc[(target_calls['strike'] - current_price).abs().argsort()[:1]]
        strike_price_to_buy = target_call_to_buy['strike'].values[0]
        premium_to_buy = target_call_to_buy['lastPrice'].values[0]
        expiry_to_buy = target_call_to_buy['expiry'].values[0]

        # Select the strike price to sell (higher than the one you bought, OTM)
        target_call_to_sell = target_calls.loc[target_calls['strike'] > strike_price_to_buy].iloc[0]
        strike_price_to_sell = target_call_to_sell['strike']
        premium_to_sell = target_call_to_sell['lastPrice']

        self.long_call_strike = strike_price_to_buy
        self.long_call_price = premium_to_buy
        self.short_call_strike = strike_price_to_sell
        self.short_call_price = premium_to_sell


        self.log_transaction(self.symbol, 'call', expiry_to_buy, strike_price_to_buy, self.quantity, 'buy', premium_to_buy)
        self.log_transaction(self.symbol, 'call', expiry_to_buy, strike_price_to_sell, self.quantity, 'sell', premium_to_sell)


        self.holdings += self.quantity
        self.premium_paid += premium_to_buy * self.quantity * 100
        self.premium_paid += premium_to_sell * self.quantity * 100


    def simulate_portfolio(self, period, holding_period_days=30, sell_percentage=0.25):
        start_date = datetime.now() - timedelta(days=period)
        end_date = datetime.now()
        self.market_data = self.get_market_data(self.symbol)
        self.simulate_trading(start_date, end_date, holding_period_days, sell_percentage)
        historical_data = yf.Ticker(self.symbol).history(start=start_date, end=end_date)
        initial_long_call_price = self.get_option_price(self.long_call_strike, start_date)
        self.calculate_portfolio_value(historical_data, initial_long_call_price)

        self.total_profits -= self.premium_paid

        result = {
            'symbol': self.symbol,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'transactions': self.transactions,
            'holdings': self.holdings,
            'total profits': float(self.total_profits),
            'current portfolio value': float(self.current_value)
        }

        return result

    def simulate_trading(self, start_date, end_date, holding_period_days=30, sell_percentage=0.25):
        ticker = yf.Ticker(self.symbol)
        historical_data = ticker.history(start=start_date, end=end_date)
        
        current_date = start_date
        while current_date < end_date:
            self.long_call_strike = self.get_at_the_money_strike(self.symbol)
            initial_long_call_price = self.get_option_price(self.long_call_strike, current_date)
            self.log_transaction(self.symbol, 'call', self.expiry, self.long_call_strike, self.quantity, 'buy', initial_long_call_price)
            
            holding_end_date = current_date + timedelta(days=holding_period_days)
            if holding_end_date > end_date:
                holding_end_date = end_date
            
            holding_period_range = pd.date_range(start=current_date, end=holding_end_date, freq='B')
            holding_period_range = holding_period_range.intersection(historical_data.index)
            
            for day in holding_period_range:
                self.current_price = historical_data.loc[day]['Close']
                self.update_price(day)
                self.calculate_profit(initial_long_call_price)

            sell_quantity = max(1, int(self.holdings * sell_percentage))
            final_long_call_price = self.get_option_price(self.long_call_strike, holding_end_date)
            self.log_transaction(self.symbol, 'call', self.expiry, self.long_call_strike, sell_quantity, 'sell', final_long_call_price)
            self.total_profits += ((final_long_call_price - initial_long_call_price) * sell_quantity * 100)
            current_date = holding_end_date + timedelta(days=1)

    def calculate_portfolio_value(self, historical_data, initial_long_call_price):
        self.total_profits = 0
        for index, row in historical_data.iterrows():
            self.current_price = row['Close']
            self.update_price(row.name)
            self.calculate_profit(initial_long_call_price)

    def log_transaction(self, symbol, contract_type, expiry, strike, quantity, action, price):
        self.transactions += 1
        if action == 'buy':
            self.holdings += quantity
            self.premium_paid += price * quantity * 100
            self.current_value -= price * quantity * 100
        elif action == 'sell':
            self.holdings -= quantity
            self.current_value += price * quantity * 100
        print(f"Transaction: {action}, Quantity: {quantity}, Holdings: {self.holdings}")

    @staticmethod
    def format_result(result):
        return (
            f"symbol: {result['symbol']}\n"
            f"period: {result['period']}\n"
            f"start_date: {result['start_date']}\n"
            f"end_date: {result['end_date']}\n"
            f"transactions: {result['transactions']}\n"
            f"holdings: {result['holdings']}\n"
            f"total profits: {result['total profits']}\n"
            f"current portfolio value: {result['current portfolio value']}"
        )

    @staticmethod
    def run_bull_call_spread_strategy(symbols, portfolio_size, risk_tolerance, contract_quantity, period, holding_period_days, sell_percentage):
        results = []
        total_profits = 0
        total_transactions = 0  
        total_holdings = 0
        final_portfolio_value = 0
        
        for symbol in symbols:
            bull_call = bullCallSpread(symbol, portfolio_size, risk_tolerance, contract_quantity)
            result = bull_call.simulate_portfolio(period, holding_period_days, sell_percentage)
            results.append(result)
            total_profits += result['total profits']
            total_transactions += result['transactions'] 
            total_holdings += result['holdings']
            final_portfolio_value += result['current portfolio value']
            
            formatted_result = bullCallSpread.format_result(result)
            print(f"Results for {symbol}:\n{formatted_result}\n")

        return (
            total_transactions,
            symbols,
            period,
            result['start_date'],
            result['end_date'],
            total_holdings,
            total_profits,
            final_portfolio_value
        )



class bearPutSpread:

    def __init__(self, symbol, portfolio_size, risk_tolerance, contract_quantity):
        self.symbol = symbol
        self.portfolio_size = portfolio_size
        self.risk_tolerance = risk_tolerance
        self.contract_quantity = contract_quantity
        self.market_data_instance = marketData()
        self.market_data = self.get_market_data(symbol)
        self.expiry = self.get_next_expiry_date(symbol)
        self.expiry_date = datetime.strptime(self.expiry, '%Y-%m-%d').replace(tzinfo=None)
        if self.expiry is None:
            raise ValueError(f"No options expiry dates found for symbol: {symbol}")
        self.strike = self.get_at_the_money_strike(symbol)
        self.quantity = 0
        self.contract_type = 'put'
        self.greeks = None
        self.current_price = None
        self.current_value = 0
        self.total_profits = 0
        self.transactions = 0
        self.holdings = 0
        self.premium_paid = 0
        self.holding_days = 30
        self.long_put_strike = None
        self.long_put_price = 0


        self.calculate_quantity()

    def get_market_data(self, symbol):
        S, sigma, r, T, data = self.market_data_instance.grab_data(symbol, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
        if data.empty:
            raise ValueError(f"Market data for {symbol} is empty.")
        if 'Adj Close' not in data.columns:
            raise KeyError(f"'Adj Close' column is missing in market data for {symbol}.")
        return S, sigma, r, T, data

    def get_next_expiry_date(self, symbol):
        ticker = yf.Ticker(symbol)
        options = ticker.options
        if not options:
            return None
        return options[0]

    def get_options_contracts(self):
        option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
        puts = option_chain.puts
        return puts

    def get_at_the_money_strike(self, symbol):
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period='1d')['Close'].iloc[-1]
        option_chain = ticker.option_chain(self.expiry)
        strikes = option_chain.puts['strike']
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))
        return atm_strike

    def calculate_quantity(self):
        max_investment = self.portfolio_size * self.risk_tolerance
        volatility_adjusted_risk_tolerance = self.risk_tolerance / (1 + self.market_data[1])
        adjusted_max_investment = self.portfolio_size * volatility_adjusted_risk_tolerance
        option_price = self.get_option_price(self.strike)
        
        if option_price == 0:
            self.quantity = 1
        else:
            self.quantity = max(1, int(adjusted_max_investment / (option_price * 100)))
        print(f"Calculated Quantity: {self.quantity}, Option Price: {option_price}")

    def get_option_price(self, strike, date=None):
        if date is None:
            option_chain = yf.Ticker(self.symbol).option_chain(self.expiry)
            option = option_chain.puts[option_chain.puts['strike'] == strike]
            option_price = option['lastPrice'].values[0] if not option.empty else 0
            return option_price
        else:
            if self.current_price is None:
                self.current_price = self.get_current_underlying_price()
            S = self.current_price
            K = strike
            T = (self.expiry_date - date.replace(tzinfo=None)).days / 365
            r = self.market_data_instance.r
            sigma = self.market_data_instance.sigma
            if T <= 0:
                T = 1/365 
            bs = optionsGreeks(S, K, T, r, sigma)
            option_price = bs.put_price(self.strike)
            return option_price

    def get_current_underlying_price(self):
        ticker = yf.Ticker(self.symbol)
        self.current_price = ticker.history(period='1d')['Close'].iloc[-1]
        return self.current_price

    def calculate_greeks(self):
        self.greeks = optionsGreeks(self.market_data[0], self.strike, self.market_data[3], self.market_data[2], self.market_data[1])

    def update_price(self, date):
        self.long_put_price = self.get_option_price(self.long_put_strike, date)
        self.current_value = self.long_put_price * self.quantity * 100

    def calculate_profit(self, initial_long_put_price):
        daily_profit = ((self.long_put_price - initial_long_put_price) * self.quantity * 100)
        self.total_profits += daily_profit

    def run(self):
        self.calculate_greeks()
        self.update_price(datetime.now())
        self.calculate_profit()

    def execute_bear_put_spread_strategy(self):


        market_data = self.market_data
        S, sigma, r, T, _ = market_data
        puts = self.get_options_contracts()


        puts['expiry'] = pd.to_datetime(puts['lastTradeDate']).dt.tz_localize(None)

        # Get the current time and make sure it's timezone-naive
        now = pd.to_datetime(datetime.now()).replace(tzinfo=None)

        # Calculate days until expiry
        puts['days_until_expiry'] = (puts['expiry'] - now).dt.days

        # Options with a maturity date in the desired range
        target_expiries = puts.loc[puts['days_until_expiry'].between(30, 60)].copy()

        # If there are none, increase the time range
        if target_expiries.empty:
            target_expiries = puts.loc[puts['days_until_expiry'].between(0, 90)].copy()


        if target_expiries.empty:
            return

        historical_volatility = sigma

        # The desired range of strike prices is the current price +/- half the historical volatility
        strike_price_range = (self.current_price * 0.95, self.current_price * 1.05)
        target_puts = target_expiries.loc[
            (target_expiries['strike'] >= strike_price_range[0]) & 
            (target_expiries['strike'] <= strike_price_range[1])].copy()

        if target_puts.empty:
            return

        # Select the strike price to buy (ATM or slightly ITM)
        target_put_to_buy = target_puts.iloc[(target_puts['strike'] - self.current_price).abs().argsort()[:1]]
        strike_price_to_buy = target_put_to_buy['strike'].values[0]
        premium_to_buy = target_put_to_buy['lastPrice'].values[0]
        expiry_to_buy = target_put_to_buy['expiry'].values[0]

        # Select the strike price to sell (lower than the one you bought, OTM)
        target_put_to_sell = target_puts.loc[target_puts['strike'] < strike_price_to_buy].iloc[0]
        strike_price_to_sell = target_put_to_sell['strike']
        premium_to_sell = target_put_to_sell['lastPrice']

        self.long_put_strike = strike_price_to_buy
        self.long_put_price = premium_to_buy
        self.short_put_strike = strike_price_to_sell
        self.short_put_price = premium_to_sell


        self.log_transaction(self.symbol, 'put', expiry_to_buy, strike_price_to_buy, self.quantity, 'buy', premium_to_buy)
        self.log_transaction(self.symbol, 'put', expiry_to_buy, strike_price_to_sell, self.quantity, 'sell', premium_to_sell)


        self.holdings += self.quantity
        self.premium_paid += premium_to_buy * self.quantity * 100
        self.premium_paid += premium_to_sell * self.quantity * 100



    def simulate_portfolio(self, period, holding_period_days=30, sell_percentage=0.25):
        start_date = datetime.now() - timedelta(days=period)
        end_date = datetime.now()
        self.market_data = self.get_market_data(self.symbol)
        self.simulate_trading(start_date, end_date, holding_period_days, sell_percentage)
        historical_data = yf.Ticker(self.symbol).history(start=start_date, end=end_date)
        initial_long_put_price = self.get_option_price(self.long_put_strike, start_date)
        self.calculate_portfolio_value(historical_data, initial_long_put_price)

        self.total_profits -= self.premium_paid

        result = {
            'symbol': self.symbol,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'transactions': self.transactions,
            'holdings': self.holdings,
            'total profits': float(self.total_profits),
            'current portfolio value': float(self.current_value)
        }

        return result

    def simulate_trading(self, start_date, end_date, holding_period_days=30, sell_percentage=0.25):
        ticker = yf.Ticker(self.symbol)
        historical_data = ticker.history(start=start_date, end=end_date)
        
        current_date = start_date
        while current_date < end_date:
            self.long_put_strike = self.get_at_the_money_strike(self.symbol)
            initial_long_put_price = self.get_option_price(self.long_put_strike, current_date)
            self.log_transaction(self.symbol, 'put', self.expiry, self.long_put_strike, self.quantity, 'buy', initial_long_put_price)
            
            holding_end_date = current_date + timedelta(days=holding_period_days)
            if holding_end_date > end_date:
                holding_end_date = end_date
            
            holding_period_range = pd.date_range(start=current_date, end=holding_end_date, freq='B')
            holding_period_range = holding_period_range.intersection(historical_data.index)
            
            for day in holding_period_range:
                self.current_price = historical_data.loc[day]['Close']
                self.update_price(day)
                self.calculate_profit(initial_long_put_price)

            sell_quantity = max(1, int(self.holdings * sell_percentage))
            final_long_put_price = self.get_option_price(self.long_put_strike, holding_end_date)
            self.log_transaction(self.symbol, 'put', self.expiry, self.long_put_strike, sell_quantity, 'sell', final_long_put_price)
            self.total_profits += ((final_long_put_price - initial_long_put_price) * sell_quantity * 100)
            current_date = holding_end_date + timedelta(days=1)

    def calculate_portfolio_value(self, historical_data, initial_long_put_price):
        self.total_profits = 0
        for index, row in historical_data.iterrows():
            self.current_price = row['Close']
            self.update_price(row.name)
            self.calculate_profit(initial_long_put_price)

    def log_transaction(self, symbol, contract_type, expiry, strike, quantity, action, price):
        self.transactions += 1
        if action == 'buy':
            self.holdings += quantity
            self.premium_paid += price * quantity * 100
            self.current_value -= price * quantity * 100
        elif action == 'sell':
            self.holdings -= quantity
            self.current_value += price * quantity * 100
        print(f"Transaction: {action}, Quantity: {quantity}, Holdings: {self.holdings}")

    @staticmethod
    def format_result(result):
        return (
            f"symbol: {result['symbol']}\n"
            f"period: {result['period']}\n"
            f"start_date: {result['start_date']}\n"
            f"end_date: {result['end_date']}\n"
            f"transactions: {result['transactions']}\n"
            f"holdings: {result['holdings']}\n"
            f"total profits: {result['total profits']}\n"
            f"current portfolio value: {result['current portfolio value']}"
        )

    @staticmethod
    def run_bear_put_spread_strategy(symbols, portfolio_size, risk_tolerance, contract_quantity, period, holding_period_days, sell_percentage):
        results = []
        total_profits = 0
        total_transactions = 0  
        total_holdings = 0
        final_portfolio_value = 0
        
        for symbol in symbols:
            bear_put = bearPutSpread(symbol, portfolio_size, risk_tolerance, contract_quantity)
            result = bear_put.simulate_portfolio(period, holding_period_days, sell_percentage)
            results.append(result)
            total_profits += result['total profits']
            total_transactions += result['transactions'] 
            total_holdings += result['holdings']
            final_portfolio_value += result['current portfolio value']
            
            formatted_result = bearPutSpread.format_result(result)
            print(f"Results for {symbol}:\n{formatted_result}\n")
        

        return (
            total_transactions,   
            symbols,
            period,               
            result['start_date'], 
            result['end_date'],   
            total_holdings,      
            total_profits,       

        ) 
        

long_call = longCall(
    symbol='AAPL', 
    portfolio_size=10000, 
    risk_tolerance=0.1, 
    contract_quantity=2  
)


long_call.execute_long_call_strategy()


result = long_call.simulate_portfolio(period=30, holding_period_days=30)
print("Long Call Strategy Result:", longCall.format_result(result))



bull_call_spread = bullCallSpread(
    symbol='AAPL', 
    portfolio_size=10000, 
    risk_tolerance=0.1, 
    contract_quantity=2 )


bull_call_spread.execute_bull_call_spread_strategy()


result = bull_call_spread.simulate_portfolio(period=30, holding_period_days=30)
print("Bull Call Spread Strategy Result:", bullCallSpread.format_result(result))


bear_put_spread = bearPutSpread(
    symbol='AAPL', 
    portfolio_size=10000, 
    risk_tolerance=0.1, 
    contract_quantity=2  
)

# Directly check if the current price is being set
print(f"Current Price Before Execution: {bear_put_spread.get_current_underlying_price()}")

bear_put_spread.execute_bear_put_spread_strategy()

result = bear_put_spread.simulate_portfolio(period=30, holding_period_days=30)
print("Bear Put Spread Strategy Result:", bearPutSpread.format_result(result))