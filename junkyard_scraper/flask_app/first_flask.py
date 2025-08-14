from flask import Flask, request, render_template, jsonify
from markupsafe import escape
from lkq import LKQSearch
from jup import JupSearch

app = Flask(__name__)

@app.route("/")
def hellow_jack():
	return render_template('index.html')

@app.route("/search", methods=["POST"])
def search_yards():
	if request.method == "POST":
		results = []
		search_str = request.json['search_str']
		lkq_results = LKQSearch(search_str).get_data()
		jup_results = JupSearch(search_str).get_data()
		results.append(jup_results)
		results.append(lkq_results)
		return jsonify(results)

