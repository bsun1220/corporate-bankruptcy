import urllib 
import json
import numpy as np
import pandas as pd

def api_call(ticker, module, category):
    response = urllib.request.urlopen(f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules={module}")
    content = response.read()
    data = json.loads(content.decode('utf8'))['quoteSummary']['result'][0][module][category]
    
    return data 

def get_altman_data(ticker):
    bs = api_call(ticker, "balanceSheetHistory", "balanceSheetStatements")[0]
    
    total_assets = bs["totalAssets"]["raw"]
    total_liab = bs["totalLiab"]["raw"]
    retained_earnings = bs["retainedEarnings"]["raw"]
    
    try:
        current_assets = bs["totalCurrentAssets"]["raw"]
    except:
        current_assets = 0
    
    try:
        current_liab = bs["totalCurrentLiabilities"]["raw"]
    except:
        current_liab = 0
    
    working_capital = current_assets - current_liab
    
    data = {}
    data["total_assets"] = total_assets
    data["total_liab"] = total_liab
    data["retained_earnings"] = retained_earnings
    data["working_capital"] = working_capital
    
    inst = api_call(ticker, "incomeStatementHistory", "incomeStatementHistory")[0]
    revenue = inst["totalRevenue"]["raw"]
    pretax_income = inst["incomeBeforeTax"]["raw"]
    
    try:
        interest_expense = inst["interestExpense"]["raw"]
    except:
        interest_expense = 0
    
    income = pretax_income + interest_expense
    data["revenue"] = revenue
    data["pretaxinterest_income"] = income
    
    price = api_call(ticker, "price", "marketCap")
    try:
        mkt_cap = price["raw"]
    except:
        mkt_cap = 0
    
    data["mkt_cap"] = mkt_cap
    
    return data

def altman_calc(ticker):
    data = get_altman_data(ticker)
    A = data["working_capital"]/data["total_assets"]
    B = data["retained_earnings"]/data["total_assets"]
    C = data["pretaxinterest_income"]/data["total_assets"]
    D = data["mkt_cap"]/data["total_liab"]
    E = data["revenue"]/data["total_assets"]
    
    return 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + E
    
    