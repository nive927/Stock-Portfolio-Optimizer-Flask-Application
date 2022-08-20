from distutils.log import debug
from turtle import pos
from flask import Flask, request, render_template
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


@app.route("/")
def index():
    conn = sqlite3.connect('./datadb/database.db')
    conn.row_factory = sqlite3.Row
    with open("./datadb/schema.sql") as f:
        conn.executescript(f.read())
    cur = conn.cursor()

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                ('Second Post', 'Content for the second post')
                )

    posts = conn.execute('SELECT * FROM posts')
    
    for post in posts:
        print(tuple(post))

    conn.commit()
    conn.close()

    return render_template("index.html")

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
    app.run(host="0.0.0.0", port=8090, debug=True)
