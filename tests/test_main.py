import os
import pytest

#this line needds to be set before the "APP" import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app, db
from models import User

@pytest.fixture
def client():
    client = app.test_client()

    cleanup()

    db.create_all()

    yield client


def cleanup():
#clean up the database
    db.drop_all()


def test_index_not_logged_in(client):
    response = client.get("/")
    assert b'username' in response.data
    assert response.status_code == 200


def test_index_logged_in(client):
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)
    response = client.get("/")
    assert b'Enter your guess' in response.data


def test_result_correct(client):
    #create a user
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True) 
    
    #get the first user object from the database
    user = db.query(User).first()

    #set the secret number to 8, so that you can maake a success "guess" in the test
    user.secret_number = 8
    user.save()

    response = client.post("/result", data={"guess": 8}) #enter the correct guess
    assert b'Correct! The secret number is 8' in response.data


def test_result_incorrect_try_bigger(client):
    #create a user
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com", 
                                "user-password": "password123"}, follow_redirects=True)
    
    #get user object from the database
    user = db.query(User).first()

    user.secret_number = 8
    user.save()

    response = client.post("/result", data={"guess": 5}) #the wrong guess -- too small
    assert b'Your guess is incorrect, try something bigger.' in response.data


def test_result_incorrect_try_smaller(client):
    #create a user
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)
    
    #get user object from the database
    user = db.query(User).first()

    user.secret_number = 8
    user.save()

    response = client.post("/result", data={"guess": 9}) #the wrong guess -- too big
    assert b'Your guess is incorrect, try something smaller.' in response.data


def test_profile(client):
    #create a user
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)
    
    response = client.get("/profile")
    assert b'Test User' in response.data


def test_profile_edit(client):
    ##create a user
    client.post("/login", data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    #GET
    response = client.get("/profile/edit")
    assert b'Edit your profile' in response.data

    #POST
    response = client.post('/profile/edit', data={"profile-name": "Test User 2",
                                                  "profile-email": "test2@user.com"}, follow_redirects=True)
    
    assert b'Test User 2' in response.data
    assert b'test2@user.com' in response.data


def test_profile_delete(client):
    # create a user
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    # GET
    response = client.get('/profile/delete')
    assert b'Delete your profile' in response.data

    # POST
    response = client.post('/profile/delete', follow_redirects=True)
    assert b'name' in response.data  # redirected back to the index site


def test_all_users(client):
    response = client.get('/users')
    assert b'<h3>Users</h3>' in response.data
    assert b'Test User' not in response.data  # Test User is not yet created

    # create a new user
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/users')
    assert b'<h3>Users</h3>' in response.data
    assert b'Test User' in response.data


def test_user_details(client):
    # create a new user
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    # get user object from the database
    user = db.query(User).first()

    response = client.get('/user/{}'.format(user.id))
    assert b'test@user.com' in response.data
    assert b'Test User' in response.data

