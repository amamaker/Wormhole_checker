import os
import requests
from bs4 import BeautifulSoup
import time
import shutil
import chardet
import glob
import customtkinter
import threading

previous_wh = None
class App(customtkinter.CTk):
    width = 320
    height = 200

    def __init__(self):
        super().__init__()
        self.title("WH Checker")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(width=False, height=False)
        self.attributes("-topmost", True)
        self.thread = None
        self.running = False

        # main window
        self.main_frame = customtkinter.CTkFrame(self,  width=500, height=300)
        self.main_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 20), sticky="nsew")
        self.main_label = customtkinter.CTkLabel(self.main_frame, width=200, height=50, text='Click start,to start', font=customtkinter.CTkFont(size=12, weight="bold"))
        self.main_label.grid(row=0, column=0, padx=(50, 50), pady=(30, 30), sticky="nsew")
        self.start_btn = customtkinter.CTkButton(self.main_frame, text='Start', command=self.start_cycle)
        self.start_btn.grid(row=1, column=0, padx=(10, 10), pady=(0, 5), sticky="ew")
        self.stop_btn = customtkinter.CTkButton(self.main_frame, text='Stop', command=self.stop_cycle)
        self.stop_btn.grid(row=2, column=0, padx=(10, 10), pady=(0, 10), sticky="ew")

    log_folder = r'C:\Users\korsu\Documents\EVE\logs\Chatlogs'

    def request_wh(self, WH):
        url = f"https://evewh.ru/{WH}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            element_class_1 = "info_hl"
            element_class_2 = "static_name"
            value2_list = []
            value1 = soup.find(class_=element_class_1).text

            for element in soup.find_all(class_=element_class_2, limit=2):
                value2 = element.text
                if len(value2) <= 30:
                    value2_list.append(value2)
            summary = f'System: {WH}\nClass: {value1}\nStatic: {", ".join(value2_list)}'
            self.main_label.configure(text=f'{summary}')
        else:
            print(f"Request error {url}. Code: {response.status_code}")
        print(f"Success.\n {summary}")

    def check_wh(self, path):
        global previous_wh
        os.system(f"rsync -r --update {path}")
        os.system(f"rsync -r --update")
        folder_path = path
        files = glob.glob(os.path.join(folder_path, 'Local_*'))
        files.sort(key=os.path.getctime, reverse=True)
        latest_file = files[0] if files else None

        if latest_file:
            shutil.copy(latest_file, 'log.txt')

            with open('log.txt', 'rb') as rawdata:
                result = chardet.detect(rawdata.read())
                encoding = result['encoding']

            with open('log.txt', 'r', encoding=encoding) as file:
                last_two_lines = [line.rstrip('\n') for line in file.readlines()[-1:]]

            found_word = None
            for line in reversed(last_two_lines):
                words = line.split()
                for word in reversed(words):
                    if word.startswith('J') and len(word) == 7:
                        found_word = word
                        break

            if found_word is not None:
                if found_word != previous_wh:
                    print(f"Found: {found_word}")
                    self.request_wh(found_word)
                    previous_wh = found_word
                else:
                    previous_wh = found_word
                    print("Change not exist")
            else:
                self.main_label.configure(text=f'Wormhole not found')
                print("Wormhole not found in log")
            os.remove('log.txt')
        else:
            self.main_label.configure(text=f'Local log not found')
            print("Local log not found.")

    def cycle(self):
        while self.running:
            self.check_wh(self.log_folder)
            time.sleep(5)
    def start_cycle(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.cycle)
            self.thread.start()
            print("Cycle started.")

    def stop_cycle(self):
        if self.running:
            self.running = False
            self.thread.join()
            self.main_label.configure(text=f'Click start,to start')
            print("Cycle stopped.")


if __name__ == "__main__":
    app = App()
    app.mainloop()