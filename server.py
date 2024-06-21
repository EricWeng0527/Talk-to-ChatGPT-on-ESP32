from flask import Flask, request, send_file
from gtts import gTTS
import whisper
from pydub import AudioSegment
import io
import os
import requests
import json

# 更换为你的 API KEY
API_KEY = 'sk-KFAYcOqq5iPTOB5yF77b363b97C54c34BaC4045a113559Fc'

def text_to_audio(text, file_path):
    # 创建 gTTS 对象
    tts = gTTS(text=text, lang='en')
    # 将音频保存到文件
    tts.save(file_path)
    print(f"Audio file saved at: {file_path}")

def get_chatgpt_response(prompt):
    url = "https://free.gpt.ge/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "gpt-3.5-turbo-0125",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50  # 更改响应长度
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

app = Flask(__name__)

# 加载 Whisper 模型
model = whisper.load_model("base")

@app.route('/whisper', methods=['POST'])
def transcribe_audio():
    try:
        audio_file = request.files['file']
        audio_data = audio_file.read()
        
        # 保存接收到的音频文件以进行本地测试
        with open('received_audio.wav', 'wb') as f:
            f.write(audio_data)

        # 使用 Whisper 模型进行转录
        result = model.transcribe('received_audio.wav')
        print(result['text'])
        response_text = get_chatgpt_response(result['text'])
        print(response_text)
        text_to_audio(response_text, 'output_temp.wav')

        # 使用 pydub 将音频转换为16位单声道16kHz
        audio = AudioSegment.from_file('output_temp.wav')
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export('output.wav', format='wav')

        # 返回生成的音频文件
        return send_file('output.wav', as_attachment=True)
    
    except Exception as e:
        app.logger.error(f"Error processing audio file: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
