import asyncio
import json
import sqlite3
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

def query_portfolio_db(ticker: str) -> str:
    try:
        db_path = r'C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE ticker = ?", (ticker.upper(),))
        row = cursor.fetchone()
        conn.close()
        return f"Database row for {ticker}: {str(row)}" if row else f"Ticker {ticker} not found."
    except Exception as e:
        return f"Database Error: {str(e)}"

# Dynamic generation of the premium, dark-themed voice interface
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JENNY // SYSTEM PLATFORM</title>
    <style>
        body { background-color: #0b0f19; color: #e4e4e7; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        .core-container { text-align: center; width: 500px; }
        .orb { width: 180px; height: 180px; border-radius: 50%; background-color: #121826; border: 4px solid #00ffff; margin: 30px auto; display: flex; align-items: center; justify-content: center; font-size: 48px; box-shadow: 0 0 20px #00ffff33; transition: all 0.3s ease; }
        .status { font-size: 14px; font-weight: bold; color: #00ffff; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }
        .console { background-color: #060910; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; height: 150px; overflow-y: auto; text-align: left; font-size: 13px; color: #a1a1aa; }
    </style>
</head>
<body>
    <div class="core-container">
        <h2 style="color: #3b82f6; margin: 0;">JENNY SYSTEM CORE</h2>
        <div class="orb" id="jennyOrb">🧬</div>
        <div class="status" id="statusLabel">Initializing Grid Connection...</div>
        <div class="console" id="consoleLog">[System] Initializing browser web-audio layer...<br></div>
    </div>

    <script>
        const consoleLog = document.getElementById('consoleLog');
        const statusLabel = document.getElementById('statusLabel');
        const jennyOrb = document.getElementById('jennyOrb');

        function log(msg) { consoleLog.innerHTML += msg + "<br>"; consoleLog.scrollTop = consoleLog.scrollHeight; }
        function setStatus(text, color) { statusLabel.innerText = text; statusLabel.style.color = color; jennyOrb.style.borderColor = color; }

        let ws = new WebSocket(`ws://${window.location.host}/ws`);
        let audioCtx, processor, mediaStream;

        ws.onopen = async () => {
            setStatus("JENNY ONLINE // LISTENING", "#00ffff");
            log("[System] Low-latency full-duplex pipeline established.");
            await initAudio();
        };

        ws.onmessage = async (event) => {
            let msg = JSON.parse(event.data);
            if (msg.type === "audio") {
                // Play raw binary sound buffers via browser hardware layer
                let rawData = Uint8Array.from(atob(msg.data), c => c.charCodeAt(0));
                playAudioChunk(rawData.buffer);
            } else if (msg.type === "state") {
                if (msg.value === "speaking") setStatus("JENNY RESPONDING", "#ff00ff");
                if (msg.value === "listening") setStatus("JENNY ONLINE // LISTENING", "#00ffff");
                if (msg.value === "crunching") setStatus("COMPUTING MODEL METRICS...", "#ffff00");
            } else if (msg.type === "log") {
                log(msg.value);
            }
        };

        async function initAudio() {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
            let source = audioCtx.createMediaStreamSource(mediaStream);
            processor = audioCtx.createScriptProcessor(1024, 1, 1);
            
            processor.onaudioprocess = (e) => {
                let inputData = e.inputBuffer.getChannelData(0);
                let pcm16 = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    pcm16[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                }
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(pcm16.buffer);
                }
            };
            source.connect(processor);
            processor.connect(audioCtx.destination);
        }

        let nextStartTime = 0;
        function playAudioChunk(arrayBuffer) {
            if (!audioCtx) return;
            let int16View = new Int16Array(arrayBuffer);
            let f32Buffer = audioCtx.createBuffer(1, int16View.length, 24000);
            let channelData = f32Buffer.getChannelData(0);
            for (let i = 0; i < int16View.length; i++) {
                channelData[i] = int16View[i] / 32768.0;
            }
            let source = audioCtx.createBufferSource();
            source.buffer = f32Buffer;
            source.connect(audioCtx.destination);
            let now = audioCtx.currentTime;
            if (nextStartTime < now) nextStartTime = now;
            source.start(nextStartTime);
            nextStartTime += f32Buffer.duration;
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(HTML_CONTENT)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = genai.Client(api_key="AIzaSyC6qX10iQ5bY6fJmlu2lqDQ5vCA_YnyO1M")
    model_id = "gemini-3.1-flash-live-preview"
    
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(parts=[types.Part(text="You are Jenny, Pierre's voice-first trading assistant. Keep responses ultra-concise and market focused.")]),
        tools=[types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name="query_portfolio_db",
                description="Queries database watchlist for a specific ticker to pull position metadata.",
                parameters={"type": "OBJECT", "properties": {"ticker": {"type": "STRING"}}, "required": ["ticker"]}
            )
        ])]
    )

    async with client.aio.live.connect(model=model_id, config=config) as session:
        
        async def send_to_google():
            while True:
                try:
                    data = await websocket.receive_bytes()
                    await session.send_realtime_input(audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000"))
                except WebSocketDisconnect:
                    break
                except Exception:
                    await asyncio.sleep(0.01)

        async def receive_from_google():
            import base64
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    await websocket.send_json({"type": "state", "value": "speaking"})
                    for part in response.server_content.model_turn.parts:
                        if part.inline_data:
                            b64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                            await websocket.send_json({"type": "audio", "data": b64_audio})
                
                if response.server_content and response.server_content.turn_complete:
                    await websocket.send_json({"type": "state", "value": "listening"})

                if response.tool_call:
                    await websocket.send_json({"type": "state", "value": "crunching"})
                    for call in response.tool_call.function_calls:
                        res = query_portfolio_db(call.args["ticker"])
                        await session.send_tool_response(
                            function_responses=[types.FunctionResponse(name=call.name, id=call.id, response={"result": res})]
                        )

        await asyncio.gather(send_to_google(), receive_from_google())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
