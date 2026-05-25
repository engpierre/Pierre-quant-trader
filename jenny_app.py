import asyncio
import threading
import queue
import sqlite3
import pyaudio
import customtkinter as ctk
from google import genai
from google.genai import types

# Premium high-contrast minimalist canvas matching video footprint
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

gui_queue = queue.Queue()
speaker_queue = queue.Queue()

# Global placeholders initialized safely inside the running async runtime thread
async_mic_queue = None
main_loop = None

def query_portfolio_db(ticker: str) -> str:
    try:
        db_path = r'C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE ticker = ?", (ticker.upper(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            gui_queue.put(("transcript", f"🔧 [System matched position metrics for {ticker.upper()}]"))
            return f"Database row for {ticker}: {str(row)}"
        return f"Ticker {ticker} not found."
    except Exception as e:
        return f"Database Error: {str(e)}"

import json
def read_openclaw_report(ticker: str) -> str:
    buffer_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\signal_intel_buffer.json"
    try:
        with open(buffer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("ticker", "").upper() == ticker.upper():
            gui_queue.put(("transcript", f"🔧 [System loaded OpenClaw Intel Report for {ticker.upper()}]"))
            return data.get("flash_intel_report", "No report text found.")
        else:
            return f"The current OpenClaw report in the buffer is for {data.get('ticker', 'UNKNOWN')}, not {ticker}."
    except Exception as e:
        return f"Error reading OpenClaw report: {str(e)}"

# Isolated Hardware Thread 1: Continuous Speaker Output
def isolated_speaker_thread():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True, frames_per_buffer=1024)
    try:
        while True:
            data = speaker_queue.get()
            stream.write(data)
            speaker_queue.task_done()
    except Exception as e:
        gui_queue.put(("transcript", f"[Hardware Error] Speaker failure: {e}"))
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Isolated Hardware Thread 2: Continuous Microphone Input
def isolated_mic_thread():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    try:
        while True:
            data = stream.read(1024, exception_on_overflow=False)
            if main_loop and async_mic_queue:
                main_loop.call_soon_threadsafe(async_mic_queue.put_nowait, data)
    except Exception as e:
        gui_queue.put(("transcript", f"[Hardware Error] Microphone failure: {e}"))
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Isolated Network Loop Core
def run_pipeline():
    async def main():
        global main_loop, async_mic_queue
        main_loop = asyncio.get_running_loop()
        async_mic_queue = asyncio.Queue()  # Safely created inside active running event loop
        
        client = genai.Client(api_key="AIzaSyC6qX10iQ5bY6fJmlu2lqDQ5vCA_YnyO1M")
        model_id = "gemini-3.1-flash-live-preview"
        
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(parts=[types.Part(text=(
                "You are Jenny, Pierre's personal AI trading assistant. Maintain a crisp, professional posture.\n"
                "\nCONDITIONAL ROUTING LOGIC (OPENCLAW SKILL):\n"
                "If the user requests a stock analysis, asks for a 'play' on a ticker, or mentions 'the Swarm':\n"
                "You must activate your OpenClaw Skill. Use the read_openclaw_report tool to read the pre-generated report for that ticker from the workspace and summarize it for the user. "
                "You are strictly a READ-ONLY reporter. You must NEVER execute backend scripts, run prediction code, or attempt to perform the calculations yourself.\n"
                "\nELSE:\n"
                "For any non-stock-related query, operate with your full, existing range of general-purpose tools (Web search, reasoning, etc.) without exception."
            ))]),
            tools=[types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name="query_portfolio_db",
                    description="Queries database watchlist for a specific ticker to pull position metadata.",
                    parameters={"type": "OBJECT", "properties": {"ticker": {"type": "STRING"}}, "required": ["ticker"]}
                ),
                types.FunctionDeclaration(
                    name="read_openclaw_report",
                    description="Reads the pre-generated OpenClaw Flash Intel Report from the local workspace for a specific ticker.",
                    parameters={"type": "OBJECT", "properties": {"ticker": {"type": "STRING"}}, "required": ["ticker"]}
                )
            ])]
        )

        async with client.aio.live.connect(model=model_id, config=config) as session:
            gui_queue.put(("status", "JENNY ONLINE", "#00ffff"))
            
            async def send_mic_loop():
                while True:
                    data = await async_mic_queue.get()
                    await session.send_realtime_input(audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000"))
                    async_mic_queue.task_done()

            async def receive_audio_loop():
                async for response in session.receive():
                    if response.server_content and response.server_content.model_turn:
                        gui_queue.put(("status", "JENNY SPEAKING", "#ff00ff"))
                        for part in response.server_content.model_turn.parts:
                            if part.text:
                                gui_queue.put(("transcript", f"Jenny: {part.text}"))
                            if part.inline_data:
                                speaker_queue.put(part.inline_data.data)
                    
                    if response.server_content and response.server_content.turn_complete:
                        gui_queue.put(("status", "JENNY LISTENING", "#00ffff"))

                    if response.tool_call:
                        gui_queue.put(("status", "CRUNCHING DATA", "#ffff00"))
                        for call in response.tool_call.function_calls:
                            if call.name == "query_portfolio_db":
                                result = query_portfolio_db(call.args["ticker"])
                            elif call.name == "read_openclaw_report":
                                result = read_openclaw_report(call.args["ticker"])
                            else:
                                result = f"Unknown tool: {call.name}"
                                
                            await session.send_tool_response(
                                function_responses=[types.FunctionResponse(name=call.name, id=call.id, response={"result": result})]
                            )

            await asyncio.gather(send_mic_loop(), receive_audio_loop())
            
    asyncio.run(main())

class JennyJarvisUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JENNY SYSTEM CORE")
        self.geometry("500x550")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")

        self.title_label = ctk.CTkLabel(self, text="JENNY SYSTEM INTEGRATION", font=ctk.CTkFont(family="Courier", size=15, weight="bold"), text_color="#3b82f6")
        self.title_label.pack(pady=(35, 5))

        self.orb_node = ctk.CTkButton(
            self, 
            text="🧬", 
            font=ctk.CTkFont(size=44), 
            width=180, 
            height=180, 
            corner_radius=90, 
            fg_color="#121826", 
            hover=False, 
            border_width=4, 
            border_color="#00ffff"
        )
        self.orb_node.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="INITIALIZING HARDWARE LAYER...", font=ctk.CTkFont(family="Courier", size=13, weight="bold"), text_color="#00ffff")
        self.status_label.pack(pady=(5, 15))

        self.chat_display = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Arial", size=13), text_color="#e4e4e7", fg_color="#060910", border_color="#1e293b", border_width=1)
        self.chat_display.pack(padx=25, pady=(0, 25), fill="both", expand=True)
        self.chat_display.insert("end", "[System] Memory mapped queues established.\n")

        self.update_gui()

    def update_gui(self):
        while not gui_queue.empty():
            msg_type, *data = gui_queue.get()
            if msg_type == "status":
                text, color = data
                self.status_label.configure(text=text, text_color=color)
                self.orb_node.configure(border_color=color)
            elif msg_type == "transcript":
                self.chat_display.insert("end", f"{data[0]}\n")
                self.chat_display.see("end")
        self.after(30, self.update_gui)

if __name__ == "__main__":
    threading.Thread(target=isolated_speaker_thread, daemon=True).start()
    threading.Thread(target=isolated_mic_thread, daemon=True).start()
    threading.Thread(target=run_pipeline, daemon=True).start()
    
    app = JennyJarvisUI()
    app.mainloop()
