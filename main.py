from google.cloud import pubsub_v1
import json
import requests
import configparser 

Config = configparser.ConfigParser()
Config.read("conf.ini")

#Google Setup
project_id = Config.get('Google', 'ProjectID')
subscription_id = Config.get('Google', 'SubscriptionID')

#Particle Setup
Particle_url = Config.get('Particle', 'URL')
payload = 'arg=on'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Authorization': Config.get('Particle', 'Token')
}


subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    message_json=json.loads(message.data.decode('utf-8'))
    event=list(message_json['resourceUpdate']['events'])[0]+"."+message_json['eventThreadState']
    message.ack()
    if (event=="sdm.devices.events.DoorbellChime.Chime.STARTED"):
        print(event)
        Particle_response = requests.request("POST", Particle_url, headers=headers, data=payload)
        print(Particle_response.text)
        

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

with subscriber:
    try:
        print(f"Listening for messages on {subscription_path}..\n")
        streaming_pull_future.result()
    except:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.