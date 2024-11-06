import datetime
import math
import time
import tkinter as tk
from tkinter import messagebox
from playsound import playsound
import os
import requests
import geocoder
import threading
import fitz
from PIL import Image, ImageTk

# Fungsi untuk mendapatkan waktu sholat
def get_prayer_times():
    g = geocoder.ip('me')
    location = g.geojson['features'][0]['properties']['country']
    
    response = requests.get('https://api.aladhan.com/v1/timingsByCity', params={
        'city': location,
        'country': '',
        'method': 5
    })

    if response.status_code == 200:
        data = response.json()
        timings = data['data']['timings']

        prayer_times = {
    'Subuh': timings['Fajr'][:5],   # Ambil jam dan menit awal hingga karakter ke-4 dari string Fajr
    'Dzuhur': timings['Dhuhr'][:5],   # Ambil jam dan menit awal hingga karakter ke-4 dari string Dhuhr
    'Ashar': timings['Asr'][:5],   # Ambil jam dan menit awal hingga karakter ke-4 dari string Asr
    'Maghrib': timings['Maghrib'][:5],   # Ambil jam dan menit awal hingga karakter ke-4 dari string Maghrib
    'Isya': timings['Isha'][:5]   # Ambil jam dan menit awal hingga karakter ke-4 dari string Isha
        }
        

        return prayer_times
    else:
        print('Gagal mendapatkan waktu sholat')
        return None

# Fungsi untuk mengatur alarm sholat
def set_prayer_alarm(prayer_name, prayer_time):
    now = datetime.datetime.now()
    alarm_time = datetime.datetime.strptime(prayer_time, '%Y-%m-%d %H:%M:%S')
    reminder_time = alarm_time - datetime.timedelta(minutes=10)

    while now < reminder_time:
        time.sleep(1)
        now = datetime.datetime.now()

    messagebox.showinfo('Alarm Sholat', 'Tinggalkan kegiatanmu sekarang, bersiaplah untuk sholat')

    while now < alarm_time:
        time.sleep(1)
        now = datetime.datetime.now()

    alarm_time_str = f"{datetime.datetime.now().strftime('%Y-%m-%d')} {prayer_time}"
    messagebox.showinfo('Alarm Sholat', f'Alarm untuk {prayer_name} berbunyi pada waktu {alarm_time_str}')
    playsound(os.path.join('D:/Tugas Besar', 'Adzan.mp3'))
    
# Fungsi untuk menampilkan waktu sholat dalam GUI
def display_prayer_times():
    prayer_times = get_prayer_times()
    
    if prayer_times is not None:
        prayer_time_str = "\n".join([f"{prayer_name}: {prayer_time}" for prayer_name, prayer_time in prayer_times.items()])
        messagebox.showinfo('Waktu Sholat', prayer_time_str)
    else:
        messagebox.showerror('Error', 'Gagal mendapatkan waktu sholat')

# Fungsi untuk menjalankan program alarm
def run_alarm_program():
    prayer_times = get_prayer_times()

    if prayer_times is not None:
        now = datetime.datetime.now()
        current_date = now.strftime('%Y-%m-%d')  # Mendapatkan tanggal saat ini
        next_prayer_name = None
        next_prayer_time = None
        minutes_until_next_prayer = None

        for prayer_name, prayer_time in prayer_times.items():
            alarm_time = datetime.datetime.strptime(f'{current_date} {prayer_time}', '%Y-%m-%d %H:%M')
            if alarm_time > now:
                if next_prayer_time is None or alarm_time < next_prayer_time:
                    next_prayer_name = prayer_name
                    next_prayer_time = alarm_time
                    minutes_until_next_prayer = int((alarm_time - now).total_seconds() / 60)

        if next_prayer_name is not None and minutes_until_next_prayer is not None:
            messagebox.showinfo('Waktu Sholat Selanjutnya', f'Waktu Sholat Selanjutnya: {next_prayer_name}\n{minutes_until_next_prayer} menit lagi')
            threading.Thread(target=set_prayer_alarm, args=(next_prayer_name, str(next_prayer_time))).start()

        else:
            messagebox.showinfo('Waktu Sholat', 'Belum ada waktu sholat selanjutnya')
    else:
        messagebox.showerror('Error', 'Gagal mendapatkan waktu sholat')

def play_adzan():
    adzan_file = os.path.join('D:/Tugas Besar', 'Adzan.mp3')
    playsound(adzan_file)

def update_clock():
    current_time = time.strftime('%H:%M:%S')
    label_clock.config(text=current_time)
    label_clock.after(1000, update_clock)

def calculate_qibla_direction(latitude, longitude):
    # Koordinat Makkah
    makkah_latitude = 21.4225
    makkah_longitude = 39.8262
    
    # Menghitung perbedaan bujur dan lintang
    diff_longitude = math.radians(makkah_longitude - longitude)
    latitude = math.radians(latitude)
    makkah_latitude = math.radians(makkah_latitude)
    
    # Menghitung arah kiblat dalam radian
    y = math.sin(diff_longitude)
    x = math.cos(latitude) * math.tan(makkah_latitude) - math.sin(latitude) * math.cos(diff_longitude)
    qibla_direction = math.degrees(math.atan2(y, x))
    
    # Menormalisasi arah kiblat ke dalam rentang 0-360 derajat
    qibla_direction = (qibla_direction + 360) % 360
    
    return qibla_direction

def get_current_location():
    # Contoh koordinat Jakarta
    latitude = -6.200000
    longitude = 106.816666
    
    return latitude, longitude

