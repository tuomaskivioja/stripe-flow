#! /usr/bin/env python3.6

"""
server.py
Stripe Sample.
Python 3.6 or newer required.
"""
import json
import os
from flask import Flask, redirect, request, send_from_directory, render_template, request, Response, jsonify
from flask_cors import CORS

import stripe

# This is your test secret API key.
stripe.api_key = 'CHANGE'

app = Flask(__name__,
            static_url_path='',
            static_folder='public')
CORS(app)

YOUR_DOMAIN = 'http://localhost:4242'

endpoint_secret = 'CHANGE'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        print(data)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'CHANGE',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '?success=true',
            cancel_url=YOUR_DOMAIN + '?canceled=true',
            metadata= {
                "user_email": data['email'],
                "user_id": data['id'],
            }
        )
    except Exception as e:
        return str(e)

    return jsonify({'url': checkout_session['url']})


@app.route("/webhook", methods=["POST"])
def webhook_received():
    request_data = json.loads(request.data)
    signature = request.headers.get("stripe-signature")

    # Verify webhook signature and extract the event.
    # See https://stripe.com/docs/webhooks/signatures for more information.
    try:
        event = stripe.Webhook.construct_event(
            payload=request.data, sig_header=signature, secret=endpoint_secret
        )
    except ValueError as e:
        # Invalid payload.
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid Signature.
        return Response(status=400)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_details = session["metadata"]
        handle_completed_checkout_session(user_details, session)

    return json.dumps({"success": True}), 200


def handle_completed_checkout_session(user_details, session):
    # Fulfill the purchase.
    print(user_details)


@app.route('/')
def serve_checkout_html():
    return send_from_directory('public', 'checkout.html')


if __name__ == '__main__':
    app.run(port=4242)
