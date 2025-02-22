import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import keyboard
import threading
import time
import pygetwindow as gw
import psutil
import webbrowser
import requests

class LuaBindManager:
    APP_VERSION = "Alpha 0.0.3"
    UPDATE_URL = "https://skel.site/binderbot/version.txt"
    DOWNLOAD_URL = "https://skel.site/binderbot"

    def check_for_update(self):
                try:
                    response = requests.get(self.UPDATE_URL, timeout=5)
                    latest_version = response.text.strip()
                    
                    if latest_version > self.APP_VERSION:
                        self.app_status = f"Доступно обновление {latest_version}!"
                        self.root.title(f"BinderBot By SkeL (TG: @XEP_TOHET) | {self.APP_VERSION} | Status: {self.app_status}")
                        
                        if messagebox.askyesno("Обновление", f"Доступна новая версия {latest_version}!\nХотите обновить?"):
                            webbrowser.open(self.DOWNLOAD_URL)
                        else:
                            messagebox.showwarning("Обновление", "Вы используете устаревшую версию.")
                    else:
                        self.app_status = "Актуальная версия"
                        self.root.title(f"BinderBot By SkeL (TG: @XEP_TOHET) | {self.APP_VERSION} | Status: {self.app_status}")
                
                except requests.exceptions.RequestException:
                    self.app_status = "Ошибка проверки обновлений"
                    self.root.title(f"BinderBot By SkeL (TG: @XEP_TOHET) | {self.APP_VERSION} | Status: {self.app_status}")


    def __init__(self, root):
        self.root = root
        self.app_status = "Проверка обновлений..."
        self.root.title(f"BinderBot By SkeL (TG: @XEP_TOHET) | {self.APP_VERSION} | Status: {self.app_status}")
        self.root.geometry("700x900")
        self.root.configure(bg="#1e1e1e")

        self.check_for_update()

        self.binds = []
        self.selected_position = None

        img = Image.open("icon.jpg")
        img = img.resize((32, 32))
        self.icon = ImageTk.PhotoImage(img)
        self.root.iconphoto(True, self.icon)

        self.frame = tk.Frame(root, bg="#1e1e1e")
        self.frame.pack(pady=10, fill="both", expand=True)

        self.btn_add_bind = tk.Button(root, text="Добавить бинд", command=self.add_bind, bg="#4caf50", fg="white", relief="flat", font=("Arial", 12), bd=0)
        self.btn_add_bind.pack(pady=5, fill="x", padx=10)

        self.btn_save = tk.Button(root, text="Сохранить бинды", command=self.save_to_lua, bg="#2196f3", fg="white", relief="flat", font=("Arial", 12), bd=0)
        self.btn_save.pack(pady=5, fill="x", padx=10)

        self.btn_edit = tk.Button(root, text="Редактировать бинды", command=self.edit_binds, bg="#ff9800", fg="white", relief="flat", font=("Arial", 12), bd=0)
        self.btn_edit.pack(pady=5, fill="x", padx=10)

        self.btn_start = tk.Button(root, text="Запустить бинды", command=self.load_and_start_binds, bg="#ff9800", fg="white", relief="flat", font=("Arial", 12), bd=0)
        self.btn_start.pack(pady=5, fill="x", padx=10)

        self.sitetext = tk.Label(root, text="https://skel.site/binderbot", font=("Arial", 7))
        self.sitetext.pack(side="bottom", padx=5)

    def add_bind(self):
        bind_frame = tk.Frame(self.frame, bg="#2e2e2e", pady=5, padx=5, bd=5, relief="ridge")
        bind_frame.pack(fill="x", pady=5, padx=10)

        key_var = tk.StringVar()
        key_entry = tk.Entry(bind_frame, textvariable=key_var, width=10, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
        key_entry.pack(side="left", padx=5)

        actions_frame = tk.Frame(bind_frame, bg="#2e2e2e")
        actions_frame.pack(side="left", padx=5, fill="x", expand=True)

        actions = [tk.StringVar()]
        action_entry = tk.Entry(actions_frame, textvariable=actions[0], width=25, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
        action_entry.pack(pady=2, fill="x")

        def add_action():
            var = tk.StringVar()
            actions.append(var)
            entry = tk.Entry(actions_frame, textvariable=var, width=25, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
            entry.pack(pady=2, fill="x")

        def remove_last_action():
            if actions_frame.winfo_children():
                actions_frame.winfo_children()[-1].destroy()
                if actions:
                    actions[-1].set("")
                    actions.pop()
                else:
                    messagebox.showwarning("Ошибка", "В этом бинде нет действий для удаления")

        btn_add_action = tk.Button(bind_frame, text="+", command=add_action, bg="#ff9800", fg="white", relief="flat", font=("Arial", 10))
        btn_add_action.pack(side="left", padx=5)

        btn_remove_last_action = tk.Button(bind_frame, text="-", command=remove_last_action, bg="#f44336", fg="white", relief="flat", font=("Arial", 10))
        btn_remove_last_action.pack(side="left", padx=5)

        self.binds.append((key_var, actions))

    def save_to_lua(self):
        file_name = simpledialog.askstring("Сохранение", "Введите имя файла:")
        if not file_name:
            return
        file_name += ".lua"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("binds = {}\n\n")
            for key_var, actions in self.binds:
                key = key_var.get()
                action_lines = ", ".join([f'"{a.get()}"' for a in actions if a.get()])
                if key and action_lines:
                    f.write(f'binds["{key}"] = {{{action_lines}}}\n')
        messagebox.showinfo("Сохранено", f"Бинды сохранены в {file_name}")

    def load_and_start_binds(self):
        file_path = filedialog.askopenfilename(title="Выберите файл биндов", filetypes=[("Lua Files", "*.lua")])
        if not file_path:
            return

        binds = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lua_content = f.read()
                binds = self.parse_lua_bind(lua_content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки биндов: {e}")
            return

        def send_message_from_bind(actions):
            for action in actions:
                keyboard.press_and_release('/')
                time.sleep(1)
                keyboard.write(action)
                time.sleep(1)
                keyboard.press_and_release('enter')
                time.sleep(1)

        def get_active_window():
            try:
                return gw.getActiveWindow().title
            except:
                return ""

        def is_roblox_running():
            for process in psutil.process_iter(['name']):
                if "RobloxPlayerBeta.exe" in process.info['name']:
                    return True
            return False

        def on_hotkey_pressed(key, actions):
            if "Roblox" in get_active_window() and is_roblox_running():
                print(f"Горячая клавиша {key} нажата, выполняю бинды...")
                send_message_from_bind(actions)
            else:
                print("Бинды работают только в окне Roblox!")

        for key, actions in binds.items():
            keyboard.add_hotkey(key, lambda key=key, actions=actions: on_hotkey_pressed(key, actions), suppress=True)

        messagebox.showinfo("Запущено", "Бинды активированы")
        threading.Thread(target=keyboard.wait, daemon=True).start()

    def parse_lua_bind(self, lua_content):
        binds = {}
        lines = lua_content.split("\n")
        for line in lines:
            if 'binds["' in line and '"] =' in line:
                key = line.split('["')[1].split('"]')[0]
                actions = line.split("= {")[1].split("}")[0].split(", ")
                actions = [action.replace('"', '').strip() for action in actions]
                binds[key] = actions
        return binds
        
    def edit_binds(self):
        file_path = filedialog.askopenfilename(title="Выберите файл биндов для редактирования", filetypes=[("Lua Files", "*.lua")])
        if not file_path:
            return
        
        self.binds.clear()
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        binds = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lua_content = f.read()
                binds = self.parse_lua_bind(lua_content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки биндов: {e}")
            return
        
        for key, actions in binds.items():
            bind_frame = tk.Frame(self.frame, bg="#2e2e2e", pady=5, padx=5, bd=5, relief="ridge")
            bind_frame.pack(fill="x", pady=5, padx=10)
            
            key_var = tk.StringVar(value=key)
            key_entry = tk.Entry(bind_frame, textvariable=key_var, width=10, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
            key_entry.pack(side="left", padx=5)
            
            actions_frame = tk.Frame(bind_frame, bg="#2e2e2e")
            actions_frame.pack(side="left", padx=5, fill="x", expand=True)
            
            action_vars = []
            for action in actions:
                var = tk.StringVar(value=action)
                action_vars.append(var)
                action_entry = tk.Entry(actions_frame, textvariable=var, width=25, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
                action_entry.pack(pady=2, fill="x")
            
            def add_action():
                var = tk.StringVar()
                action_vars.append(var)
                entry = tk.Entry(actions_frame, textvariable=var, width=25, bg="#444", fg="white", insertbackground="white", relief="flat", font=("Arial", 10))
                entry.pack(pady=2, fill="x")
            
            def remove_last_action():
                if action_vars:
                    action_vars[-1].set("")
                    action_vars.pop()
                else:
                    messagebox.showwarning("Ошибка", "В этом бинде нет действий для удаления")
            
            btn_add_action = tk.Button(bind_frame, text="+", command=add_action, bg="#ff9800", fg="white", relief="flat", font=("Arial", 10))
            btn_add_action.pack(side="left", padx=5)

            btn_remove_last_action = tk.Button(bind_frame, text="-", command=remove_last_action, bg="#f44336", fg="white", relief="flat", font=("Arial", 10))
            btn_remove_last_action.pack(side="left", padx=5)

            self.binds.append((key_var, action_vars))

root = tk.Tk()
app = LuaBindManager(root)
root.mainloop()
