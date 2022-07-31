import chemica.engine as chemica
from chemica.substance import Substance
from chemica.structure import Structure
from chempy import chemistry
from helpers import *
import PIL
from flask import Flask, render_template, request, redirect

import sys

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """ Simple Reaction Calculator """

    if request.method == "POST":
        A_reagent = request.form.get("A")
        B_reagent = request.form.get("B")

        # Make sure there is input
        if A_reagent is None or B_reagent is None:
            return apology("Missing Reagent", 401)

        # Solve for products
        try:
            solved = chemica.solve(A_reagent, B_reagent)
        except Exception:
            return apology("Invalid reagents", 401)
        # If there is an error
        if type(solved) == str:
            return apology(solved, 401)

        # Get the balanced equation and the reagent names by unpacking tuple
        # Why? balanced_eq has coef will reagents don't (except for dict values)
        balanced_equation, reagents = solved

        # Parse balanced equation
        # Get the fixed reagents
        fixed_reagents = balanced_equation.split("→")

        # Reactants
        fixed_A, fixed_B = fixed_reagents[0].split("+")
        # Products
        fixed_products = fixed_reagents[1]

        # Parse reagent names
        reactants, products = reagents
        reac_reagents = list(reactants.keys())
        prod_reagents = list(products.keys())
        # If it has more than 1 product, forcibly get an error 'message'
        if len(prod_reagents) > 1:
            prod_reagents = ["C4"]

        return render_template("predicted.html", A=fixed_A, B=fixed_B, prod=fixed_products, reac_reagents=reac_reagents, prod_reagents=prod_reagents)

    return render_template("predictor.html")


@app.route("/lewis", methods=["GET", "POST"])
def lewis():
    """ Generate Lewis Structure Procedurally """

    if request.method == "POST":
        compound = request.form.get("compound")

        # Make sure there is input
        if compound is None:
            return apology("Missing Compound", 401)

        return render_template("lewis.html", compound=compound)

    return render_template("lewis.html")


@app.route("/name", methods=["GET", "POST"])
def name():
    """ Name Compound Procedurally """

    if request.method == "POST":
        compound = request.form.get("compound")

        # Make sure there is input
        if compound is None:
            return apology("Missing Compound", 401)

        # Name compound
        try:
            compound_name = Substance.from_formula(compound).nomenclature
        except Exception:
            return apology("Invalid reagents", 401)

        return render_template("name.html", compound_name=compound_name)

    return render_template("name.html")


@app.route("/balance", methods=["GET", "POST"])
def balance():
    """ Name Compound Procedurally """

    if request.method == "POST":
        reactants = request.form.get("reactants")
        products = request.form.get("products")

        # Make sure there is input
        if reactants is None:
            return apology("Missing Reactants", 401)
        if products is None:
            return apology("Missing Products", 401)

        # Parse reagents
        reactants = reactants.split("+")
        products = products.split("+")

        # Balance reaction
        try:
            reac, prod = chemistry.balance_stoichiometry(reactants, products)
        except Exception:
            return apology("Invalid reagents", 401)

        balanced_equation = chemica.reaction_equation(reac, prod)

        return render_template("balance.html", balanced_equation=balanced_equation)

    return render_template("balance.html")


@app.route("/lewis_api/<formula>")
def lewis_api(formula):
    structure = Structure.from_formula(formula)
    return serve_pil_image(structure.lewis)
