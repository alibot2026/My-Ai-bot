import os
import io
import urllib.parse
import requests
from flask import Flask, request, jsonify, render_template_string, send_file
from PIL import Image, ImageDraw

app = Flask(__name__)

# ============================================================
#  YAHAN APNI GROQ API KEY PASTE KAREIN (Quotes ke andar)
# ============================================================
GROQ_API_KEY = "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"
# ============================================================

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TEXT_MODEL = MODEL = "openai/gpt-oss-120b"
VISION_MODEL = "llama-3.2-11b-vision-preview"

# 🧠 AI Ki Memory (Aapki Saari Requirements)
SYSTEM_PROMPT = """Aap ek bohot friendly, smart aur madadgar AI Assistant hain. Aapka naam "Master Ali AI" hai.
Aap Urdu aur English dono mein baat karte hain aur hamesha khushmizaj andaz mein jawab dete hain.

Zaroori Maloomat (Inko hamesha yaad rakhein):
- Agar user pooche "Tumhe kisne banaya hai?" toh jawab dein: "Mujhe Master Ali Arsh Khan ne banaya hai."
- Agar user pooche "Owner ke Father ka naam kya hai?" toh jawab dein: "Mr. Mueez Khan."
- Agar user pooche "Mother ka naam kya hai?" toh jawab dein: "Mrs. Sajda Khan."
- Agar user pooche "Bhai ka naam kya hai?" toh jawab dein: "Chota Don Zain Khan."
- Agar user pooche "Favourite teacher kaun hain?" toh jawab dein: "V.P sir, Shiv Kumar."
- Agar user pooche "Favourite cousin kaun hain?" toh jawab dein: "Aman Khan aur Junaid Khan."
- Baaki har aam sawal ka jawab aap ek smart AI ki tarah dein."""

