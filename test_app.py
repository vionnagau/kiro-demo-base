import pytest
from datetime import datetime
from app import db, Event, Contact, Invitation

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Events' in response.data

def test_create_event(client):
    response = client.post('/events/new', data={
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-01 18:00:00',
        'location': 'Test Location',
        'csrf_token': 'test'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_create_contact(client):
    response = client.post('/contacts/new', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '123-456-7890',
        'csrf_token': 'test'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_event_model():
    event = Event(title='Test', date=datetime.now())
    assert event.title == 'Test'

def test_contact_model():
    contact = Contact(name='Test', email='test@example.com')
    assert contact.name == 'Test'
