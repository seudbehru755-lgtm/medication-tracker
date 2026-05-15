from cs50 import SQL
from flask import Flask, render_template, request, redirect

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///medication.db")



# HOME PAGE

@app.route("/")
def index():

    medications = db.execute( "SELECT * FROM medications ORDER BY time")

    return render_template("index.html", medications=medications)



# ADD MEDICATION

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form.get("name")
        dosage = request.form.get("dosage")
        time = request.form.get("time")

        # Validation
        if not name:
            return "Missing medication name"

        if not dosage:
            return "Missing dosage"

        if not time:
            return "Missing time"

        db.execute( """ INSERT INTO medications (name, dosage, time) VALUES (?, ?, ?) """, name, dosage, time)

        return redirect("/")

    return render_template("add.html")



# EDIT MEDICATION
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    medication = db.execute(
        "SELECT * FROM medications WHERE id = ?",
        id
    )

    if len(medication) != 1:
        return "Medication not found"

    if request.method == "POST":

        name = request.form.get("name")
        dosage = request.form.get("dosage")
        time = request.form.get("time")
        status = request.form.get("status")

        db.execute( """ UPDATE medications SET name = ?, dosage = ?, time = ?, status = ? WHERE id = ? """, name, dosage, time, status, id )

        return redirect("/")

    return render_template( "edit.html", medication=medication[0])



# DELETE MEDICATION
@app.route("/delete/<int:id>")
def delete(id):

    db.execute( "DELETE FROM medications WHERE id = ?", id )
    return redirect("/")



# MARK MEDICATION AS TAKEN
@app.route("/taken/<int:id>")
def taken(id):

    medication = db.execute( "SELECT * FROM medications WHERE id = ?", id)

    if len(medication) != 1:
        return "Medication not found"

    # Update status
    db.execute(""" UPDATE medications SET status = 'Taken' WHERE id = ? """, id)

    # Save to history
    db.execute( """ INSERT INTO history (medication_id) VALUES (?, ?) """, id)
    return redirect("/")

# HISTORY PAGE
@app.route("/history")
def history():

    history = db.execute( "SELECT medications.name, history.taken_at FROM history JOIN medications ON history.medication_id = medications.id ORDER BY taken_at DESC")
    return render_template( "history.html", history=history)



# RESET STATUS
@app.route("/reset/<int:id>")
def reset(id):

    db.execute( """ UPDATE medications SET status = 'Pending' WHERE id = ? """, id )
    return redirect("/")
