# Talk-to-ChatGPT-on-ESP32

This project allows you to interact with ChatGPT using an ESP32, capturing audio input, processing it through a Flask server, and playing back the response audio. 

## Components Used
- ESP32
- INMP441 Microphone
- MAX98537 Amplifier
- Speaker
- Buttons (x2)
- Computer for Flask server

## Prerequisites
1. **ESP32**: Ensure your ESP32 is set up with MicroPython.
2. **Server**: Set up a Flask server on your computer.
3. **Dependencies**:
    - Python3
    - Flask
    - gTTS (Google Text-to-Speech)
    - Whisper (for transcription)
    - Pydub
    - Requests

## Build and Usage Steps

### I. Setting Up the Flask Server
1. **Install dependencies**:
    ```bash
    pip install Flask gtts whisper pydub requests
    ```

2. **Run the server**:
    ```bash
    python server.py
    ```

### II. Setting Up the ESP32
1. **Change your Wi-Fi SSID/PASSWORD**:
    ```python
    import network

    ssid = 'your-SSID'
    password = 'your-PASSWORD'

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        pass

    print('Connected to Wi-Fi:', wlan.ifconfig())
    ```
    
2. **Change your server IP**
   ```python
    server_url = 'http://ip-to-your-server:8000/whisper'
   ```
   
4. **Put GPT-on-ESP32.py on your ESP32**
 
5. **Run the GPT-on-ESP32.py**:
    ```bash
    python GPT-on-ESP32.py
    ```
 
6. **Record Audio**:
press the button and you have 5 seconds to talk

5. **Waiting for Response**:
And speaker will play the response messsage

## Conclusion
By following these steps, you will set up a system where the ESP32 captures audio, sends it to a Flask server for processing by ChatGPT, and plays back the response. This project demonstrates integrating various components and services to create a unique interactive experience.
