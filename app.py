from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"


products = [
    {
        "id": 1,
        "name": "NVIDIA RTX 3090",
        "description": "High-end performance for gaming and AI workloads",
        "image": "",
        "price": 3600.00,
        "panel_class": "panel-primary"
    },
    {
        "id": 2,
        "name": "AMD Radeon RX 6800",
        "description": "Great performance for gaming and content creation",
        "image": "",
        "price": 7900.00,
        "panel_class": "panel-primary"
    },
    {
        "id": 3,
        "name": "NVIDIA RTX 3060",
        "description": "Affordable performance for gamers and streamers",
        "image": "",
        "price": 1650.00,
        "panel_class": "panel-primary"
    },
    {
        "id": 4,
        "name": "NVIDIA RTX 3080",
        "description": "Ultimate performance for high-end gaming.",
        "image": "",
        "price": 3500.00,
        "panel_class": "panel-primary"
    },
    {
        "id": 5,
        "name": "AMD Radeon RX 6780",
        "description": "Excellent choice for 1440p gaming",
        "image": "",
        "price": 2400.00,
        "panel_class": "panel-primary"
    }
]

#to render index
@app.route('/')
def index():
    return render_template('index.html', products=products)


@app.route('/add_to_cart/<int:product_id>') 
def add_to_cart(product_id):
    if 'cart' not in session: 
        session['cart'] = [] 

    product = next((item for item in products if item["id"] == product_id), None)

    if product:
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += 1
                flash(f'{product["name"]} quantity increased to {item["quantity"]}!')
                break
        else:
            product_copy = product.copy()
            product_copy['quantity'] = 1
            session['cart'].append(product_copy)
            flash(f'{product["name"]} added to cart!')

    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        flash('Product removed from cart!')

    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)  # to calculate total amount
    return render_template("cart.html", cart=cart_items, total_amount=total_amount)  # Pass total_amount to template


@app.route("/checkout")
def checkout():
    PAYMONGO_API_KEY = " " #put your own scret key form paymongo
    url = 'https://api.paymongo.com/v1/links'

    total_amount = sum(item['price'] * item['quantity'] for item in session.get('cart', []))

    amount_in_centavos = total_amount * 100
    payload = {
        "data": {
            "attributes": {
                "amount": int(amount_in_centavos),
                "description": "GPU Online Store Purchase",
                "remarks": "Thank you for your purchase!",
                "currency": "PHP",
                "redirect": {
                    "success": url_for('success', _external=True),
                    "failed": url_for('failed', _external=True)
                }
            }
        }
    }

    api_key_encoded = base64.b64encode(f"{PAYMONGO_API_KEY}:".encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key_encoded}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        print(response_data)

        payment_url = response_data['data']['attributes']['checkout_url']
        return redirect(payment_url)

    except requests.exceptions.RequestException as e:
        flash(f'Error with payment: {e}')
        return redirect(url_for('cart'))

    except KeyError:
        flash('Unexpected response structure from PayMongo')
        return redirect(url_for('cart'))

@app.route('/success')
def success():
    flash("Payment successful!")
    session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/failed')
def failed():
    flash("Payment failed. Please try again.")
    return redirect(url_for('cart'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        flash(f'Thank you for signing up for our deals, {email}!')
        return redirect(url_for("index"))
    else:
        flash('Invalid email address.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
