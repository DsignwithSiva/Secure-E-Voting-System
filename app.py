import time
from flask import Flask, render_template,request ,jsonify, redirect, url_for, session
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os

import requests
import xml.etree.ElementTree as ET
import base64


app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.secret_key = "secret123"
CORS(app)

# Detect FM220U Fingerprint Scanner
VENDOR_ID = 0x0bca  # Change if needed
PRODUCT_ID = 0x8220  # Change if needed

# MongoDB Connection
MONGO_URI = "mongodb+srv://dineshvaradhi121:BiCHNjDT5elXkB4U@cluster-1.g4plz.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["E_voting"]

# Collections
candidates_collection = db["candidates"]
voters_collection = db["voters"]
elections_collection = db["elections"]

# Upload Folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def login_page():
    return render_template("admin login.html")


@app.route("/index")
def index_page():
    if "admin" in session:
        return render_template("index.html")
    return redirect(url_for("login_page"))


@app.route("/add_candidate")
def add_candidate_page():
    return render_template("add candidate.html")


@app.route("/add_voter")
def add_voter_page():
    return render_template("add voter.html")


@app.route("/add_election")
def add_election_page():
    return render_template("add election.html")


@app.route("/calculate_result")
def calculate_result_page():
    return render_template("calculate result.html")

@app.route("/start")
def start_page():
    return render_template("start.html")


