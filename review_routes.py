from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from extensions import mysql
from datetime import datetime
from utils.auth_utils import login_required

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews')
def reviews():
    # Get all public reviews
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT r.*, u.username, t.destination 
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN trips t ON r.trip_id = t.id
        WHERE r.is_public = 1
        ORDER BY r.created_at DESC
    ''')
    reviews = cursor.fetchall()
    cursor.close()
    
    return render_template('reviews.html', reviews=reviews)

@review_bp.route('/trips/<int:trip_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(trip_id):
    # Check if trip exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM trips 
        WHERE id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    trip = cursor.fetchone()
    
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('trip.trips'))
    
    # Check if review already exists
    cursor.execute('''
        SELECT * FROM reviews 
        WHERE trip_id = %s AND user_id = %s
    ''', (trip_id, session['user_id']))
    existing_review = cursor.fetchone()
    
    if existing_review:
        flash('You have already reviewed this trip', 'info')
        return redirect(url_for('review.edit_review', review_id=existing_review['id']))
    
    if request.method == 'POST':
        # Get form data
        rating = request.form['rating']
        title = request.form['title']
        content = request.form['content']
        is_public = 'is_public' in request.form
        
        # Validate form data
        if not rating or not title or not content:
            flash('Please fill out all required fields', 'danger')
            return render_template('add_review.html', trip=trip)
        
        # Insert review into database
        cursor.execute('''
            INSERT INTO reviews (trip_id, user_id, rating, title, content, is_public) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (trip_id, session['user_id'], rating, title, content, is_public))
        mysql.connection.commit()
        cursor.close()
        
        flash('Review added successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=trip_id))
    
    return render_template('add_review.html', trip=trip)

@review_bp.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    # Get review details
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT r.*, t.destination 
        FROM reviews r
        JOIN trips t ON r.trip_id = t.id
        WHERE r.id = %s AND r.user_id = %s
    ''', (review_id, session['user_id']))
    review = cursor.fetchone()
    
    if not review:
        flash('Review not found', 'danger')
        return redirect(url_for('review.reviews'))
    
    if request.method == 'POST':
        # Get form data
        rating = request.form['rating']
        title = request.form['title']
        content = request.form['content']
        is_public = 'is_public' in request.form
        
        # Validate form data
        if not rating or not title or not content:
            flash('Please fill out all required fields', 'danger')
            return render_template('edit_review.html', review=review)
        
        # Update review in database
        cursor.execute('''
            UPDATE reviews 
            SET rating = %s, title = %s, content = %s, is_public = %s 
            WHERE id = %s
        ''', (rating, title, content, is_public, review_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Review updated successfully!', 'success')
        return redirect(url_for('trip.view_trip', trip_id=review['trip_id']))
    
    return render_template('edit_review.html', review=review)

@review_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    # Check if review exists and belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM reviews 
        WHERE id = %s AND user_id = %s
    ''', (review_id, session['user_id']))
    review = cursor.fetchone()
    
    if not review:
        flash('Review not found', 'danger')
        return redirect(url_for('review.reviews'))
    
    # Delete review
    cursor.execute('DELETE FROM reviews WHERE id = %s', (review_id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('trip.view_trip', trip_id=review['trip_id']))

@review_bp.route('/destinations/top-rated')
def top_rated_destinations():
    # Get top-rated destinations based on reviews
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT t.destination, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count
        FROM reviews r
        JOIN trips t ON r.trip_id = t.id
        GROUP BY t.destination
        HAVING review_count >= 3
        ORDER BY avg_rating DESC
        LIMIT 10
    ''')
    destinations = cursor.fetchall()
    cursor.close()
    
    return render_template('top_rated_destinations.html', destinations=destinations)

@review_bp.route('/reviews/helpful/<int:review_id>', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    # Check if review exists
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM reviews WHERE id = %s', (review_id,))
    review = cursor.fetchone()
    
    if not review:
        return jsonify({'success': False, 'message': 'Review not found'})
    
    # Check if user has already marked this review as helpful
    cursor.execute('''
        SELECT * FROM helpful_reviews 
        WHERE review_id = %s AND user_id = %s
    ''', (review_id, session['user_id']))
    existing = cursor.fetchone()
    
    if existing:
        # Remove helpful mark
        cursor.execute('''
            DELETE FROM helpful_reviews 
            WHERE review_id = %s AND user_id = %s
        ''', (review_id, session['user_id']))
        
        # Update helpful count
        cursor.execute('''
            UPDATE reviews 
            SET helpful_count = helpful_count - 1 
            WHERE id = %s
        ''', (review_id,))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'helpful': False, 'count': review['helpful_count'] - 1})
    else:
        # Add helpful mark
        cursor.execute('''
            INSERT INTO helpful_reviews (review_id, user_id) 
            VALUES (%s, %s)
        ''', (review_id, session['user_id']))
        
        # Update helpful count
        cursor.execute('''
            UPDATE reviews 
            SET helpful_count = helpful_count + 1 
            WHERE id = %s
        ''', (review_id,))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'helpful': True, 'count': review['helpful_count'] + 1})