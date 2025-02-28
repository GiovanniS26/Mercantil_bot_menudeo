import os
import time
import xml.etree.ElementTree as ET
import uiautomator2 as u2
import tkinter as tk
from tkinter import messagebox
import threading
import adbutils

APP_PACKAGE = "com.mercantilbanco.mercantilmovil"
#DEVICE_ID = "pfxg8tb6gqqkrgqs"

# -------------------------
#       LÓGICA DEL BOT
# -------------------------


def is_app_open(d):
    """
    Verifica que la aplicación del banco esté abierta en primer plano.
    """
    try:
        current_app = d.app_current()
        current_package = current_app["package"]
        return current_package == APP_PACKAGE
    except:
        return False


def login(d, password, bot_status):
    """
    Inicia sesión si es que el botón 'Ingresar' está disponible.
    Se encarga de enviar la contraseña si el usuario la especificó.
    """
    if not bot_status:
        return

    # Usamos click_exists con timeout para esperar a que aparezca el botón 'Ingresar'
    if d(text="Ingresar").exists:
        # Buscamos el campo de contraseña (android.widget.EditText)
        password_input = d(className="android.widget.EditText")
        if password_input.wait(timeout=2):  # Espera a que aparezca el EditText
            if password:  # Si el usuario ingresó una contraseña en la interfaz
                password_input.send_keys(password)
            # Hacemos click en 'Ingresar' (por si no lo detectó click_exists anterior)
            d(text="Ingresar").click_exists(timeout=1)

        # Espera breve (tiempo de respuesta del servidor)
        time.sleep(
            2
        )  # <-- Aquí puedes intentar reemplazar con un .wait() de la siguiente vista


def tap_menu_button(d):
    """
    Hace tap en el botón que despliega el menú.
    Actualmente usa coordenadas fijas (clic en 50% ancho, ~90% alto).
    """
    screen_size = d.window_size()
    screen_width = screen_size[0]
    screen_height = screen_size[1]

    # Coordenadas relativas
    rel_x = 540 / screen_width  # 50% del ancho
    rel_y = 2159 / screen_height  # 90% del alto

    # Convertir coordenadas relativas a absolutas
    abs_x = int(rel_x * screen_width)
    abs_y = int(rel_y * screen_height)

    d.click(abs_x, abs_y)


def enter_menudeo(d, bot_status):
    """
    Navega hasta "Operaciones de Menudeo" y luego "Comprar divisas".
    Maneja la validación de "Uuups! Algo ha salido mal..."
    """
    if not bot_status:
        return

    # Si existe el texto 'Operaciones de Menudeo', clic
    if d(text="Operaciones de Menudeo").click_exists(timeout=1):
        pass

    # Ahora revisamos si hay "Comprar divisas"
    if d(text="Comprar divisas").click_exists(timeout=1):
        pass
    # Mientras aparezca el mensaje de error, volvemos a intentar
    while bot_status and (
        d(
            text="¡Uuups! Algo ha salido mal... Intenta realizar esta operación más tarde."
        ).exists
        or d(
            text="¡Vaya! En este momento las Operaciones de Menudeo no se encuentran disponibles."
        ).exists
        or d(text="Comprar divisas").exists
    ):
        try:
            # Clic en 'Aceptar' si aparece
            if d(text="Aceptar").click_exists(timeout=1):
                time.sleep(0.3)

            # Intentar de nuevo "Comprar divisas"
            d(text="Comprar divisas").click_exists(timeout=1)
            time.sleep(1)
        except:
            pass


