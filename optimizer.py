import pandas as pd
import numpy as np
import yfinance as yf


def download_prices(tickers):
    df = yf.download(tickers.split(), '2020-1-1')['Adj Close']
    df = df[-253:]
    return df

def calculate_variables(df):
    daily_ret = df.pct_change()
    NUM_DAYS = daily_ret.count()
    annual_ret = daily_ret.mean() * NUM_DAYS
    cov_daily = daily_ret.cov()
    cov_annual = cov_daily * NUM_DAYS
    return annual_ret, cov_annual

def calculate_eff_frontier(df, annual_ret, cov_annual):
    NUM_ASSETS = len(df.columns)
    NUM_PORTFOLIOS = 50000
    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    stock_weights = []
    sharpe_ratio = []
    
    # populate the empty lists with each portfolios returns,risk and weights
    for portfolio in range(NUM_PORTFOLIOS):
        weights = np.random.random(NUM_ASSETS)
        weights /= np.sum(weights)
        returns = np.dot(weights, annual_ret)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)
    
    # Create a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns, 'Volatility': port_volatility,'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    assets = df.columns

    for counter,asset in enumerate(assets):
        portfolio[asset+' Weight'] = [Weight[counter] for Weight in stock_weights]
    # make a nice dataframe of the extended dictionary
    df_portfolio = pd.DataFrame(portfolio)   
    return df_portfolio

def optimize(tickers):
    df = download_prices(tickers)
    annual_ret, cov_annual = calculate_variables(df)
    df_portfolio = calculate_eff_frontier(df, annual_ret, cov_annual)
    # find min Volatility & max sharpe values in the dataframe 
    is_min_vol = df_portfolio['Volatility'] ==  df_portfolio['Volatility'].min()
    is_max_sharpe = df_portfolio['Sharpe Ratio'] == df_portfolio['Sharpe Ratio'].max()
    # use the min, max values to locate and create the two special portfolios
    max_sharpe_port = df_portfolio.loc[is_max_sharpe].to_json()
    min_vol_port = df_portfolio.loc[is_min_vol].to_json()
    return min_vol_port, max_sharpe_port
