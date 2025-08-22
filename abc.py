# from pymongo import MongoClient
#
# MONGO_URI = "mongodb+srv://dineshvaradhi121:BiCHNjDT5elXkB4U@cluster-1.g4plz.mongodb.net/"
# client = MongoClient(MONGO_URI)
# db = client["E_voting"]
#
# # Insert sample data to create collections
# db["candidates"].insert_one({
#     "candidateName": "Test Candidate",
#     "candidateID": "123",
#     "candidateAddress": "Test Address",
#     "photoInput": "test_candidate.jpg"  # Storing the filename
# })
#
# # Insert sample voter with image file reference
# db["voters"].insert_one({
#     "voterID": "V001",
#     "voterName": "John Doe",
#     "mobileNumber": "1234567890",
#     "address": "Test City",
#     "photoInput": "test_voter.jpg"
# })
# db["elections"].insert_one({"electionID": "E001", "topic": "Test Election", "candidateCount": 2, "endDate": "2025-12-31"})
#
# print("Inserted sample data successfully!")
#
# # Check collections
# print("Collections:", db.list_collection_names())



# import usb.core
# import usb.util
# import usb.backend.libusb1
#
# # Set the backend manually
# backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Windows\\System32\\libusb-1.0.dll")  # Windows path
# # For Linux, use: find_library=lambda x: "/usr/lib/x86_64-linux-gnu/libusb-1.0.so"
#
# device = usb.core.find(idVendor=0x0FDE, idProduct=0xCA01, backend=backend)
#
# if device is None:
#     print("FM220U Device Not Found!")
# else:
#     print("FM220U Device Connected!")


# import usb.core
# print(usb.core.find())
#
#
# import usb.core
#
# import usb.util
#
# # Find FM220U Fingerprint Scanner (Update with correct Vendor & Product ID)
# dev = usb.core.find(idVendor=0x0bca, idProduct=0x8220)  # Replace with your scanner's values
#
# if dev is None:
#     raise ValueError("Fingerprint scanner not found")
#
# # Set configuration to access USB device
# dev.set_configuration()
#
# # Claim the USB interface
# usb.util.claim_interface(dev, 0)


import usb.core
import usb.util

# Find the FM220U scanner
# dev = usb.core.find(idVendor=0x0bca)  # Mantra FM220U Vendor ID
#
# if dev:
#     print("FM220U Fingerprint Scanner detected!")
# else:
#     print("FM220U not found. Check connections and drivers.")
#
# for cfg in dev:
#     for interface in cfg:
#         for endpoint in interface:
#             print(endpoint.bEndpointAddress)

# import usb.core
# import usb.util
#
# dev = usb.core.find(idVendor=0x0bca, idProduct=0x8220)
#
# if dev is None:
#     raise ValueError("Device not found")
# else:
#     try:
#         dev.set_configuration()
#         print("Device configured successfully!")
#     except usb.core.USBError as e:
#         print(f"USB Error: {e}")



import win32com.client
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Fingerprint Scanner"

@app.route('/capture_fingerprint', methods=['POST'])
def capture_fingerprint():
    try:
        # You will need to explore `win32com.client` for interacting with the device
        # Here is a placeholder for accessing Biometric device
        biometric_service = win32com.client.Dispatch("WsBiometrics.Service")
        # Further interactions with the biometric_service would be required here.

        return jsonify({"status": "success", "message": "Fingerprint capture initiated."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)