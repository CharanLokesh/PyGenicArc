@app.route("/update_task/<int:id>", methods=["GET", "POST"])
def update_task(id):
    task = Todo.query.get_or_404(id)
    print(task.id)
    if not task:
        return jsonify({"message": "task not found"}), 404
    if request.method == "POST":
        task.title = request.form["title"]
        task.task = request.form["task"]
        task.due = request.form["due"]
        try:
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            print(e)
            db.session.rollback()
            return "there is an issue while updating the record"
    return render_template("update.html", task=task)


# Two blank lines required before top-level function / decorator (E302)
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


# Two blank lines required after top-level function definition (E305)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)