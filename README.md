# Options-Trading-Center

I wanted to make a tool to allow people with very little financial experience to learn
about options and how they trade. The project has 2 main components, a research tool 
and a trading simulator. The trading simulator takes user input variables i.e.
companies, risk tolerance, portfolio size etc and determines how that specific trategy
(there are 3, explained below) would have performed over a given period. The other 
component is the graphs for the options greeks, the user inputs the stock and time duration
and chooses which greek they want to display and the graph appears with plotted points the 
user click on. 

Long Call Strategy: A long call strategy involves buying a call option with the expectation that the underlying asset's price 
will rise above the strike price before expiration, allowing for potential unlimited profit with limited risk (the premium paid). 
This strategy is typically used by traders who are bullish on the asset.

Bull Call Spread Strategy: The bull call spread strategy involves buying a call option at a lower 
strike price and simultaneously selling a call option at a higher strike price, both with the same
 expiration date. This strategy limits both potential profit and risk, making it a conservative bullish strategy.

Bear Put Spread Strategy: A bear put spread strategy involves buying a put option at a higher strike price and
simultaneously selling a put option at a lower strike price, with both options having the same expiration date. 
This strategy is used when there's anticipation of moderate decline in the underlying asset's price, offering limited profit and reduced risk.

Delta: Delta measures the sensitivity of an option's price to a $1 change in the underlying asset's price, indicating how much the option's price is expected to move.

Gamma: Gamma measures the rate of change of delta with respect to changes in the underlying asset's price, indicating the stability of delta over time.

Theta: Theta represents the rate at which an option's price declines as it approaches its expiration date, quantifying the time decay of the option.

Vega: Vega measures the sensitivity of an option's price to changes in the volatility of the underlying asset, indicating how much the option's price is expected to change with a 1% change in implied volatility.

Rho: Rho measures the sensitivity of an option's price to changes in interest rates, showing how much the option's price is expected to change with a 1% change in interest rates.
