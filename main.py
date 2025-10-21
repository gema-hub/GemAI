import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import threading
import json
import time

# =============================
# CONFIGURACIÓN
# =============================
API_URL = "http://by-font.gl.at.ply.gg:23773/chat"  # Tu Playit.gg
SYSTEM_PROMPT = "Eres GemAI, un asistente de IA muy inteligente que siempre habla español."

conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

# =============================
# FUNCIONES
# =============================
def send_message_thread(user_input):
    """
    Función que se ejecuta en un hilo para no bloquear la GUI.
    """
    global conversation
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"Tú: {user_input}\n")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)

    conversation.append({"role": "user", "content": user_input})

    # Mostrar indicador de "pensando"
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, "GemAI está pensando...\n")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)

    start_time = time.time()
    try:
        payload = {"user_input": user_input, "conversation": conversation}
        response = requests.post(API_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        end_time = time.time()
        elapsed = round(end_time - start_time, 2)

        # Quitar "pensando"
        chat_box.configure(state='normal')
        chat_box.delete("end-2l", "end-1l")  # elimina la última línea "Jan está pensando..."
        chat_box.configure(state='disabled')

        if "reply" in data:
            reply = data["reply"]
            conversation[:] = data.get("conversation", conversation)
            chat_box.configure(state='normal')
            chat_box.insert(tk.END, f"GemAI ({elapsed}s): {reply}\n\n")
            chat_box.configure(state='disabled')
            chat_box.see(tk.END)
        else:
            chat_box.configure(state='normal')
            chat_box.insert(tk.END, f"⚠️ Error: {data.get('error','Respuesta inesperada')}\n")
            chat_box.configure(state='disabled')
            chat_box.see(tk.END)

    except requests.exceptions.RequestException as e:
        chat_box.configure(state='normal')
        chat_box.insert(tk.END, f"❌ Error de conexión: {e}\n")
        chat_box.configure(state='disabled')
        chat_box.see(tk.END)

def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return
    entry.delete(0, tk.END)
    # Ejecutar en hilo separado para no congelar la GUI
    threading.Thread(target=send_message_thread, args=(user_input,), daemon=True).start()

# =============================
# INTERFAZ GRÁFICA
# =============================
root = tk.Tk()
root.title("GemAI Chat")
root.geometry("700x500")
root.configure(bg="#f4f4f4")

# Caja de chat
chat_box = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, font=("Arial", 12), bg="#ffffff")
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Entrada de texto
entry_frame = tk.Frame(root, bg="#f4f4f4")
entry_frame.pack(fill=tk.X, padx=10, pady=(0,10))

entry = tk.Entry(entry_frame, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
entry.focus()

send_button = tk.Button(entry_frame, text="Enviar", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                        command=send_message)
send_button.pack(side=tk.RIGHT)

# Enter para enviar
entry.bind("<Return>", lambda event: send_message())

# =============================
# RUN
# =============================
root.mainloop()
