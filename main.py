from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo  = db.Column(db.String(150), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Todo({self.todo}, {self.is_completed})"

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def index():
    db_todos = Todos.query.order_by(Todos.id.asc())
    return render_template('index.html', todos=db_todos)

@app.route('/home/new', methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        todo_text = request.form['todo']
        todo = Todos(todo=todo_text)
        db.session.add(todo)
        db.session.commit()
        flash('Your todo has been added to todo list successfully', 'success')
    return redirect(url_for('index'))

@app.route('/home/<int:todo_id>/delete')
def delete(todo_id):
    todo = Todos.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Your todo has been successfully deleted', 'success')
    return redirect(url_for('index'))
    
@app.route('/home/<int:todo_id>/toggle')
def toggle_completed(todo_id):
    todo = Todos.query.get_or_404(todo_id)
    todo.is_completed = not todo.is_completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/home/<int:todo_id>/edit', methods=['POST', 'GET'])
def edit_todo(todo_id):
    todo = Todos.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo_text = request.form['todo']
        todo.todo = todo_text
        db.session.commit()
        flash('Your todo has been updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', todo_id=todo_id, todo=todo)

@app.route('/home/delete_completed', methods=['GET'])
def delete_completed():
    todos = Todos.query.all()
    flag = False
    for todo in todos:
        if todo.is_completed:
            flag = True
            db.session.delete(todo)
    db.session.commit()
    if len(Todos.query.all()) != 0 and flag:
        flash('Marked items has been removed successfully', 'success')
    return redirect(url_for('index'))

@app.route('/home/delete_all', methods=['GET'])
def delete_all():
    length = len(Todos.query.all())
    db.session.query(Todos).delete()
    db.session.commit()
    if length != 0:
        flash('All items has been removed successfully', 'success')
    return redirect(url_for('index'))

def toggle_all_todos():
    todos = Todos.query.all()
    length = len(todos)
    count = 0
    for todo in todos:
        if todo.is_completed:
            count += 1
    if count == length:
        Todos.query.update({"is_completed": False})
    else:
        Todos.query.update({"is_completed": True})
    db.session.commit()
        

@app.route('/home/toggle_all', methods=['GET'])
def toggle_all():
    toggle_all_todos()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)