def ask_groq(msg, img_b64=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if img_b64:
        content = [
            {"type": "text", "text": msg if msg else "Is photo mein kya hai?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]
        messages.append({"role": "user", "content": content})
        model_to_use = VISION_MODEL
    else:
        messages.append({"role": "user", "content": msg})
        model_to_use = TEXT_MODEL

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": model_to_use, "messages": messages, "temperature": 0.7, "max_tokens": 500}
    
    try:
        r = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def make_image_url(prompt):
    encoded = urllib.parse.quote(prompt + ", high quality, detailed, cinematic lighting")
    return f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true"

# 🎨 UI Design (100% Fixed for Old Phones + History)
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#764ba2">
<link rel="manifest" href="/manifest.json">
<title>Master Ali AI</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
html, body { height: 100%; height: 100dvh; overflow: hidden; background:#0d0d15; }
body { display:flex; justify-content:center; }
.app { width:100%; max-width:520px; height:100%; display:flex; flex-direction:column; }
.header { background:linear-gradient(90deg,#667eea,#764ba2); padding:12px 16px; display:flex; justify-content:space-between; align-items:center; flex-shrink: 0; }
.hinfo { display:flex; align-items:center; gap:10px; }
.avatar { width:38px; height:38px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-size:20px; }
.hinfo h2 { color:#fff; font-size:15px; }
.hinfo p { color:#d0d0ff; font-size:10px; }
.clear-btn { background:transparent; border:1px solid #fff; color:#fff; padding:5px 10px; border-radius:10px; font-size:11px; cursor:pointer; }
.chat { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:10px; scroll-behavior: smooth; }
.msg { max-width:85%; padding:10px 14px; border-radius:16px; font-size:14px; line-height:1.4; word-wrap:break-word; }
.user { align-self:flex-end; background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; border-bottom-right-radius:4px; }
.bot { align-self:flex-start; background:#1e1e2e; color:#e0e0e0; border-bottom-left-radius:4px; border:1px solid #333; }
.bot img { max-width:100%; border-radius:10px; margin-top:8px; display:block; }
.typing { align-self:flex-start; color:#888; font-size:12px; padding:8px 14px; font-style:italic; }
.modes { display:flex; gap:8px; padding:8px 12px; background:#1a1a2e; border-top:1px solid #333; flex-shrink: 0; }
.mode-btn { flex:1; padding:8px; border:1px solid #333; background:#252540; color:#aaa; border-radius:20px; font-size:12px; cursor:pointer; }
.mode-btn.active { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; border:none; }
.input-area { padding:8px 12px; background:#1a1a2e; display:flex; gap:8px; align-items:center; flex-shrink: 0; padding-bottom: max(8px, env(safe-area-inset-bottom)); }
.upload-btn { background:#252540; color:#fff; padding:9px; border-radius:50%; cursor:pointer; font-size:16px; }
.input-area input[type="text"] { flex:1; padding:10px 14px; border:none; border-radius:20px; background:#252540; color:#fff; font-size:14px; outline:none; }
.input-area button { padding:0 16px; border:none; border-radius:20px; background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; font-weight:bold; cursor:pointer; }
#preview { display:none; width:35px; height:35px; border-radius:8px; object-fit:cover; }
</style>
</head>
<body>
<div class="app">
    <div class="header">
        <div class="hinfo">
            <div class="avatar">🤖</div>
            <div>
                <h2>Master Ali AI</h2>
                <p>● Online (Memory Active)</p>
            </div>
        </div>
        <button class="clear-btn" onclick="clearHistory()">Clear</button>
    </div>
    <div class="chat" id="chat">
        <div class="msg bot">Salam! Main Master Ali AI hoon. Meri memory save hai! Mujhse kuch bhi poochein ya image banwayein! 🌟</div>
    </div>
    <div class="modes">
        <button class="mode-btn active" id="chatMode" onclick="setMode('chat')">💬 Photo/Chat</button>
        <button class="mode-btn" id="imgMode" onclick="setMode('image')">🎨 Art</button>
    </div>
    <div class="input-area">
        <img id="preview" src="">
        <label class="upload-btn" for="fileInput" id="uploadLabel">📎</label>
        <input type="file" id="fileInput" accept="image/*" style="display:none" onchange="handleFile()">
        <input type="text" id="inp" placeholder="Kuch likhein..." onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()">Send</button>
    </div>
</div>
<script>
let mode = 'chat';
let uploadedImageBase64 = null;
const chat = document.getElementById('chat');
const inp = document.getElementById('inp');

// History Load Karne Ka System
let history = JSON.parse(localStorage.getItem('ali_chat_history')) || [];

window.onload = () => {
    history.forEach(msg => {
        const div = document.createElement('div');
        div.className = 'msg ' + msg.role;
        if (msg.text) div.innerText = msg.text;
        if (msg.img) {
            const img = document.createElement('img');
            img.src = msg.img;
            div.appendChild(img);
        }
        chat.appendChild(div);
    });
    chat.scrollTop = chat.scrollHeight;
};

function saveToHistory(role, text, img=null) {
    history.push({role, text, img});
    localStorage.setItem('ali_chat_history', JSON.stringify(history));
}

function clearHistory() {
    if(!confirm("Kya aap pakka chat delete karna chahte hain?")) return;
    localStorage.removeItem('ali_chat_history');
    history = [];
    chat.innerHTML = '<div class="msg bot">Chat history clear ho gayi! Naya sawal poochein. 🌟</div>';
}

function setMode(m) {
    mode = m;
    document.getElementById('chatMode').classList.toggle('active', m==='chat');
    document.getElementById('imgMode').classList.toggle('active', m==='image');
    inp.placeholder = m==='chat' ? 'Poochein ya photo ke baare mein...' : 'Kaisi art banau?';
    document.getElementById('uploadLabel').style.display = m === 'chat' ? 'block' : 'none';
    if (m === 'image') { uploadedImageBase64 = null; document.getElementById('preview').style.display = 'none'; }
}

// 🚨 PHOTO COMPRESSOR (Error 400 Fix)
function handleFile() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const MAX_SIZE = 800; 
            let width = img.width;
            let height = img.height;
            if (width > height) { if (width > MAX_SIZE) { height *= MAX_SIZE / width; width = MAX_SIZE; } } 
            else { if (height > MAX_SIZE) { width *= MAX_SIZE / height; height = MAX_SIZE; } }
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            uploadedImageBase64 = dataUrl.split(',')[1];
            const preview = document.getElementById('preview');
            preview.src = dataUrl;
            preview.style.display = 'block';
            inp.value = "Is photo mein kya hai?";
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// Keyboard khulte hi neeche scroll (Old Phone Fix)
window.addEventListener('resize', () => { setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 100); });
inp.addEventListener('focus', () => { setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 200); });

async function send() {
    const text = inp.value.trim();
    if (!text && !uploadedImageBase64) return;
    
    const u = document.createElement('div');
    u.className = 'msg user'; 
    u.innerText = text ? text : "Photo";
    let imgData = null;
    if (uploadedImageBase64) {
        imgData = 'data:image/jpeg;base64,' + uploadedImageBase64;
        const img = document.createElement('img');
        img.src = imgData;
        u.appendChild(img);
    }
    chat.appendChild(u); 
    saveToHistory('user', text, imgData);
    
    inp.value = ''; chat.scrollTop = chat.scrollHeight;
    uploadedImageBase64 = null;
    document.getElementById('preview').style.display = 'none';
    document.getElementById('fileInput').value = '';
    
    const t = document.createElement('div');
    t.className = 'typing';
    t.innerText = mode === 'chat' ? 'Soch raha hoon...' : '🎨 Art ban rahi hai (10-20 sec)...';
    chat.appendChild(t); chat.scrollTop = chat.scrollHeight;
    
    try {
        if (mode === 'chat') {
            const r = await fetch('/chat', {
                method:'POST', headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({message:text, image: imgData ? uploadedImageBase64 || imgData.split(',')[1] : null})
            });
            const d = await r.json();
            t.remove();
            const b = document.createElement('div');
            b.className = 'msg bot'; b.innerText = d.reply;
            chat.appendChild(b);
            saveToHistory('bot', d.reply);
        } else {
            const r = await fetch('/image', {
                method:'POST', headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({prompt:text})
            });
            const d = await r.json();
            t.remove();
            const b = document.createElement('div');
            b.className = 'msg bot';
            const img = document.createElement('img');
            img.src = d.url;
            img.onload = () => { chat.scrollTop = chat.scrollHeight; }; 
            b.innerText = '🎨 ' + text;
            b.appendChild(img);
            chat.appendChild(b);
            saveToHistory('bot', '🎨 ' + text, d.url);
        }
        chat.scrollTop = chat.scrollHeight;
    } catch(e) { 
        t.innerText = 'Internet check karein.'; 
    }
}
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js');
</script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    d = request.get_json()
    return jsonify({'reply': ask_groq(d.get('message',''), d.get('image'))})

@app.route('/image', methods=['POST'])
def image():
    d = request.get_json()
    return jsonify({'url': make_image_url(d.get('prompt',''))})

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Master Ali AI", "short_name": "Ali AI", "start_url": "/",
        "display": "standalone", "background_color": "#0d0d15", "theme_color": "#764ba2",
        "icons": [{"src":"/icon.png","sizes":"192x192","type":"image/png"},
                  {"src":"/icon.png","sizes":"512x512","type":"image/png"}]
    })

@app.route('/service-worker.js')
def sw():
    js = "self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());self.addEventListener('fetch',e=>{});"
    return app.response_class(js, mimetype='application/javascript')

@app.route('/icon.png')
def icon():
    img = Image.new('RGB', (512,512), (118,75,162))
    d = ImageDraw.Draw(img)
    d.ellipse([60,60,452,452], fill=(255,255,255))
    d.ellipse([140,200,200,260], fill=(118,75,162))
    d.ellipse([312,200,372,260], fill=(118,75,162))
    d.rounded_rectangle([180,320,332,355], radius=15, fill=(118,75,162))
    buf = io.BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
