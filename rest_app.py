from distutils.log import debug
from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
import optimizer

def create_app():
	app = Flask(__name__)
	return app

app = create_app()
api = Api(app)
CORS(app)

@app.route("/")
def index():
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
