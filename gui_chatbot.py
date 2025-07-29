import tkinter as tk
from tkinter import filedialog
from chatbot import generate_response, set_uploaded_csv, set_uploaded_text
import PyPDF2

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[
        ("Supported files", "*.csv *.txt *.pdf"),
        ("CSV files", "*.csv"),
        ("Text files", "*.txt"),
        ("PDF files", "*.pdf")
    ])
    if file_path:
        try:
            extension = file_path.split(".")[-1].lower()
            chat_log.config(state=tk.NORMAL) 
            if extension == 'csv':
                set_uploaded_csv(file_path)
                chat_log.insert(tk.END, "📊 CSV uploaded! Ask questions like 'Show me patients with diabetes'.\n", "bot")
            elif extension == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    set_uploaded_text(text)
                    chat_log.insert(tk.END, "📄 Text file uploaded! Type 'summarize file' to summarize it.\n", "bot")
            elif extension == 'pdf':
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    pdf_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    set_uploaded_text(pdf_text)
                    chat_log.insert(tk.END, "📄 PDF uploaded! Type 'summarize file' to summarize it.\n", "bot")
            else:
                chat_log.insert(tk.END, f"⚠️ Unsupported file type: {extension}\n", "bot")
        except Exception as e:
            chat_log.insert(tk.END, f"❌ Error reading file: {str(e)}\n", "bot")
        chat_log.config(state=tk.DISABLED)

def send_message_with_typing():
    msg = entry.get()
    if msg.strip() == "":
        return

    # Insert user's message
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"You: {msg}\n", "user")
    chat_log.insert(tk.END, "Bot: Typing...\n", "bot")  # Temporary typing animation
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)
    entry.delete(0, tk.END)

    # Simulate a short delay
    def display_response():
        chat_log.config(state=tk.NORMAL)
        chat_content = chat_log.get("1.0", tk.END)

        # Remove the "Typing..." line
        lines = chat_content.strip().split('\n')
        if lines and lines[-1] == "Bot: Typing...":
            chat_log.delete("end-2l", "end-1l")  # Delete last line

        # Generate actual response
        response = generate_response(msg)
        chat_log.insert(tk.END, f"Bot: {response}\n\n", "bot")
        chat_log.config(state=tk.DISABLED)
        chat_log.yview(tk.END)

    root.after(1000, display_response)  # 1-second delay

def send_message_without_typing(predefined_msg):
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"You: {predefined_msg}\n", "user")
    response = generate_response(predefined_msg)
    chat_log.insert(tk.END, f"Bot: {response}\n\n", "bot")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)


def send_predefined_message(text):
    entry.delete(0, tk.END)
    send_message_without_typing(text)


def toggle_fullscreen():
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    fullscreen_btn.config(text="🗖" if not is_fullscreen else "🗗")

def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    root.attributes("-fullscreen", False)
    fullscreen_btn.config(text="🗖")

# ---------------- GUI LAYOUT ---------------- #
root = tk.Tk()
root.title("AI Chatbot")
root.attributes('-fullscreen', True)
root.configure(bg="#1e1e1e")
root.bind("<Escape>", exit_fullscreen)

top_bar = tk.Frame(root, bg="#1e1e1e")
top_bar.pack(fill=tk.X)
fullscreen_btn = tk.Button(top_bar, text="🗗", command=toggle_fullscreen, bg="#1e1e1e", fg="white", bd=0)
fullscreen_btn.pack(side=tk.RIGHT, padx=10, pady=5)

chat_log = tk.Text(root, bg="#2e2e2e", fg="white", font=("Arial", 12), wrap=tk.WORD)
chat_log.config(state=tk.DISABLED)
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(fill=tk.X, pady=5)

entry = tk.Entry(bottom_frame, font=("Arial", 14), bg="#3e3e3e", fg="white", insertbackground="white")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
entry.bind("<Return>", lambda event: send_message_with_typing())

upload_btn = tk.Button(bottom_frame, text="➕", font=("Arial", 12), bg="#444", fg="white",
                       command=upload_file, relief=tk.FLAT, width=4)
upload_btn.pack(side=tk.LEFT, padx=5)
send_button = tk.Button(
    bottom_frame, text="Send", font=("Arial", 12),
    bg="#2E8B57", fg="white", command=send_message_with_typing, relief=tk.FLAT
)
send_button.pack(side=tk.LEFT, padx=5)

suggestion_frame = tk.Frame(root, bg="#1e1e1e")
suggestion_frame.pack(pady=5)

suggestions = [
    ("🌦 Get Weather", "get weather"),
    ("📚 Search Wikipedia", "tell me about"),
    ("📊 CSV Data Search", "Show me patients with diabetes")
]

for label, message in suggestions:
    btn = tk.Button(suggestion_frame, text=label, font=("Arial", 12), bg="#3a3a3a", fg="white",
                    padx=20, pady=10, width=25, command=lambda m=message: send_predefined_message(m))
    btn.pack(pady=5)

chat_log.tag_config("user", foreground="skyblue")
chat_log.tag_config("bot", foreground="lightgreen")

is_fullscreen = True
root.mainloop()