@app.route("/voting_process")
def voting_process_page():
    return render_template("voting process.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if data["username"] == "admin" and data["password"] == "8074@":
        session["admin"] = True
        return jsonify({"message": "Login successful", "redirect": "/index"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login_page"))


# 📌 **Handle Candidate Registration with Image**
@app.route("/add_candidate", methods=["POST"])
def add_candidate():
    if "photoInput" not in request.files or request.files["photoInput"].filename == "":
        return jsonify({"error": "No file part"}), 400

    file = request.files["photoInput"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Get other form data
    election_id = request.form.get("electionID")
    candidate_name = request.form.get("candidateName")
    candidate_id = request.form.get("candidateID")
    candidate_address = request.form.get("candidateAddress")

    print("Received Data in Flask:")  # 🔍 Debugging
    print("Election Id:", election_id)
    print("Candidate Name:", candidate_name)
    print("Candidate ID:", candidate_id)
    print("Candidate Address:", candidate_address)
    print("Photo Path:", file_path)

    if not candidate_name or not candidate_id or not candidate_address:
        return jsonify({"error": "Missing required fields"}), 400

    candidate_data = {
        "electionID": election_id,  # Added Election ID
        "candidateName": candidate_name,
        "candidateID": candidate_id,
        "candidateAddress": candidate_address,
        "photoPath": file_path,
        "voteCount": 0  # ✅ Initialize vote count
    }

    result = candidates_collection.insert_one(candidate_data)
    print("Inserted ID:", result.inserted_id)  # 🔍 Debugging

    return jsonify({"message": "Candidate added successfully!"})

# 📌 **Handle Voter Registration with Image**
@app.route("/add_voter", methods=["POST"])
def add_voter():
    if "photoInput" not in request.files or request.files["photoInput"].filename == "":
        return jsonify({"error": "No file part"}), 400

    file = request.files["photoInput"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Get voter details
    voter_id = request.form.get("voterID")
    voter_name = request.form.get("voterName")
    mobile_number = request.form.get("mobileNumber")
    address = request.form.get("address")
    fingerprint_xml = request.form.get("fingerprintXML")

    print("Received Data in Flask:")  # Debugging
    print("Voter ID:", voter_id)
    print("Voter Name:", voter_name)
    print("Mobile Number:", mobile_number)
    print("Address:", address)
    print("Photo Path:", file_path)

    if not voter_id or not voter_name or not mobile_number or not address:
        return jsonify({"error": "Missing required fields"}), 400

    voter_data = {
        "voterID": voter_id,
        "voterName": voter_name,
        "mobileNumber": mobile_number,
        "address": address,
        "photoPath": file_path,
        "fingerprint": fingerprint_xml  # ✅ Save only here
    }

    result = voters_collection.insert_one(voter_data)
    print("Inserted ID:", result.inserted_id)  # Debugging

    return jsonify({"message": "Voter added successfully!"})

# 📌 **Handle Election Registration**
@app.route("/add_election", methods=["POST"])
def add_election():
    try:
        # Get JSON data from the frontend
        data = request.get_json()

        # Debugging: Print received data
        print("🛠️ Debug: Received Data in Flask", data)

        # Validate required fields
        if not data:
            print("❌ Error: No data received")
            return jsonify({"error": "No data received"}), 400

        electionID = data.get("electionID")
        topic = data.get("topic")
        candidateCount = data.get("candidateCount")
        endDate = data.get("endDate")
        candidates = data.get("candidates")

        # Debugging: Print individual fields
        print("🛠️ Debug: Election ID:", electionID)
        print("🛠️ Debug: Topic:", topic)
        print("🛠️ Debug: Candidate Count:", candidateCount)
        print("🛠️ Debug: End Date:", endDate)
        print("🛠️ Debug: Candidates:", candidates)

        # Check for missing fields
        if not electionID or not topic or not candidateCount or not endDate or not candidates:
            print("❌ Error: Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Ensure candidateCount is a valid integer
        try:
            candidateCount = int(candidateCount)
        except ValueError:
            print("❌ Error: Candidate count must be a number")
            return jsonify({"error": "Candidate count must be a number"}), 400

        # Ensure at least 2 candidates are selected
        if candidateCount < 2:
            print("❌ Error: At least 2 candidates must be selected")
            return jsonify({"error": "At least 2 candidates must be selected"}), 400

        # Prepare data for MongoDB
        election_data = {
            "electionID": electionID,
            "topic": topic,
            "candidateCount": candidateCount,
            "endDate": endDate,
            "candidates": candidates
        }

        # Debugging: Print data to be inserted into MongoDB
        print("🛠️ Debug: Data to be inserted into MongoDB:", election_data)

        # Insert data into MongoDB
        result = elections_collection.insert_one(election_data)
        print("✅ Inserted Election ID:", result.inserted_id)

        return jsonify({"message": "✅ Election added successfully!"})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": "An error occurred while adding the election"}), 500

@app.route("/capture_fingerprint", methods=["POST"])
def capture_fingerprint():
    data = request.get_json()
    voter_id = data.get("voterID")

    if not voter_id:
        return jsonify({"error": "Voter ID is missing!"}), 400

    # XML request as per Startek RD Service spec
    pid_options = """
    <PidOptions ver="1.0">
        <Opts env="P" fCount="1" fType="0" iCount="0" pCount="0" format="0" pidVer="2.0" timeout="20000" otp="" wadh="" posh="UNKNOWN"/>
    </PidOptions>
    """.strip()

    try:
        # Send to RD Service
        response = requests.post("http://127.0.0.1:11100/rd/capture", data=pid_options, headers={"Content-Type": "text/xml"})

        # Check for errors
        if response.status_code != 200:
            return jsonify({"error": "Failed to capture fingerprint"}), 500

        # Parse XML response
        xml_data = response.text
        root = ET.fromstring(xml_data)
        resp_node = root.find("Resp")
        if resp_node is not None and resp_node.attrib.get("errCode") != "0":
            err = resp_node.attrib.get("errInfo")
            return jsonify({"error": f"Fingerprint Error: {err}"}), 400

        # Save full XML to MongoDB
        voters_collection.update_one(
            {"voterID": voter_id},
            {"$set": {"fingerprintXML": xml_data}},
            upsert=True
        )

        return jsonify({"message": "Fingerprint captured and stored successfully!"})

    except Exception as e:
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500


# @app.route("/verify_fingerprint", methods=["POST"])
# def verify_fingerprint():
#     data = request.get_json()
#     captured_xml = data.get("fingerprintXml")
#
#     if not captured_xml:
#         return jsonify({"error": "Fingerprint data missing"}), 400
#
#     try:
#         captured_root = ET.fromstring(captured_xml)
#         captured_pid_data = captured_root.find("Data").text if captured_root.find("Data") is not None else ""
#
#         if not captured_pid_data:
#             return jsonify({"error": "Invalid fingerprint structure"}), 400
#
#         # Get all stored fingerprints
#         all_voters = voters_collection.find({}, {"voterID": 1, "voterName": 1, "photoPath": 1, "fingerprint": 1})
#
#         print("Captured fingerprint data (from scanner):", captured_pid_data)
#
#         for voter in all_voters:
#             xml = voter.get("fingerprint")
#             if not xml:
#                 continue
#
#             db_root = ET.fromstring(xml)
#             db_pid_data = db_root.find("Data").text if db_root.find("Data") is not None else ""
#             print("Stored fingerprint data (from DB):", db_pid_data)
#             if captured_pid_data.strip() == db_pid_data.strip():
#                 return jsonify({
#                     "voterID": voter.get("voterID"),
#                     "voterName": voter.get("voterName"),
#                     "photoPath": voter.get("photoPath")
#                 })
#
#         return jsonify({"error": "Fingerprint does not match any registered voter."}), 404
#
#     except Exception as e:
#         return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/get_voter_details", methods=["GET"])
def get_voter_details():
    voter_id = request.args.get('voterID')

    if not voter_id:
        return jsonify({"error": "Voter ID is required"}), 400

    try:
        voter = voters_collection.find_one({"voterID": voter_id})

        if not voter:
            return jsonify({"error": "Voter not found"}), 404

        # Prepare response
        response = {
            "voterID": voter["voterID"],
            "voterName": voter["voterName"],
            "photoPath": voter.get("photoPath", "")
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_all_election_ids")
def get_all_election_ids():
    try:
        elections = elections_collection.find({}, {"_id": 0, "electionID": 1})
        ids = [election["electionID"] for election in elections]
        return jsonify({"electionIDs": ids})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_election_details")
def get_election_details():
    election_id = request.args.get("electionID")

    if not election_id:
        return jsonify({"error": "Missing Election ID"}), 400

    election = elections_collection.find_one({"electionID": election_id})

    if not election:
        return jsonify({"error": "Election not found"}), 404

    return jsonify({
        "topic": election.get("topic"),
        "candidates": election.get("candidates", [])
    })


@app.route("/cast_vote", methods=["POST"])
def cast_vote():
    data = request.get_json()
    election_id = data.get("electionID")
    candidate_name = data.get("candidate")

    if not election_id or not candidate_name:
        return jsonify({"error": "Missing data"}), 400

    try:
        # ✅ Increment voteCount for the right candidate
        result = candidates_collection.update_one(
            {
                "electionID": election_id,
                "candidateName": candidate_name
            },
            {"$inc": {"voteCount": 1}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Candidate not found or vote not updated"}), 404

        return jsonify({"message": f"Vote successfully cast for {candidate_name}!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_results')
def get_results():
    election_id = request.args.get('electionID','').strip()
    print(election_id)
    candidates = list(candidates_collection.find({'electionID':election_id},{"_id": 0, "candidateName": 1, "voteCount": 1}))
    print(candidates)
    return jsonify(candidates)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