def calculate_qibla():
    latitude, longitude = get_current_location()
    qibla_direction = calculate_qibla_direction(latitude, longitude)
    return qibla_direction

def show_qibla_direction():
    qibla_direction = calculate_qibla()
    messagebox.showinfo('Arah Kiblat', f"Arah Kiblat: {qibla_direction:.2f} derajat")

def play_adzan():
    threading.Thread(target=playsound, args=(os.path.join('D:/Tugas Besar', 'Adzan.mp3'),)).start()

# Fungsi untuk mengubah nomor halaman saat tombol prev ditekan
def prev_page():
    global current_page_number
    
    if current_page_number > 1:
        current_page_number -= 1
        show_quran_page()

# Fungsi untuk mengubah nomor halaman saat tombol next ditekan
def next_page():
    global current_page_number
    
    if current_page_number < doc.page_count:
        current_page_number += 1
        show_quran_page()

def show_quran_page():
    global page_entry, current_page_number

    current_page_number = int(page_entry.get())
    if current_page_number >= 1 and current_page_number <= doc.page_count:
        page = doc.load_page(current_page_number - 1)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo = ImageTk.PhotoImage(img)

        # Menghapus gambar sebelumnya jika ada
        if hasattr(show_quran_page, 'canvas'):
            show_quran_page.canvas.delete("all")

        # Membuat jendela baru
        quran_window = tk.Toplevel()
        quran_window.title('Al-Quran')
        quran_window.geometry(f'{pix.width}x{pix.height}')

        # Membuat area tampilan untuk lembaran Al-Quran di jendela baru
        canvas = tk.Canvas(quran_window, width=pix.width, height=pix.height)
        canvas.pack()

        # Menampilkan gambar lembaran Al-Quran di area tampilan
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo
        
        # Menambahkan tombol next dan prev
        prev_button = tk.Button(quran_window, text="Prev", command=prev_page)
        prev_button.pack(side=tk.LEFT)
        
        next_button = tk.Button(quran_window, text="Next", command=next_page)
        next_button.pack(side=tk.RIGHT)
        
        # Menyimpan objek canvas pada fungsi show_quran_page
        show_quran_page.canvas = canvas
    else:
        if hasattr(show_quran_page, 'canvas'):
            show_quran_page.canvas.delete("all")

def open_quran_page():
    # Membuat jendela baru untuk memasukkan nomor halaman
    page_window = tk.Toplevel()
    page_window.title('Baca Al-Qur\'an')

    # Membuat label dan entri untuk halaman di jendela baru
    global page_entry  # Menggunakan variabel global
    page_label = tk.Label(page_window, text='Nomor Halaman:')
    page_label.pack(pady=10)
    page_entry = tk.Entry(page_window)
    page_entry.pack()

    # Membuat tombol untuk menampilkan halaman Al-Quran di jendela baru
    show_button = tk.Button(page_window, text='Tampilkan', command=show_quran_page)
    show_button.pack(pady=10)

def import_file():
    file_path = 'D:/Tugas Besar/coba.py'  # Mengganti dengan path file coba.py yang sesuai
    with open(file_path, 'r') as file:
        code = file.read()
    exec(code)

def animate_text(text, delay):
    if len(text) > 0:
        label.config(text=label.cget("text") + text[0])
        label.after(delay, animate_text, text[1:], delay)

# Membaca file PDF Al-Quran
doc = fitz.open('D:/Tugas Besar/Al-Quran.pdf')
    
# Membaca gambar menggunakan Pillow
image = Image.open('D:/Tugas Besar/Masjid2.png')

# Membuat jendela GUI
window = tk.Tk()
window.title('Aplikasi Tel U Sholeh')
window.geometry('700x400')

# Mengkonversi gambar menjadi format yang dapat ditampilkan di Tkinter
tk_image = ImageTk.PhotoImage(image)

# Membuat label untuk menampilkan gambar
label_image = tk.Label(window, image=tk_image)
label_image.place(x=0, y=0, relwidth=1, relheight=1)

label = tk.Label(window, font=("Arial", 18), pady=20)
label.pack()

# Panggil fungsi animate_text dengan teks "Selamat Datang Di Tel U Sholeh"
animate_text("Selamat Datang Di Tel U Sholeh", 100)

# Membuat label untuk menampilkan jam
label_clock = tk.Label(window, font=('Arial', 18), fg='black')
label_clock.pack(pady=8)

# Memanggil fungsi untuk memperbarui jam secara terus-menerus
update_clock()

btn_display_times = tk.Button(window, text='Tampilkan Waktu Sholat', command=display_prayer_times, fg='black')
btn_display_times.pack(pady=8, anchor='center')

# Membuat tombol untuk menjalankan program alarm
btn_start_alarm = tk.Button(window, text='Waktu Sholat Selanjutnya', command=run_alarm_program, fg='black')
btn_start_alarm.pack(pady=8, anchor='center')

play_button = tk.Button(window, text="Putar Adzan", command=play_adzan)
play_button.pack(pady=8)

# Tombol untuk menghitung arah kiblat
calculate_button = tk.Button(window, text="Hitung Arah Kiblat", command=show_qibla_direction)
calculate_button.pack(pady=8, anchor='center')

# Membuat tombol untuk membuka jendela baru untuk memasukkan nomor halaman
open_page_button = tk.Button(window, text='Baca Al-Qur\'an', command=open_quran_page)
open_page_button.pack(pady=8)

browse_button = tk.Button(window, text='Tuntunan Sholat', command=import_file)
browse_button.pack(pady=8)

# Menjalankan GUI loop
window.mainloop()