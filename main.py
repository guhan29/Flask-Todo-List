from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('MYSECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    todo  = db.Column(db.String(150), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Todo({self.todo}, {self.is_completed})"

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def index():
    db_todos = Todo.query.order_by(Todo.id.asc())
    return render_template('index.html', todos=db_todos)

@app.route('/home/new', methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        todo_text = request.form['todo']
        todo = Todo(todo=todo_text)
        db.session.add(todo)
        db.session.commit()
        flash('Your todo has been added to todo list successfully', 'success')
    return redirect(url_for('index'))

@app.route('/home/<int:todo_id>/delete')
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Your todo has been successfully deleted', 'success')
    return redirect(url_for('index'))
    
@app.route('/home/<int:todo_id>/toggle')
def toggle_completed(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.is_completed = not todo.is_completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/home/<int:todo_id>/edit', methods=['POST', 'GET'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo_text = request.form['todo']
        todo.todo = todo_text
        db.session.commit()
        flash('Your todo has been updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', todo_id=todo_id, todo=todo)

@app.route('/home/delete_completed', methods=['GET'])
def delete_completed():
    todos = Todo.query.all()
    flag = False
    for todo in todos:
        if todo.is_completed:
            flag = True
            db.session.delete(todo)
    db.session.commit()
    if len(Todo.query.all()) != 0 and flag:
        flash('Marked items has been removed successfully', 'success')
    return redirect(url_for('index'))

@app.route('/home/delete_all', methods=['GET'])
def delete_all():
    length = len(Todo.query.all())
    db.session.query(Todo).delete()
    db.session.commit()
    if length != 0:
        flash('All items has been removed successfully', 'success')
    return redirect(url_for('index'))

def toggle_all_todos():
    todos = Todo.query.all()
    length = len(todos)
    count = 0
    for todo in todos:
        if todo.is_completed:
            count += 1
    if count == length:
        Todo.query.update({"is_completed": False})
    else:
        Todo.query.update({"is_completed": True})
    db.session.commit()
        

@app.route('/home/toggle_all', methods=['GET'])
def toggle_all():
    toggle_all_todos()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)