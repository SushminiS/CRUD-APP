from flask import Flask,render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)

Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    person = db.Column(db.String(100), nullable=False)  # Name of the person
    completed = db.Column(db.Boolean, default=False)    # Completion status
    reschedule = db.Column(db.Boolean, default=False)   # Reschedule option
    scheduled_at = db.Column(db.DateTime, nullable=True) # Date and time selection
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Task {self.id}>'
    
with app.app_context():
        db.create_all()

#routes to webpage
#home page
@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        current_task = request.form['content']
        person = request.form['person']
        completed = 'completed' in request.form
        reschedule = 'reschedule' in request.form
        scheduled_at = request.form.get('scheduled_at')
        scheduled_at_dt = datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M') if scheduled_at else None

        new_task = MyTask(
            content=current_task,
            person=person,
            completed=completed,
            reschedule=reschedule,
            scheduled_at=scheduled_at_dt
        )
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
    else:
        tasks = MyTask.query.order_by(MyTask.created_at).all()

    return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    task = MyTask.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.person = request.form['person']
        task.completed = 'completed' in request.form
        task.reschedule = 'reschedule' in request.form
        scheduled_at = request.form.get('scheduled_at')
        task.scheduled_at = datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M') if scheduled_at else None

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Error: {e}"
    return render_template("edit.html", task=task)

@app.route("/complete/<int:id>", methods=['POST'])
def complete(id):
    task = MyTask.query.get_or_404(id)
    task.completed = True
    try:
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
