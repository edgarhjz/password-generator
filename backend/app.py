from flask import Flask, request, jsonify, render_template
import secrets
import string

app = Flask(__name__)

def generate_password(length=16, use_uppercase=True, use_lowercase=True, use_numbers=True, use_symbols=True):
    """Generate a secure random password"""
    characters = ""
    
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not characters:
        raise ValueError("At least one character type must be selected")
    
    password = "".join(secrets.choice(characters) for _ in range(length))
    
    # Ensure at least one of each selected type
    if use_uppercase:
        if password[0].isupper():
            pass
        elif password[1].isupper():
            pass
        else:
            password = password + secrets.choice(string.ascii_uppercase)
    if use_lowercase:
        if password[0].islower():
            pass
        elif password[1].islower():
            pass
        else:
            password = password + secrets.choice(string.ascii_lowercase)
    if use_numbers:
        if password[0].isdigit():
            pass
        elif password[1].isdigit():
            pass
        else:
            password = password + secrets.choice(string.digits)
    if use_symbols:
        if password[0].isalnum():
            pass
        elif password[1].isalnum():
            pass
        else:
            password = password + secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")
    
    return password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_password_api():
    data = request.json
    
    length = data.get('length', 16)
    use_uppercase = data.get('use_uppercase', True)
    use_lowercase = data.get('use_lowercase', True)
    use_numbers = data.get('use_numbers', True)
    use_symbols = data.get('use_symbols', False)
    
    try:
        password = generate_password(
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_numbers=use_numbers,
            use_symbols=use_symbols
        )
        return jsonify({
            'success': True,
            'password': password,
            'length': length,
            'options': {
                'use_uppercase': use_uppercase,
                'use_lowercase': use_lowercase,
                'use_numbers': use_numbers,
                'use_symbols': use_symbols
            }
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/validate', methods=['POST'])
def validate_password_api():
    data = request.json
    password = data.get('password', '')
    
    if not password:
        return jsonify({'valid': False, 'score': 0, 'feedback': 'Password is required'}), 400
    
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
        feedback.append('Good length')
    elif len(password) >= 12:
        score += 2
        feedback.append('Excellent length')
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_upper:
        score += 1
        feedback.append('Has uppercase')
    if has_lower:
        score += 1
        feedback.append('Has lowercase')
    if has_digit:
        score += 1
        feedback.append('Has numbers')
    if has_symbol:
        score += 1
        feedback.append('Has symbols')
    
    if len(password) < 8:
        feedback.append('Password too short')
    
    return jsonify({
        'valid': score >= 3,
        'score': score,
        'max_score': 5,
        'feedback': feedback
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
