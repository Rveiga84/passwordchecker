from flask import Flask, render_template, request, jsonify
import requests
import hashlib
import os  

app = Flask(__name__)

@app.route('/')
def home():
        return render_template('index.html')

def request_api_data(query_char):
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f'Error fetching: {res.status_code}, check the API and try again')
    return res

def get_password_leaks_count(hashes, hash_to_check):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == hash_to_check:
            return int(count)
    return 0

def pwned_api_check(password):
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_char, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(first5_char)
    return get_password_leaks_count(response, tail)

@app.route('/check', methods=['POST'])
def check_password():
    data = request.json
    password = data['password']
    count = pwned_api_check(password)
    if count:
        return jsonify({'message': f'{password} was found {count} times... you should probably change your password'})
    else:
        return jsonify({'message': f'{password} was NOT found. Carry on!'})

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
