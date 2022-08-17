from distutils.log import debug
from flask import Flask, request, render_template, Response
from flask_restful import Resource, Api
from flask_cors import CORS
import optimizer
import pandas as pd

def create_app():
	app = Flask(__name__)
	return app

app = create_app()
api = Api(app)
CORS(app)

class portfolio(Resource):
    def get(self):
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
        return data

api.add_resource(portfolio, '/api/portfolio')

@app.route("/")
def index():
    # return """<h2 style='color:red;background-color:blue'>Portfolio Optimizer Rest API using Flask</h2>
    # <p>Pass ticker symbols to tickers variable in URL string e.g. :</p>
    # <a href='/api/portfolio?tickers=AAPL TSLA'>View Min Risk and Max Return Portfolios for FB and GOOGL</a>"""

    return render_template("index.html")

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8090)
    app.run(host="0.0.0.0", port=8090, debug=True)
