import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Load predefined tables (severity, priority)
    load_bug_options(db)


def load_bug_options(db):

    severity = ['non-critical', 'critical']
    priority = ['non-critical', 'critical']
    for item in severity:
        db.execute('INSERT INTO priority (title) VALUES (?)', (item,))
    for item in priority:
        db.execute('INSERT INTO severity (title) VALUES (?)', (item,))
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    click.echo('Loading predefined tables')
    # load_bug_options()
    click.echo('Ready!')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)