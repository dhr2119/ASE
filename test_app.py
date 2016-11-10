# content of test_sample.py
import pytest

'''Test various get methods on app routes'''
def test_get_home_OK(client):
	assert client.get('/').status_code == 200

def test_get_signup_OK(client):
	assert client.get('/signup').status_code == 200

def test_get_view_account_redirect(client):
	assert client.get('/view_current_account').status_code == 302

def test_get_add_account_redirect(client):
	assert client.get('/add_bank_account').status_code == 302



'''Login post tests'''
def test_post_login_bad_request(client):
	assert client.post('/login').status_code == 400

def test_bad_login(client):
	assert client.post('/login', data=dict(usr = 'nelly', pwd = 'dog')).status_code == 302
	assert client.get('/view_current_account').status_code == 302

def test_good_login(client):
	assert client.post('/login', data=dict(usr = 'daniel', pwd = 'hi')).status_code == 302
	assert client.get('/view_current_account').status_code == 200



'''Login empty fields tests'''
def test_login_empty_usr(client):
	assert client.post('/login', data=dict(usr = '', pwd = 'themostsecure')).status_code == 302
	assert client.get('/view_current_account').status_code == 302

def test_login_empty_pass(client):
	assert client.post('/login', data=dict(usr = 'daniel', pwd = '')).status_code == 302
	assert client.get('/view_current_account').status_code == 302

def test_login_empty(client):
	assert client.post('/login', data=dict(usr = '', pwd = '')).status_code == 302
	assert client.get('/view_current_account').status_code == 302


'''Signup empty bad request test'''
def test_signup_empty_bad_request(client):
	assert client.post('/signup', data=dict(usr = '', pwd = '')).status_code == 400
	assert client.get('/view_current_account').status_code == 302