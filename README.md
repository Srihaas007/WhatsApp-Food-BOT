# WhatsApp Food BOT

WhatsApp chat bot created using the Twilio Programmable SMS API

# What is Needed
  - A Google Developers API Key 
  - ngrok
- A Twilio account for

### Installation
 - Create a Twilio account.
 - Install ngrok, authenticate and run the following command on a terminal:
 ```sh
$ ngrok http 5000
``` 
  - Go to the following page after you have created your Twilio account - https://www.twilio.com/console/sms/whatsapp/sandbox
  - Copy the generated URL from the ngrok terminal into the 'WHEN A MESSAGE COMES IN' box.
  - Click Save at the bottom
  - Follow the prompts on the page to add your WhatsApp number to the sandbox.
  - Clone this repo and run the following commands: 
```sh
$ pip install -r requirements.txt
$ echo GOOGLE_API_KEY=your_google_api_key > .env
$ python app.py
```
 - The application is ready!
