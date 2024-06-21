import machine
import network
import urequests as requests
import ustruct as struct
import array
import time
import os

# 配置Wi-Fi
ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Connected to Wi-Fi:', wlan.ifconfig())

# 配置I2S麦克风输入
i2s = machine.I2S(0, 
                  sck=machine.Pin(14), 
                  ws=machine.Pin(15), 
                  sd=machine.Pin(32), 
                  mode=machine.I2S.RX, 
                  bits=16, 
                  format=machine.I2S.MONO, 
                  rate=16000, 
                  ibuf=40000)

audio_file = 'input.wav'

# def write_wav_header(file, sample_rate, bits_per_sample, channels, data_size):
#     file.write(b'RIFF')
#     file.write(ustruct.pack('<I', 36 + data_size))
#     file.write(b'WAVE')
#     file.write(b'fmt ')
#     file.write(ustruct.pack('<I', 16))
#     file.write(ustruct.pack('<H', 1))
#     file.write(ustruct.pack('<H', channels))
#     file.write(ustruct.pack('<I', sample_rate))
#     file.write(ustruct.pack('<I', sample_rate * channels * bits_per_sample // 8))
#     file.write(ustruct.pack('<H', channels * bits_per_sample // 8))
#     file.write(ustruct.pack('<H', bits_per_sample))
#     file.write(b'data')
#     file.write(ustruct.pack('<I', data_size))

# def record_audio(duration):
#     buffer = bytearray(1024)
#     samples_per_second = 16000
#     bytes_per_sample = 2  # 16-bit audio
#     samples_per_buffer = len(buffer) // bytes_per_sample
#     buffers_per_second = samples_per_second // samples_per_buffer
#     total_buffers = duration * buffers_per_second
#     data_size = total_buffers * len(buffer)

#     with open(audio_file, 'wb') as f:
#         write_wav_header(f, samples_per_second, bytes_per_sample * 8, 1, data_size)
#         for _ in range(total_buffers):
#             i2s.readinto(buffer)
#             f.write(buffer)

# 录制5秒音频
# record_audio(5)

def create_wav_header(sample_rate, bits_per_sample, channels, num_samples):
    datasize = num_samples * channels * bits_per_sample // 8
    o = bytes("RIFF", 'ascii')                                               # (4byte) Marks file as RIFF
    o += struct.pack('<I', datasize + 36)                                    # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", 'ascii')                                              # (4byte) File type
    o += bytes("fmt ", 'ascii')                                              # (4byte) Format Chunk Marker
    o += struct.pack('<I', 16)                                               # (4byte) Length of above format data
    o += struct.pack('<H', 1)                                                # (2byte) Format type (1 - PCM)
    o += struct.pack('<H', channels)                                         # (2byte)
    o += struct.pack('<I', sample_rate)                                      # (4byte)
    o += struct.pack('<I', sample_rate * channels * bits_per_sample // 8)    # (4byte)
    o += struct.pack('<H', channels * bits_per_sample // 8)                  # (2byte)
    o += struct.pack('<H', bits_per_sample)                                  # (2byte)
    o += bytes("data", 'ascii')                                              # (4byte) Data Chunk Marker
    o += struct.pack('<I', datasize)                                         # (4byte) Data size in bytes
    return o

#創建 WAV 文件頭
wav_header = create_wav_header(16000, 16, 1, 160005)

#打開文件並寫入頭文件
with open("input.wav", "wb") as f:
    f.write(wav_header)

    buffer = array.array('H', [0] * 1024)  # 创建一个缓冲区
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
        i2s.readinto(buffer)  # 读取数据到缓冲区
        f.write(buffer)       # 写入文件

#關閉 I2S
i2s.deinit()

# 上传音频文件到服务器

def upload_audio(file_path, server_url):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    headers = {
        'Content-Type': 'multipart/form-data; boundary={}'.format(boundary)
    }
    def file_generator():
        yield '--{}\r\n'.format(boundary).encode('utf-8')
        yield 'Content-Disposition: form-data; name="file"; filename="{}"\r\n'.format(file_path).encode('utf-8')
        yield 'Content-Type: audio/wav\r\n\r\n'.encode('utf-8')
        with open(file_path, 'rb') as audio_file:
            while True:
                data = audio_file.read(1024)
                if not data:
                    break
                yield data
        yield '\r\n--{}--\r\n'.format(boundary).encode('utf-8')

    response = requests.post(server_url, headers=headers, data=file_generator())
    if response.status_code == 200:
        with open('output.wav', 'wb') as f:
            while True:
                chunk = response.raw.read(1024)
                if not chunk:
                    break
                f.write(chunk)
        print("Audio file received and saved as output.wav")
    else:
        print("Failed to upload")
        print("Status code:", response.status_code)
        print("Response:", response.text)

server_url = 'http://192.168.199.48:8000/whisper'
upload_audio(audio_file, server_url)

#配置I2S MAX98357输出
i2s_out = machine.I2S(1, 
                      sck=machine.Pin(27), 
                      ws=machine.Pin(26), 
                      sd=machine.Pin(25), 
                      mode=machine.I2S.TX, 
                      bits=16, 
                      format=machine.I2S.MONO, 
                      rate=16000, 
                      ibuf=40000)

def play_audio(file_path):
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            i2s_out.write(data)

play_audio("output.wav")

