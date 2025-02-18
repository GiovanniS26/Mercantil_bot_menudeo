# version 1 para un dispositivo

import os
import time
import xml.etree.ElementTree as ET
import uiautomator2 as u2
import tkinter as tk
from tkinter import messagebox
import threading


APP_PACKAGE = "com.mercantilbanco.mercantilmovil"

# Funciones para controlar el bot

# Verificar que la app del banco esté abierta
def is_app_open():
    try:
        # Obtener información de la aplicación en primer plano
        current_app = d.app_current()
        current_package = current_app['package']
        
        # Verificar si el paquete en primer plano es el de la app
        return current_package == APP_PACKAGE
    except Exception as e:
        return False

# Loguearse en el banco
def login():
    global password_entry, bot_status

    password_input = d(text="Clave de Internet")
    if password_input.exists and bot_status:
        if password_entry.get() is None or password_entry.get() == "":
            bot_status = False
            update_buttons()
        password_input.send_keys(password_entry.get())
        d(text="Ingresar").click()
        time.sleep(2)


# Hacer tap en el botón que despliega el menú
def tap_menu_button():
    screen_size = d.window_size()
    screen_width = screen_size[0]
    screen_height = screen_size[1]

    # Coordenadas relativas

    rel_x = 540 / screen_width  # 50% del ancho
    rel_y = 2159 / screen_height  # 90% del alto
    # Convertir coordenadas relativas a absolutas en tiempo de ejecución
    abs_x = int(rel_x * screen_width)
    abs_y = int(rel_y * screen_height)

    # Hacer tap en las coordenadas calculadas
    d.click(abs_x, abs_y)


# Entrar a Operaciones de Menudeo
def enter_menudeo():
    if (
        d(text="Operaciones de Menudeo").exists
        and not d(text="¡Uuups! Algo ha salido mal...").exists
        and bot_status
    ):
        d(text="Operaciones de Menudeo").click()
        time.sleep(1)
    if d(text="Comprar divisas").exists and bot_status:
        d(text="Comprar divisas").click()
        time.sleep(2)
    while (
        d(
            text="¡Uuups! Algo ha salido mal... Intenta realizar esta operación más tarde."
        ).exists
        or d(
            text="¡Vaya! En este momento las Operaciones de Menudeo no se encuentran disponibles."
        ).exists
    ) and bot_status:
        d(text="Aceptar").click()
        d(text="Comprar divisas").click()
        time.sleep(2)


# Colocar el monto a comprar
def set_price(amount=None):
    if amount is None or amount == "":
        amount = 20
    if d(text="Ingresa los datos").exists and bot_status:
        if d(text="0,00"):
            d(text="0,00").set_text(amount)
            time.sleep(1)
            d.press("back")
            time.sleep(1)

        d.swipe(540, 1800, 540, 500)

        if d(text="Producto de venta de inmueble").exists and bot_status:
            d(text="Producto de venta de inmueble").click()
            d(text="Sueldos y salarios").click()
            d(text="Comprar").click()


# Aceptar juramentacion
def accept_declaration():
    # Localizar el texto "Acepto la Declaración Jurada"
    declaration = d(text="Acepto la Declaración Jurada")
    if declaration.exists and bot_status:
        # Obtener el nodo hermano (hermano siguiente)
        switch = declaration.sibling(className="android.view.ViewGroup", clickable=True)
        if switch.exists and bot_status:

            # Cambiar el estado del Switch
            switch.click()
            d(text="Continuar").click()
            time.sleep(1)


def buy_review():
    global failed_tries, success_tries
    global failed_tries_label, success_tries_label
    if d(text="Verifica tu operación").exists and bot_status:
        d(text="Aceptar").click()
        time.sleep(3)
    if d(text="¡Uuups! Algo ha salido mal...").exists and bot_status:
        failed_tries = failed_tries + 1
        failed_tries_label.config(text=f"Intentos Fallidos: {failed_tries}")
        d(text="Resumen").click()
        time.sleep(1)
    elif d.xpath("//*[contains(@text, '¡Listo!')]").exists and bot_status:
        success_tries = success_tries + 1
        success_tries_label.config(text=f"Intentos Exitosos: {success_tries}")
        d(text="Resumen").click()
        time.sleep(1)


# Funciones para manejo de la interfaz


# Funciones para los botones
def on_play():
    try:
        # Crear y ejecutar un hilo para la tarea
        global play_thread
        play_thread = threading.Thread(target=lambda: start_bot())
        play_thread.start()
    except:
        update_buttons()  # Actualizar los botones
        messagebox.showinfo("Stop", "Error: se ha detenido la acción.")


def start_bot():
    global bot_status, price_entry
    bot_status = True
    update_buttons()  # Actualizar los botones

    while bot_status:
        if not is_app_open():
            d.app_start(APP_PACKAGE)
        login()
        if d(text="Resumen financiero").exists and bot_status:
            tap_menu_button()
        enter_menudeo()
        set_price(price_entry.get())
        accept_declaration()
        buy_review()
        if d(text="Atención").exists:
            d(text="Aceptar").click()


def on_stop():
    global bot_status
    bot_status = False
    update_buttons()  # Actualizar los botones


# Función para actualizar el estado de los botones
def update_buttons():
    if bot_status:
        play_button.config(state="disabled")  # Deshabilitar Play si bot_status es True
        stop_button.config(state="normal")  # Habilitar Stop
    else:
        play_button.config(state="normal")  # Habilitar Play si bot_status es False
        stop_button.config(state="disabled")  # Deshabilitar Stop


def validate_input(action, value_if_allowed):

    if action == "1":  # Solo validar cuando se añade texto
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False
    return True


# Función principal
def main():
    global play_button, stop_button, bot_status, d, play_thread, failed_tries, success_tries
    global price_entry, password_entry, failed_tries_label, success_tries_label

    d = u2.connect()
    # Conexión al dispositivo (automática)
    bot_status = False

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Bot Mercantil")

    # Crear validación
    vcmd = (
        root.register(validate_input),
        "%d",
        "%P",
    )  # %d: acción, %P: valor propuesto

    password_label = tk.Label(root, text="Contraseña:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, width=30, validate="key")
    password_entry.pack(pady=5)

    price_label = tk.Label(root, text="Monto a Comprar:")
    price_label.pack(pady=5)
    price_label = tk.Label(root, text="(Por defecto: $20)")
    price_label.pack(pady=5)
    price_entry = tk.Entry(root, width=30, validate="key", validatecommand=vcmd)
    price_entry.pack(pady=5)

    failed_tries = 0
    failed_tries_label = tk.Label(root, text=f"Intentos Fallidos: {failed_tries}")
    failed_tries_label.pack(pady=5)

    success_tries = 0
    success_tries_label = tk.Label(root, text=f"Intentos Exitosos: {success_tries}")
    success_tries_label.pack(pady=5)

    # Botones para activar y detener
    play_button = tk.Button(
        root,
        text="Play",
        command=on_play,
        bg="green",
        fg="white",
        width=10,
    )
    play_button.pack(pady=10)

    stop_button = tk.Button(
        root, text="Stop", command=on_stop, bg="red", fg="white", width=10
    )
    stop_button.pack(pady=10)

    # Configurar el estado inicial de los botones
    update_buttons()

    # Iniciar el bucle principal
    root.mainloop()


# Verificar si el script se está ejecutando directamente
if __name__ == "__main__":
    main()
