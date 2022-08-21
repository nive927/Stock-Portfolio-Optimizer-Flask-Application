from distutils.log import debug
from sys import flags
from turtle import pos
from flask import Flask, request, render_template, url_for, redirect, flash, get_flashed_messages
from flask_restful import Resource, Api
from flask_cors import CORS
import optimizer

import sqlite3
import pymysql

def create_app():
	app = Flask(__name__)
	return app

app = create_app()
api = Api(app)
CORS(app)

TICKERS = {"Bonds": ["^FVX", "^IRX", "^TNX", "^TYX"],
"Commodities": ["CL=F", "GC=F", "KC=F"],
"Cryptos": ["BNB-USD", "BTC-USD", "ETH-USD", "USDC-USD", "USDT-USD"],
"Indices": ["^GDAXI", "^GSPC", "^N225", "^RUT"],
"Stocks": ["AAPL", "AMZN", "F", "GOOGL", "META", "NFLX", "TSLA"]}

BONDS = TICKERS["Bonds"] + TICKERS["Commodities"]
STOCKS = TICKERS["Cryptos"] + TICKERS["Indices"] + TICKERS["Stocks"]

conn = sqlite3.connect('./datadb/database.db')
conn.row_factory = sqlite3.Row
with open("./datadb/schema.sql") as f:
    conn.executescript(f.read())
conn.close()

def set_portfolio_type(tickers: list):

    percentage_bonds = (len(list(filter(lambda ele: ele in BONDS, tickers))) / len(tickers)) * 100
    
    portfolio_type = "NA"

    if 60 <= percentage_bonds <= 100:
        portfolio_type = "Conservative"
    elif 35 <= percentage_bonds < 60:
        portfolio_type = "Balanced"
    elif 5 <= percentage_bonds < 35:
        portfolio_type = "Growth"
    elif 0 <= percentage_bonds <= 5:
        portfolio_type = "Aggressive"
    else:
        portfolio_type = "NA"

    print(f"\n\n{tickers}: {portfolio_type}\n\n")

    return portfolio_type

@app.route("/")
def index():
    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    data = cur.execute('SELECT * FROM portfolios')
    
    portfolios = list()

    for portfolio in data:
        print(dict(portfolio))
        portfolios.append(dict(portfolio))

    conn.commit()

    return render_template("index.html", portfolios=portfolios)

@app.route("/add_portfolio")
def add_portfolio():
    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    title = request.args.get("title")
    assets = request.args.get("assets")
    portfolio_type = set_portfolio_type(assets.split())

    cur.execute("INSERT INTO portfolios (title, assets, portfolio_type) VALUES (?, ?, ?)",
            (title, assets, portfolio_type))
    conn.commit()

    flash("Portfolio added successfully!")
    return redirect(url_for("index"))

@app.route("/edit_portfolio/<id>")
def edit_portfolio(id):
    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM portfolios WHERE id={id}")
    data = cur.fetchall()
    cur.close()
    print(f"Edit Record {id}: {dict(data[0])}")

    return render_template("edit.html", portfolio=dict(data[0]))

@app.route("/update_portfolio/<id>")
def update_portfolio(id):
    title = request.args.get("title")
    assets = request.args.get("assets")
    portfolio_type = set_portfolio_type(assets.split())

    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print(f"Update: {title} {assets} {portfolio_type}")

    cur.execute("UPDATE portfolios SET title=?, assets=?, portfolio_type=? WHERE id=?", (str(title), str(assets), str(portfolio_type), int(id)))
    flash("Portfolio update successfully!")
    
    conn.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route("/delete_portfolio/<string:id>")
def delete_portfolio(id):
    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('DELETE FROM portfolios WHERE id = {0}'.format(id))
    conn.commit()
    cur.close()

    flash("Portfolio deleted successfully!")
    return redirect(url_for("index"))


@app.route("/portfolio_optimizer")
def portfolio_optimizer():
    #ticker_list = "AAPL TSLA"
    data = dict()
    if request.args.get("tickers") and len(request.args.get("tickers").split()) >= 2:
        ticker_list = request.args.get("tickers")
        app.logger.info(ticker_list.split())
        minRisk, maxReturn = optimizer.optimize(ticker_list)
        data["minRisk"] = minRisk
        data["maxReturn"] = maxReturn
    else:
        data["Error"] = "No portfolio provided"
    app.logger.info(data)
    return render_template("portfolio_optimizer.html", data=data)

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8090)
    app.secret_key = 'nive'
    app.run(host="0.0.0.0", port=8090, debug=True)
