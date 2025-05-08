from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re
from extensions import mysql, bcrypt
from utils.auth_utils import login_required

auth_bp = Blueprint('auth', __name__)

# User Registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('Please fill out all fields', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Email validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user:
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert user into database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                      (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# User Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        
        # Validate form data
        if not email or not password:
            flash('Please fill out all fields', 'danger')
            return render_template('login.html')
        
        # Check if user exists
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
        
        # Check password
        if bcrypt.check_password_hash(user['password'], password):
            # Create session
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

# User Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# User Profile
@auth_bp.route('/profile')
def profile():
    if 'logged_in' not in session:
        flash('Please log in to view your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    
    return render_template('profile.html', user=user)

# Update Profile
@auth_bp.route('/profile/update', methods=['GET', 'POST'])
def update_profile():
    if 'logged_in' not in session:
        flash('Please log in to update your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        
        # Validate form data
        if not username or not email:
            flash('Please fill out all fields', 'danger')
            return redirect(url_for('auth.update_profile'))
        
        # Email validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('auth.update_profile'))
        
        # Update user in database
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET username = %s, email = %s WHERE id = %s', 
                      (username, email, session['user_id']))
        mysql.connection.commit()
        cursor.close()
        
        # Update session
        session['username'] = username
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    
    return render_template('update_profile.html', user=user)