from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Category(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    events     = db.relationship('Event', backref='category', lazy=True)

event_contacts = db.Table('event_contacts',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'), primary_key=True)
)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    contacts = db.relationship('Contact', secondary=event_contacts, backref='events')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
    contact = db.relationship('Contact', backref='invitations')

# Forms
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateTimeField('Date', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    location = StringField('Location')
    submit = SubmitField('Save Event')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    submit = SubmitField('Save Contact')

# Routes
@app.route('/')
def index():
    try:
        events = Event.query.order_by(Event.date.desc()).all()
        if not events:
            return render_template('landing.html')
        return render_template('index.html', events=events)
    except Exception as e:
        flash(f'Error loading events: {str(e)}', 'error')
        return render_template('index.html', events=[])

@app.route('/events/new', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        try:
            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=form.date.data,
                location=form.location.data
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('view_event', id=event.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'error')
    return render_template('event_form.html', form=form, title='Create Event')

@app.route('/events/<int:id>')
def view_event(id):
    try:
        event = Event.query.get_or_404(id)
        invitations = Invitation.query.filter_by(event_id=id).all()
        return render_template('event_detail.html', event=event, invitations=invitations)
    except Exception as e:
        flash(f'Error loading event: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/events/<int:id>/edit', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        try:
            form.populate_obj(event)
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('view_event', id=event.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'error')
    return render_template('event_form.html', form=form, title='Edit Event')

@app.route('/contacts')
def contacts():
    try:
        contacts = Contact.query.order_by(Contact.name).all()
        return render_template('contacts.html', contacts=contacts)
    except Exception as e:
        flash(f'Error loading contacts: {str(e)}', 'error')
        return render_template('contacts.html', contacts=[])

@app.route('/contacts/new', methods=['GET', 'POST'])
def create_contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            contact = Contact(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data
            )
            db.session.add(contact)
            db.session.commit()
            flash('Contact created successfully!', 'success')
            return redirect(url_for('contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating contact: {str(e)}', 'error')
    return render_template('contact_form.html', form=form, title='Create Contact')

@app.route('/api/contacts')
def api_contacts():
    try:
        contacts = Contact.query.order_by(Contact.name).all()
        return jsonify([{
            'id': contact.id,
            'name': contact.name,
            'email': contact.email
        } for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/events/<int:event_id>/invite', methods=['POST'])
def send_invitations(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        contact_ids = request.json.get('contact_ids', [])
        
        for contact_id in contact_ids:
            existing = Invitation.query.filter_by(event_id=event_id, contact_id=contact_id).first()
            if not existing:
                invitation = Invitation(event_id=event_id, contact_id=contact_id)
                db.session.add(invitation)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Invitations sent successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/invitations/<int:id>/respond', methods=['POST'])
def respond_invitation(id):
    try:
        invitation = Invitation.query.get_or_404(id)
        status = request.json.get('status')
        if status in ['accepted', 'declined']:
            invitation.status = status
            invitation.responded_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

def initialize_database():
    """Initialize database with tables and default data."""
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)