def set_price(d, bot_status, amount=None):
    """
    Coloca el monto a comprar. Si `amount` es None o '', se asume 20.
    Realiza selección de motivo y presiona Comprar.
    """
    if not bot_status:
        return

    if amount is None or amount == "":
        amount = 20

    # Verificamos que estemos en la pantalla donde se ingresan los datos
    if d(text="Ingresa los datos").exists:
        
        if d(text="Vender USD").exists(timeout=1):
            d(text="Resumen").click_exists(timeout=1)
            return
        # A veces el campo puede estar representado por un text="0,00" o
        # un input distinto según la versión de la app.
        amount_input = d(text="0,00")

        # Caso 1: si no está el input con text="0,00" y tampoco está el botón 'Comprar'
        if (not amount_input.exists) and (not d(text="Comprar").exists):
            # Podrías usar un selector distinto, p.e. un sibling:
            # d(text="Comprar USD").sibling(index=6).set_text(amount)
            # Pero dependerá de cómo se vea tu layout real:
            try:
                d(text="Comprar USD").sibling(index=6).send_keys(str(amount))
                time.sleep(0.2)
                d.press("back")

                try:
                    select_origin = d(text="Producto de venta de inmueble")
                    if not select_origin.exists:
                        # Intentamos un scroll vertical
                        d(scrollable=True).scroll.to(
                            text="Producto de venta de inmueble"
                        )
                    if select_origin.exists:
                        select_origin.click()
                        d(text="Sueldos y salarios").click_exists(timeout=1)

                except:
                    pass
            except:
                pass

        # Caso 2: si existe un input con text="0,00"
        elif amount_input.exists:
            try:
                amount_input.send_keys(str(amount))
                time.sleep(0.2)
                d.press("back")
                try:
                    select_origin = d(text="Producto de venta de inmueble")
                    if not select_origin.exists:
                        # Intentamos un scroll vertical
                        d(scrollable=True).scroll.to(
                            text="Producto de venta de inmueble"
                        )
                    if select_origin.exists:
                        select_origin.click()
                        d(text="Sueldos y salarios").click_exists(timeout=1)

                except:
                    pass
            except:
                pass

            # Buscar la opción "Producto de venta de inmueble", si no está visible, hacer scroll

        # Finalmente, clic en "Comprar"
        if d(text="Comprar").click_exists(timeout=1):
            time.sleep(1)

def accept_declaration(d, bot_status):
    """
    Activa el switch "Acepto la Declaración Jurada" y presiona 'Continuar'.
    """
    if not bot_status:
        return

    declaration = d(text="Acepto la Declaración Jurada")
    if declaration.exists:
        switch = declaration.sibling(className="android.view.ViewGroup", clickable=True)
        if switch.click_exists(timeout=1):
            d(text="Continuar").click_exists(timeout=1)
            time.sleep(1)  # animación


def buy_review(d, bot_status, counters):
    """
    Verifica el resultado de la operación de compra:
    - Si es 'Uuups', incrementa los fallidos.
    - Si es '¡Listo!', incrementa los exitosos.
    - Luego clic en 'Resumen'.
    """
    if not bot_status:
        return

    # "Verifica tu operación"
    if d(text="Verifica tu operación").exists:
        d(text="Aceptar").click_exists(timeout=1)
        time.sleep(2)  # respuesta del servidor

    # Error
    if d(text="¡Uuups! Algo ha salido mal...").exists:
        counters["failed"] += 1
        tap_menu_button(d)
        time.sleep(0.5)

    # Éxito
    elif d.xpath("//*[contains(@text, '¡Listo!')]").exists:
        counters["success"] += 1
        tap_menu_button(d)
        time.sleep(0.5)


# -------------------------
#     INTERFAZ GRÁFICA
# -------------------------


def on_play():
    """
    Crea y lanza un thread para `start_bot` si existe dispositivo conectado.
    """
    global play_thread
    try:
        if device.get() != "Selecciona un dispositivo":
            play_thread = threading.Thread(target=lambda: start_bot(), daemon=True)
            play_thread.start()
        else:
            messagebox.showinfo("Stop", "Error: debes seleccionar un dispositivo.")

    except:
        update_buttons()
        messagebox.showinfo("Stop", "Error: se ha detenido la acción.")


