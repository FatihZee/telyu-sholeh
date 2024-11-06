def animate_text(index=0):
    canvas.itemconfigure(text_id, text=text[:index+1])
    if index < len(text) - 1:
        window.after(100, animate_text, index+1)