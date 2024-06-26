from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('packages.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rowid,* FROM packages')
    packages = cursor.fetchall()
    conn.close()
    return render_template('index.html', packages=packages)

@app.route('/add', methods=('POST',))
def add():
    name = request.form['name']
    version = request.form['version']
    release = request.form['release']
    repo = request.form['repo']
    build_status = request.form['build_status']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO packages (name, version, release, repo, build_status) VALUES (?, ?, ?, ?, ?)',
                   (name, version, release, repo, build_status))
    except:
        pass
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<name>', methods=('POST',))
def edit(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM packages WHERE name = ?', (name,))
    package = cursor.fetchone()

    version = request.form['version']
    release = request.form['release']
    repo = request.form['repo']
    build_status = request.form['build_status']

    cursor.execute('UPDATE packages SET version = ?, release = ?, repo = ?, build_status = ? WHERE name = ?',
                   (version, release, repo, build_status, name))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<name>', methods=('POST',))
def delete(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM packages WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<name>', methods=('POST',))
def update(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM packages WHERE name = ?', (name,))
    package = cursor.fetchone()

    if package:
        build_status = request.form['build_status']
        cursor.execute('UPDATE packages SET build_status = ? WHERE name = ?',
                       (build_status, name))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

