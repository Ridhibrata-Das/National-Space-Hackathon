import firebase_admin
from firebase_admin import credentials, firestore, db
import os
import asyncio

# The user explicitly named the file this way
CRED_PATH = os.path.join(os.path.dirname(__file__), "nationalspacehackathon-firebase-adminsdk-fbsvc-9dab521244.json")

db_firestore = None
db_rtdb = None

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(CRED_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://nationalspacehackathon-default-rtdb.firebaseio.com'
        })
    print("DEBUG: Firebase Admin SDK initialized successfully.")
    db_firestore = firestore.client()
    db_rtdb = db.reference()
except Exception as e:
    print(f"ERROR: Failed to initialize Firebase Admin SDK: {e}")


async def sync_state_to_firebase(telemetry_data):
    """Pushes the current simulation state to Firebase (Non-blocking)."""
    if not db_rtdb:
        return
        
    def _firebase_push():
        try:
            # Push to Realtime Database
            db_rtdb.child("telemetry").set({
                "timestamp": telemetry_data["timestamp"],
                "satellites": telemetry_data["satellites"]
            })
            
            # Push Warnings to Firestore
            if db_firestore and "cdm_warnings" in telemetry_data:
                batch = db_firestore.batch()
                cdms = telemetry_data["cdm_warnings"]
                for cdm in cdms:
                    doc_id = f"{cdm['sat_id']}_{cdm['debris_id']}"
                    doc_ref = db_firestore.collection("cdm_warnings").document(doc_id)
                    batch.set(doc_ref, cdm, merge=True)
                batch.commit()
                
        except Exception as e:
            print(f"ERROR: Firebase Sync Failed: {e}")
            
    await asyncio.to_thread(_firebase_push)
