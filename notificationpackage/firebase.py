import firebase_admin
from firebase_admin import credentials, messaging
import os

# Define the path to the credentials JSON file
cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credential.json')

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase app with the service account key
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_push_notification(tokens, title, message):
    try:
        # Create a MulticastMessage instance
        multicast_message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=title,
                body=message,
            )
        )

        # Send the message
        response = messaging.send_multicast(multicast_message)

        # Print the full response
        print(f"Notification sent successfully: {response}")

        # Collect results
        success_count = 0
        failure_count = 0
        for i, result in enumerate(response.responses):
            if result.success:
                success_count += 1
            else:
                failure_count += 1
                print(f"Error sending notification to token {tokens[i]}: {result.exception}")

        return success_count, failure_count

    except Exception as e:
        print(f"Error sending push notification: {e}")
        raise
