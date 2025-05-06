from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'V@r$ha#123'
app.config['MYSQL_DB'] = 'login'

mysql = MySQL(app)

# Navigation or landing page
@app.route('/')
def nav():
    return render_template('navigatereg.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

# Upload product image
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files.get('product_image')
        if not file or file.filename == '':
            return 'No file selected'

        description = request.form.get('product_description')
        price = request.form.get('product_price')
        filename = file.filename
        img_data = file.read()

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO images (description, image_name, image_data, price)
                VALUES (%s, %s, %s, %s)
            """, (description, filename, img_data, price))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error uploading product: {e}'

    return render_template('upload.html')

# Homepage displaying images
@app.route('/index')
def index():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id, description, image_name, price FROM images")
        images = cur.fetchall()
        cur.close()
        return render_template('index.html', images=images)
    except Exception as e:
        return f'Error fetching images: {e}'

# Serve image from DB
@app.route('/image/<int:image_id>')
def get_image(image_id):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT image_name, image_data FROM images WHERE id = %s", (image_id,))
        image = cur.fetchone()
        cur.close()
        if image:
            ext = image['image_name'].rsplit('.', 1)[-1].lower()
            return send_file(io.BytesIO(image['image_data']), mimetype=f'image/{ext}')
        return 'Image not found', 404
    except Exception as e:
        return f'Error fetching image: {e}', 500

# Other routes
@app.route('/handicrafts')
def handicrafts(): return render_template('handicrafts.html')

@app.route('/textiles')
def textiles(): return render_template('textiles.html')

@app.route('/jewellery')
def jewellery(): return render_template('jewellery.html')

@app.route('/pottery')
def pottery(): return render_template('pottery.html')

@app.route('/culture')
def culture(): return render_template('culture.html')

@app.route('/natural_oils')
def natural_oils(): return render_template('natural_oils.html')

@app.route('/herbal_soaps')
def herbal_soaps(): return render_template('herbal_soaps.html')

@app.route('/ayurvedic_products')
def ayurvedic_products(): return render_template('ayurvedic_products.html')

@app.route('/dishes')
def dishes(): return render_template('dishes.html')

if __name__ == '__main__':
    app.run(debug=True)
