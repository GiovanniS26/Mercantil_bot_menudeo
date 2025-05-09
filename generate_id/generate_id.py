import os
import tkinter as tk
import re

def get_android_id():
    resultado = os.popen("adb devices").read()
    lineas = resultado.strip().split('\n')
    
    if len(lineas) > 1:
        # La segunda línea debería contener el dispositivo (si hay alguno conectado)
        dispositivo_linea = lineas[1]
        # Usamos expresión regular para encontrar el código del dispositivo
        match = re.match(r'^([^\s]+)\s+device$', dispositivo_linea)
        if match:
            return match.group(1)
    
    return None

def run_bot():
    global root
    
    print(os.system("adb devices"))
    device_id = get_android_id()
    # Crear ventana principal
    root = tk.Tk()
    root.title("Android ID")
    root.geometry("100x100")
    root.resizable(True, True)

    root.columnconfigure(0, weight=1)
    for i in range(10):
        root.rowconfigure(i, weight=1)

    # Frame de monto de compra
    title_frame = tk.Frame(root)
    title_frame.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

    title_label = tk.Label(
        title_frame, text="Unique ID:", font=("Arial", 10, "bold")
    )
    title_label.pack(anchor="w")
    

    id_label = tk.Label(
        title_frame, text=f"{device_id}", font=("Arial", 10, "bold")
    )
    id_label.pack(anchor="w")


    root.mainloop()


def main():
    run_bot()


if __name__ == "__main__":
    main()
