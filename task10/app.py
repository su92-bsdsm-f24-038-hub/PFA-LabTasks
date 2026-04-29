from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Medical center data
doctors = {
    "cardiology": ["Dr. Ahmed Khan", "Dr. Sara Ali"],
    "neurology": ["Dr. Bilal Hassan", "Dr. Fatima Noor"],
    "pediatrics": ["Dr. Ayesha Malik", "Dr. Usman Tariq"],
    "orthopedics": ["Dr. Zain Abbas", "Dr. Hira Jamil"]
}

departments = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Emergency", "Radiology"]

timings = "Monday to Friday: 9:00 AM - 5:00 PM, Saturday: 10:00 AM - 2:00 PM"

# Simple chatbot logic
def get_response(message):
    msg = message.lower()

    # Greetings
    if "hello" in msg or "hi" in msg or "hey" in msg:
        return "Hello! Welcome to City Medical Center. How can I help you today?"

    # Appointment related
    if "appointment" in msg or "book" in msg:
        return "To book an appointment, please call us at 042-1234567 or visit our reception. What department are you looking for?"

    # Department info
    if "department" in msg:
        dept_list = ", ".join(departments)
        return f"We have the following departments: {dept_list}. Which one would you like to know about?"

    # Doctor info
    if "doctor" in msg or "doctors" in msg:
        if "cardiology" in msg or "heart" in msg:
            return f"Our Cardiology doctors are: {', '.join(doctors['cardiology'])}"
        elif "neurology" in msg or "brain" in msg or "neuro" in msg:
            return f"Our Neurology doctors are: {', '.join(doctors['neurology'])}"
        elif "pediatric" in msg or "child" in msg or "kids" in msg:
            return f"Our Pediatrics doctors are: {', '.join(doctors['pediatrics'])}"
        elif "orthopedic" in msg or "bone" in msg or "fracture" in msg:
            return f"Our Orthopedics doctors are: {', '.join(doctors['orthopedics'])}"
        else:
            return "Please specify which department's doctors you want to know about (Cardiology, Neurology, Pediatrics, Orthopedics)"

    # Timing
    if "timing" in msg or "time" in msg or "hours" in msg or "open" in msg:
        return f"Our hospital timings are: {timings}"

    # Emergency
    if "emergency" in msg or "urgent" in msg:
        return "For emergencies, please call 1122 or visit our Emergency Department which is open 24/7."

    # Location
    if "location" in msg or "address" in msg or "where" in msg:
        return "We are located at 123 Main Street, Lahore. You can find us near Liberty Market."

    # Contact
    if "contact" in msg or "phone" in msg or "number" in msg:
        return "You can contact us at: Phone: 042-1234567, Email: info@citymedical.com"

    # Default response
    return "I'm here to help! You can ask me about appointments, departments, doctors, timings, or emergency services."


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please type something!"})

    bot_response = get_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
