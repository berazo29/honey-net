from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('bug', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT b.id, title, body, author_id, username'
        ' FROM bug b JOIN user u ON b.author_id = u.id'
        ' ORDER BY priority DESC'
    ).fetchall()

    return render_template('bug/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    severity_options = get_db().execute('SELECT * FROM priority').fetchall()
    priority_options = get_db().execute('SELECT * FROM severity').fetchall()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        priority = int(request.form['priority'])
        severity = int(request.form['severity'])
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bug (title, body, author_id, priority, severity)'
                'VALUES (?, ?, ?, ?, ?)',
                (title, body, g.user['id'], priority, severity)
            )
            bug_id = db.execute('SELECT id FROM bug WHERE id = (SELECT MAX(id) FROM bug)').fetchone()
            init_comment = "Initial report"

            db.execute(
                'INSERT INTO history (bug_id, author_id, description)'
                'VALUES (?, ?, ?)', (bug_id[0], g.user['id'], init_comment)
            )
            db.commit()
            return redirect(url_for('bug.index'))

    return render_template('bug/create.html', severity_options=severity_options, priority_options=priority_options)


def get_post(id, check_author=True):
    bug = get_db().execute(
        'SELECT b.id, title, body, author_id, username'
        ' FROM bug b JOIN user u ON b.author_id = u.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if bug is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and bug['author_id'] != g.user['id']:
        abort(403)

    return bug


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE bug SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            bug_id = db.execute('SELECT id FROM bug WHERE id = (SELECT MAX(id) FROM bug)').fetchone()
            description = "Edit report"
            db.execute(
                'INSERT INTO history (bug_id, author_id, description)'
                'VALUES (?, ?, ?)', (bug_id[0], g.user['id'], description)
            )
            db.commit()
            return redirect(url_for('bug.index'))

    return render_template('bug/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM history WHERE id = ?', (id,))
    db.execute('DELETE FROM bug WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('bug.index'))


@bp.route('/<int:id>/history', methods=('GET', 'POST'))
@login_required
def add_history(id):
    bug_history = get_db().execute(
        'SELECT b.id, b.title, b.body, h.description, h.date'
        ' FROM bug b JOIN history h ON b.id = h.bug_id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchall()
    for bug in bug_history:
        print('id: ', bug[0], 'title: ', bug[1])
        print('body: ', bug[2])
        print('description: ', bug[3])
        print('date: ', bug[4])
    return 'hello'