def start_bot():
    """
    Bucle principal del bot, que se repite mientras `bot_status` sea True.
    Se encarga de:
      - Verificar si la app está abierta, y si no, abrirla.
      - Realizar login (si se puede).
      - Tap en el menú (si la pantalla actual no muestra opciones esperadas).
      - Navegar a Menudeo y hacer compra de divisas.
      - Aceptar declaración jurada.
      - Revisar estado de la compra (fallido/éxito).
    """
    global bot_status, price_entry, device, d
    global failed_tries, success_tries
    global failed_tries_label, success_tries_label

    d = u2.connect_usb(device.get())
    d.set_orientation("natural")  # o "portrait"
    bot_status = True
    update_buttons()

    # Contadores para mostrar en la interfaz
    counters = {"failed": failed_tries, "success": success_tries}

    while bot_status:
        # 1. Verificar que la app esté abierta
        if not is_app_open(d):
            d.app_start(APP_PACKAGE)

        # 2. Login (si es posible)
        login(d, password_entry.get(), bot_status)

        # 3. Si no está la pantalla de "Pagos de servicios" pero sí "Resumen financiero",
        #    entonces desplegamos el menú
        if (
            not d(text="Pagos de servicios").exists
            and d(text="Resumen financiero").exists
            and bot_status
        ):
            tap_menu_button(d)

        # 4. Entrar a Menudeo
        enter_menudeo(d, bot_status)

        # 5. Colocar monto
        set_price(d, bot_status, price_entry.get())

        # 6. Aceptar declaración
        accept_declaration(d, bot_status)

        # 7. Verificar resultado de la compra
        buy_review(d, bot_status, counters)

        # Actualizar contadores en la interfaz
        failed_tries = counters["failed"]
        success_tries = counters["success"]
        failed_tries_label.config(text=f"❌ Intentos Fallidos: {failed_tries}")
        success_tries_label.config(text=f"✅ Intentos Exitosos: {success_tries}")

        # 8. Manejo de diálogo de "Atención" (por si aparece)
        if d(text="Atención").exists:
            d(text="Aceptar").click_exists(timeout=2)

        # 8. Manejo de error (por si aparece)
        if d(text="Error code 605").exists or d(text="Unexpected error").exists:
            d(text="OK").click_exists(timeout=1)
            
        # 9. Manejo de error (por si aparece)
        if d(text="Inicia sesión nuevamente").exists:
            d(text="Aceptar").click_exists(timeout=1)


def on_stop():
    """
    Detiene el bot.
    """
    global bot_status
    bot_status = False
    update_buttons()


def update_buttons():
    """
    Habilita/Deshabilita botones según el estado `bot_status`.
    """
    if bot_status:
        play_button.config(state="disabled")
        stop_button.config(state="normal")
    else:
        play_button.config(state="normal")
        stop_button.config(state="disabled")
        
def on_close():
    global bot_status
    bot_status = False
    root.destroy()  # Termina el bucle principal de Tkinter


def validate_input(action, value_if_allowed):
    """
    Valida que el usuario solo introduzca dígitos o vacío en el campo de monto.
    """
    if action == "1":  # Cuando se añade texto
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False
    return True


def toggle_password(entry, button):
    """
    Muestra/oculta la contraseña en el Entry correspondiente.
    """
    if entry.cget("show") == "*":
        entry.config(show="")
        button.config(text="Hide")
    else:
        entry.config(show="*")
        button.config(text="Show")


def update_device_list():
    """
    Actualiza la lista de dispositivos conectados vía ADB.
    """
    global listDevices

    new_devices = adbutils.adb.device_list()
    if len(new_devices) != len(listDevices) or any(
        nd.serial != od.serial for nd, od in zip(new_devices, listDevices)
    ):
        listDevices = new_devices
        menu["menu"].delete(0, "end")

        if listDevices:
            menu.config(state="active")
            for dev in listDevices:
                serial = dev.serial
                menu["menu"].add_command(
                    label=serial, command=lambda s=serial: device.set(s)
                )
            # device.set(listDevices[0].serial)
        else:
            device.set("No hay dispositivos")

    root.after(1000, update_device_list)


# -------------------------
#       MAIN / UI
# -------------------------


