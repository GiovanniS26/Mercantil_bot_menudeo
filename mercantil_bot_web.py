from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import tkinter as tk

# import os
import time
from tkinter import messagebox
import threading

# Configura las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument(
    "user-data-dir=C:\\Users\\giova\\AppData\\Local\\Google\\Chrome\\User Data"
)
chrome_options.add_argument("profile-directory=Default")  # Usa el perfil predeterminado


# Funciones para los botones
def on_play():
    # Crear y ejecutar un hilo para la tarea
    play_thread = threading.Thread(target=lambda: start_bot())
    play_thread.start()


def open_browser():
    global driver
    # Configura el WebDriver (en este caso, Chrome)
    driver = webdriver.Chrome(options=chrome_options)

    # Abre una página web
    driver.get("https://www30.mercantilbanco.com/login")

    time.sleep(3)


def login(password):
    global driver

    # Localiza el botón por su ID (por ejemplo) y pone la contraseña
    driver.find_element(By.ID, "password").send_keys(password)

    # Localiza el botón que contiene el texto "Iniciar" y hace click()
    driver.find_element(By.XPATH, "//button[text()=' Iniciar ']").click()
    time.sleep(3)


def enter_menudeo():
    dashboard_screen = driver.find_element(
        By.XPATH, "//p[text()=' Cuentas en Moneda Nacional ']"
    )
    if dashboard_screen and bot_status:
        driver.find_element(By.CLASS_NAME, "header-left-menu-toggle").click()
        time.sleep(1)

    mercado_divisas = driver.find_element(
        By.XPATH, "//a[text()=' Mercado de divisas ']"
    )
    if mercado_divisas and bot_status:
        mercado_divisas.click()
        time.sleep(1)

    compra_divisas = driver.find_element(By.XPATH, "//a[text()=' Compra de divisas ']")
    if compra_divisas and bot_status:
        compra_divisas.click()
        time.sleep(2)

def set_amount(amount=None):
    if amount is None or amount == "":
        amount = 20
        
    dolares_button = driver.find_element(By.XPATH, "//p[text()='Dólares']")
    if dolares_button and bot_status:
        dolares_button.click()
        time.sleep(1)
        driver.find_element(
            By.XPATH, "//input[contains(@placeholder, '0,00')]"
        ).send_keys(amount * 100)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()=' Continuar ']").click()
        time.sleep(2)

def start_bot():
    global bot_status, price_entry
    bot_status = True
    update_buttons()  # Actualizar los botones
    print(type(price_entry.get()).__name__)
    open_browser()
    login("Guataparo24*")

    enter_menudeo()
    set_amount(price_entry.get())
    time.sleep(1)
    while (
        (driver.find_element(By.XPATH, "//div[text()='Código 9022']")
        or driver.find_element(By.XPATH, "//div[text()='Código 9021']")) and bot_status
    ):
        driver.find_element(By.XPATH, "//button[text()=' Regresar ']").click()
        enter_menudeo()
        set_amount(price_entry.get())
        time.sleep(1)
    set_account()
    check_buy()
    accept_terms()
    
def set_account():
    if driver.find_element(By.XPATH, "//div[text()='Completa los datos']"):
        driver.find_element(By.XPATH, "//mat-label[text()=' Desde mi cuenta ']").click()
        mat_option = driver.find_element(By.TAG_NAME, "mat-option")
        if mat_option:
            mat_option.click()

        driver.find_element(
            By.XPATH, "//mat-label[text()='Origen de los fondos']"
        ).click()
        mat_option = driver.find_element(
            By.XPATH, "//span[text()='Sueldos Y Salarios']"
        )
        if mat_option:
            mat_option.click()

        driver.find_element(
            By.XPATH, "//mat-label[text()='Motivo de la compra']"
        ).click()
        mat_option = driver.find_element(By.XPATH, "//span[text()='Ahorro']")
        if mat_option:
            mat_option.click()

        driver.find_element(By.XPATH, "//button[text()=' Continuar ']").click()


def check_buy():
    if driver.find_element(By.XPATH, "//div[text()='Verifica tu operación']"):
        driver.find_element(By.XPATH, "//button[text()=' Aceptar ']").click()


def accept_terms():
    if driver.find_element(By.XPATH, "//div[text()='Declaración Jurada']"):
        driver.find_element(By.XPATH, "//input[@type='checkbox']").click()
        driver.find_element(By.XPATH, "//button[text()=' Aceptar ']").click()





def on_stop():
    messagebox.showinfo("Stop", "Se ha detenido la acción.")
    global bot_status
    bot_status = False
    update_buttons()  # Actualizar los botones
    driver.quit()


# Función para actualizar el estado de los botones
def update_buttons():
    if bot_status:
        play_button.config(state="disabled")  # Deshabilitar Play si bot_status es True
        price_entry.config(state="disabled")
        stop_button.config(state="normal")  # Habilitar Stop
    else:
        play_button.config(state="normal")  # Habilitar Play si bot_status es False
        price_entry.config(state="normal")
        stop_button.config(state="disabled")  # Deshabilitar Stop


def validate_input(action, value_if_allowed):
    if action == "1":  # Solo validar cuando se añade texto
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False
    return True


def check_entry(event=None):
    if price_entry.get().strip():
        play_button.config(state=tk.NORMAL)
    else:
        play_button.config(state=tk.DISABLED)


# Función principal
def main():
    global play_button, stop_button, bot_status, driver, price_entry

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

    price_label = tk.Label(root, text="Price:")
    price_label.pack(pady=5)
    price_entry = tk.Entry(root, width=30, validate="key", validatecommand=vcmd)
    price_entry.pack(pady=5)
    # Vincular el evento KeyRelease a la función check_entry
    price_entry.bind("<KeyRelease>", check_entry)

    play_button = tk.Button(
        root,
        text="Play",
        command=lambda: on_play(),
        bg="green",
        fg="white",
        width=10,
        state=tk.DISABLED,  # Deshabilitar inicialmente
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
