from flask import Flask, render_template, request
import pandas as pd
import pickle

# =====================================================
# CREATE FLASK APP
# =====================================================

app = Flask(__name__)

# =====================================================
# LOAD MODEL & PREPROCESSOR
# =====================================================

model = pickle.load(open("model.pkl", "rb"))

preprocessor = pickle.load(open("preprocessor.pkl", "rb"))

# =====================================================
# HOME ROUTE
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")

# =====================================================
# PREDICTION ROUTE
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # =================================================
        # BASIC FORM INPUTS
        # =================================================

        transaction_id = int(
            request.form["transaction_id"]
        )

        amount = float(
            request.form["amount"]
        )

        transaction_hour = int(
            request.form["transaction_hour"]
        )

        merchant_category = request.form[
            "merchant_category"
        ]

        foreign_transaction = int(
            request.form["foreign_transaction"]
        )

        velocity_last_24h = float(
            request.form["velocity_last_24h"]
        )

        cardholder_age = int(
            request.form["cardholder_age"]
        )

        # =================================================
        # LOCATION MISMATCH
        # =================================================

        location_mismatch = int(
            request.form["unusual_location"]
        )

        # =================================================
        # DEVICE TRUST SCORE CALCULATION
        # =================================================

        new_device = request.form["new_device"]

        vpn_used = request.form["vpn_used"]

        same_location = request.form[
            "same_location"
        ]

        successful_transactions = int(
            request.form["successful_transactions"]
        )

        # Initial Trust Score
        device_trust_score = 100

        # Risk deductions

        if new_device == "Yes":

            device_trust_score -= 25

        if vpn_used == "Yes":

            device_trust_score -= 15

        if same_location == "No":

            device_trust_score -= 20

        if successful_transactions < 5:

            device_trust_score -= 15

        # Velocity based deductions

        if velocity_last_24h > 10:

            device_trust_score -= 20

        elif velocity_last_24h > 5:

            device_trust_score -= 10

        # Keep within range

        device_trust_score = max(
            0,
            min(100, device_trust_score)
        )

        # =================================================
        # CREATE INPUT DATAFRAME
        # =================================================

        input_data = pd.DataFrame([{

            "transaction_id": transaction_id,

            "amount": amount,

            "transaction_hour": transaction_hour,

            "merchant_category": merchant_category,

            "foreign_transaction":
                foreign_transaction,

            "location_mismatch":
                location_mismatch,

            "device_trust_score":
                device_trust_score,

            "velocity_last_24h":
                velocity_last_24h,

            "cardholder_age":
                cardholder_age

        }])

        # =================================================
        # PREPROCESS INPUT
        # =================================================

        input_processed = preprocessor.transform(
            input_data
        )

        # =================================================
        # ML MODEL PREDICTION
        # =================================================

        prediction = model.predict(
            input_processed
        )[0]

        probability = model.predict_proba(
            input_processed
        )[0][1]

        # =================================================
        # RULE-BASED FRAUD ENGINE
        # =================================================

        fraud_score = 0

        reasons = []

        # High Amount

        if amount > 5000:

            fraud_score += 2

            reasons.append(
                "Very high transaction amount"
            )

        elif amount > 1000:

            fraud_score += 1

            reasons.append(
                "High transaction amount"
            )

        # Foreign Transaction

        if foreign_transaction == 1:

            fraud_score += 2

            reasons.append(
                "Foreign transaction detected"
            )

        # Location Mismatch

        if location_mismatch == 1:

            fraud_score += 2

            reasons.append(
                "Unusual transaction location"
            )

        # Low Trust Device

        if device_trust_score < 30:

            fraud_score += 3

            reasons.append(
                "Very low device trust score"
            )

        elif device_trust_score < 50:

            fraud_score += 2

            reasons.append(
                "Low device trust score"
            )

        # Velocity Check

        if velocity_last_24h > 10:

            fraud_score += 3

            reasons.append(
                "Extremely high transaction activity"
            )

        elif velocity_last_24h > 5:

            fraud_score += 2

            reasons.append(
                "High transaction velocity detected"
            )

        # Night Transactions

        if transaction_hour < 5:

            fraud_score += 1

            reasons.append(
                "Transaction made at unusual hour"
            )

        # New Device

        if new_device == "Yes":

            fraud_score += 2

            reasons.append(
                "Transaction from new device"
            )

        # VPN Usage

        if vpn_used == "Yes":

            fraud_score += 1

            reasons.append(
                "VPN usage detected"
            )

        # =================================================
        # FINAL HYBRID DECISION
        # =================================================

        # Rule-based override

        if fraud_score >= 5:

            prediction = 1

        # =================================================
        # RESULT MESSAGE
        # =================================================

        if prediction == 1:

            if len(reasons) == 0:

                reasons.append(
                    "Suspicious transaction pattern detected"
                )

            result = f"""
⚠ FRAUD TRANSACTION DETECTED

Confidence Score : {probability * 100:.2f}%

Fraud Risk Score : {fraud_score}/15

Device Trust Score : {device_trust_score}/100

Possible Reasons:
"""

            for reason in reasons:

                result += f"\n• {reason}"

        else:

            result = f"""
✓ NORMAL TRANSACTION

Confidence Score : {(1 - probability) * 100:.2f}%

Fraud Risk Score : {fraud_score}/15

Device Trust Score : {device_trust_score}/100

Transaction appears safe and follows normal customer behavior.
"""

        # =================================================
        # RETURN RESULT
        # =================================================

        return render_template(

            "index.html",

            prediction_text=result
        )

    except Exception as e:

        return render_template(

            "index.html",

            prediction_text=f"Error: {e}"
        )

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)