def main():
    global play_button, stop_button, bot_status, d, play_thread
    global failed_tries, success_tries, failed_tries_label, success_tries_label
    global price_entry, password_entry, menu
    global device, listDevices, root

    bot_status = False
    failed_tries = 0
    success_tries = 0
    listDevices = []

    # Crear ventana principal
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_close)  # Ejecuta on_close al cerrar la ventana
    root.title("Bot Mercantil")
    root.geometry("350x400")
    root.resizable(True, True)

    root.columnconfigure(0, weight=1)
    for i in range(10):
        root.rowconfigure(i, weight=1)

    # Variables
    device = tk.StringVar(root)
    device.set("Selecciona un dispositivo")

    # Frame selección de dispositivo
    device_frame = tk.Frame(root)
    device_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

    menu_label = tk.Label(device_frame, text="Dispositivo:", font=("Arial", 10, "bold"))
    menu_label.pack(side="top", anchor="w")

    menu = tk.OptionMenu(device_frame, device, "No hay dispositivos")
    menu.config(state="disabled")
    menu.pack(fill="x")

    # Frame de contraseña
    password_frame = tk.Frame(root)
    password_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

    password_label = tk.Label(
        password_frame, text="Contraseña (Opcional):", font=("Arial", 10, "bold")
    )
    password_label.pack(anchor="w")

    password_entry_frame = tk.Frame(password_frame)
    password_entry_frame.pack(fill="x")

    password_entry = tk.Entry(password_entry_frame, width=25, show="*")
    password_entry.pack(side="left", fill="x", expand=True)

    toggle_button = tk.Button(
        password_entry_frame,
        text="Show",
        command=lambda: toggle_password(password_entry, toggle_button),
        width=3,
    )
    toggle_button.pack(side="right")

    password_info = tk.Label(
        password_frame,
        text="Sin contraseña funciona igual, pero si se termina la sesión hay que volver a ingresar manualmente.",
        font=("Arial", 8),
        fg="gray",
        wraplength=320,
        justify="left",
    )
    password_info.pack(anchor="w")

    # Frame de monto de compra
    price_frame = tk.Frame(root)
    price_frame.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

    vcmd = (root.register(validate_input), "%d", "%P")
    price_label = tk.Label(
        price_frame, text="Monto a Comprar:", font=("Arial", 10, "bold")
    )
    price_label.pack(anchor="w")

    price_entry = tk.Entry(price_frame, width=30, validate="key", validatecommand=vcmd)
    price_entry.pack(fill="x")
    price_entry.insert(0, "20")

    price_info = tk.Label(
        price_frame,
        text="Si este campo esta vacío, el monto por defecto será de $20.",
        font=("Arial", 8),
        fg="gray",
        wraplength=320,
        justify="left",
    )
    price_info.pack(anchor="w")

    # Estadísticas de intentos
    stats_frame = tk.Frame(root)
    stats_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

    failed_tries_label = tk.Label(
        stats_frame, text=f"❌ Intentos Fallidos: {failed_tries}", fg="red"
    )
    failed_tries_label.pack(anchor="w")

    success_tries_label = tk.Label(
        stats_frame, text=f"✅ Intentos Exitosos: {success_tries}", fg="green"
    )
    success_tries_label.pack(anchor="w")

    # Frame de botones
    buttons_frame = tk.Frame(root)
    buttons_frame.grid(row=4, column=0, pady=20, padx=10, sticky="ew")

    play_button = tk.Button(
        buttons_frame,
        text="Iniciar",
        command=on_play,
        bg="green",
        fg="white",
        width=10,
        font=("Arial", 10, "bold"),
    )
    play_button.pack(side="left", expand=True, fill="x", padx=5)

    stop_button = tk.Button(
        buttons_frame,
        text="Detener",
        command=on_stop,
        bg="red",
        fg="white",
        width=10,
        font=("Arial", 10, "bold"),
    )
    stop_button.pack(side="right", expand=True, fill="x", padx=5)

    update_buttons()
    root.after(1000, update_device_list)
    root.mainloop()


if __name__ == "__main__":
    main()
