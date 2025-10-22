import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import threading
import time
import json

# ===========================================
# CONFIGURACIÓN
# ===========================================
API_URL = "http://by-font.gl.at.ply.gg:23773/chat"  # Tu API (Playit.gg)
SYSTEM_PROMPT = "Eres GemAI, un asistente avanzado que responde siempre en español."

conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

# ===========================================
# FUNCIONES
# ===========================================
def send_message_thread(user_input):
    """Envía el mensaje sin congelar la interfaz."""
    global conversation
    append_text(f"🧍‍♂️ Tú: {user_input}\n", "user")

    conversation.append({"role": "user", "content": user_input})
    append_text("🤖 GemAI está pensando...\n", "thinking")

    start_time = time.time()

    try:
        payload = {"user_input": user_input, "conversation": conversation}
        response = requests.post(API_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        end_time = time.time()
        elapsed = round(end_time - start_time, 2)

        chat_box.configure(state='normal')
        chat_box.delete("end-2l", "end-1l")
        chat_box.configure(state='disabled')

        if "reply" in data:
            reply = data["reply"]
            conversation[:] = data.get("conversation", conversation)
            append_text(f"💬 GemAI ({elapsed}s): {reply}\n\n", "ai")
        else:
            append_text(f"⚠️ Error: {data.get('error', 'Respuesta inesperada')}\n", "error")

    except requests.exceptions.RequestException as e:
        append_text(f"❌ Error de conexión: {e}\n", "error")


def append_text(text, tag=None):
    """Agrega texto con color y formato."""
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, text, tag)
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)


def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return
    entry.delete(0, tk.END)
    threading.Thread(target=send_message_thread, args=(user_input,), daemon=True).start()

# ===========================================
# INTERFAZ GRÁFICA
# ===========================================
root = tk.Tk()
root.title("GemAI Chat")
root.geometry("750x520")
root.config(bg="#ECEFF1")

# Frame superior (Chat)
chat_frame = tk.Frame(root, bg="#ECEFF1")
chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

chat_box = scrolledtext.ScrolledText(chat_frame, state='disabled', wrap=tk.WORD, 
                                     bg="#FFFFFF", fg="#000000", font=("Segoe UI", 12), relief="flat")
chat_box.pack(fill=tk.BOTH, expand=True)

# Colores para estilos
chat_box.tag_config("user", foreground="#1E88E5")
chat_box.tag_config("ai", foreground="#388E3C")
chat_box.tag_config("error", foreground="#D32F2F")
chat_box.tag_config("thinking", foreground="#616161")

# Frame inferior (entrada + botón)
entry_frame = tk.Frame(root, bg="#ECEFF1")
entry_frame.pack(fill=tk.X, padx=10, pady=(0,10))

entry = tk.Entry(entry_frame, font=("Segoe UI", 13))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
entry.focus()

send_button = tk.Button(entry_frame, text="Enviar 💬", font=("Segoe UI", 11, "bold"), 
                        bg="#4CAF50", fg="white", activebackground="#66BB6A",
                        activeforeground="white", relief="flat", command=send_message)
send_button.pack(side=tk.RIGHT)

# Evento Enter
entry.bind("<Return>", lambda event: send_message())

# ===========================================
# INICIO
# ===========================================
append_text("🤖 GemAI listo para ayudarte.\n\n", "ai")

root.mainloop()
