def add_message(text, sender):
    bubble = tk.Label(messages_frame,
                      text=text,
                      bg="#2a9d8f" if sender == "user" else "#264653",
                      fg="white",
                      font=("Arial", 12),
                      wraplength=300,
                      justify="left" if sender == "bot" else "right",
                      padx=10,
                      pady=5,
                      bd=0,
                      relief=tk.SOLID)

    bubble.pack(anchor="e" if sender == "user" else "w", padx=10, pady=5)

    # Scroll to bottom
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)