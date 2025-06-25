import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import locale
import sympy as sp
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')


class FuzzyInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Fuzzy Distribution Raskin")

        # Ukuran layar penuh
        screen_width, screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Load data
        self.df = pd.read_excel("Laporan Tahunan.xlsx", header=2)
        self.df = self.df[:10]

        # Inisialisasi nilai
        self.rice = 0
        self.people = 0
        self.raskin = 0

        # Container kiri dan kanan
        self.container_left = tb.Frame(self.root, width=screen_width/2)
        self.container_right = tb.Frame(self.root, width=screen_width/2)
        self.container_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.container_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Variabel teks metode fuzzy
        self.text_var = tb.StringVar(value="Silakan pilih metode fuzzy")
        data = self.get_fuzzy_data()
        def set_metode(nama_metode):
            self.text_var.set(f"{nama_metode}")
        self.text_var = tb.StringVar(value=data["help"])

        # ==================== NAVBAR ====================
        navbar_frame = tb.Frame(self.container_left, height=50, bootstyle="primary")
        navbar_frame.pack(fill="x", padx=5, pady=5)

        button_frame = tb.Frame(navbar_frame)
        button_frame.pack(fill="x", expand=True, padx=10)

        # Konfigurasi kolom grid: 3 kolom sama lebar
        button_frame.columnconfigure((0, 1, 2), weight=1)

        # Tombol navbar di kiri, tengah, dan kanan
        tb.Button(button_frame, text="Help", bootstyle="solid", command=lambda: set_metode(data['help'])).grid(row=0, column=0, sticky="nsew")
        tb.Button(button_frame, text="Tsukamoto", bootstyle="solid", command=lambda: set_metode(data['tsukamoto'])).grid(row=0, column=1, sticky="nsew")
        tb.Button(button_frame, text="Mamdani", bootstyle="solid", command=lambda: set_metode(data['mamdani'])).grid(row=0, column=2, sticky="nsew")

        # ==================== KONTEN KIRI ====================
        # Visualisasi Fungsi Keanggotaan
        visual_box = tb.LabelFrame(
            self.container_left,
            text="Visualisasi Fungsi Keanggotaan",
            bootstyle="info",
            height=600  # << TINGGI MAKSIMAL
        )
        visual_box.pack(fill="x", padx=3, pady=3)  # Hapus expand=True
        visual_box.pack_propagate(False)  # Cegah frame menyesuaikan tinggi otomatis


        button_vis_frame = tb.Frame(visual_box)
        button_vis_frame.pack(pady=5)

        tb.Button(button_vis_frame, text="Pengadaan",         bootstyle="outline-info", command=lambda:self.visualisasi()).pack(side="left", padx=5)
        tb.Button(button_vis_frame, text="Penduduk Miskin",   bootstyle="outline-info", command=lambda:self.visualisasi(col_name='Jumlah Penduduk Miskin (Jt)')).pack(side="left", padx=5)
        tb.Button(button_vis_frame, text="Penyaluran",        bootstyle="outline-info", command=lambda: self.visualisasi(col_name='Penyaluran Raskin / Rastra')).pack(side="left", padx=5)

        # Placeholder area untuk grafik
        self.plot_area = tb.Frame(visual_box, bootstyle="secondary")
        self.plot_area.pack(fill="both", expand=True, padx=8, pady=8)
        self.visualisasi()

        # ==================== INPUT ====================
        input_frame = tb.LabelFrame(self.container_left, text="Input Data", bootstyle="info")
        input_frame.pack(fill="both", padx=5, pady=5)

        self.input_pengadaan = self.make_input(input_frame, "Pengadaan Beras PSO (Ton):", default_value="Masukkan nilai pengadaan beras PSO setidaknya 2,000,000")
        self.input_rakyat    = self.make_input(input_frame, "Jumlah Penduduk Miskin (Jt):", default_value="Masukkan jumlah penduduk miskin setidaknya 25.00")
        self.output          = self.make_input(input_frame, "Penyaluran Raskin / Rastra (Ton):")
        self.output.config(state='readonly')

        # Pilih metode fuzzy
        tb.Label(input_frame, text="Pilih Metode Fuzzy:").pack(anchor="w", padx=5, pady=(10, 0))
        self.method_var = tk.StringVar(value="Tsukamoto")
        tb.Combobox(input_frame, textvariable=self.method_var, values=["Tsukamoto", "Mamdani"], state="readonly").pack(fill="x", padx=5, pady=5)

        # Tombol jalankan
        tb.Button(input_frame, text="Jalankan Fuzzy", bootstyle="primary", command=self.jalankan_fuzzy).pack(pady=10)

        # ==================== KONTEN KANAN ====================
        result_frame = tb.LabelFrame(self.container_right, text="Penjelasan Bantuan", bootstyle="secondary")
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)
        result_frame.pack_propagate(False)

        tb.Label(result_frame, textvariable=self.text_var, wraplength=600, justify="left", bootstyle="primary").pack(fill="both", padx=10, pady=10)


    def get_fuzzy_data(self):
        fuzzy = {
            'tsukamoto':'Fuzzy Tsukamoto merupakan salah satu metode dalam fuzzy logic yang cara pengambilan keputusannya dengan memberikan output crisp yang dapat memudahkan dalam mengidentifikasi hubungan antara input dan juga output. Pada metode ini setiap aturan IF - THEN harus direpresentasikan dengan satu atau lebih himpunan fuzzy. kelebihannya yaitu mampu bekerja dengan informasi yang bersifat kualitatif, tidak akurat, dan ambigu. Fuzzy tsukamoto biasanya digunakan untuk mengatasi situasi pengambilan keputusan yang kompleks dan setiap output dari aturan IF - THEN menyajikan himpunan fuzzy yang memiliki sifat monton. metode ini menghasilkan output yang tegas sehingga memudahkan dalam identifikasi hubungan antara input dan output. ',
            'mamdani':'Fuzzy Mamdani merupakan salah satu metode fuzzy logic yang cara penyelesaiannya melibatkan beberapa langkah penting dalam suatu pemrograman dan desain suatu sistem pengendalian untuk pengambilan keputusan. Fuzzy mamdani mengambil keputusan dengan menggunakan variabel fuzzy input dimana variabel ini akan mewakili input dari sistem yang akan dievaluasi oleh aturan - aturan fuzzy untuk mendapatkan hasil yang sesuai. Dalam logika fuzzy mamdani, aturan fuzzy didefinisikan dalam bentuk “IF - THEN” dimana setiap aturan IF maka dihubungkan dengan tindakan THEN. Fuzzy Mamdani juga merupakan metode yang pertama kali dibangun dan berhasil diterapkan dalam rancang bangun system. Pembentukan himpunan fuzzy pada metode mamdani baik variabel input maupun output biasanya dibagi menjadi satu atau lebih himpunan fuzzy. Metode fuzzy mamdani dikenal sebagai metode yang mampu menangani masalah ketidakpastian dan keraguan untuk pengambilan keputusan dengan cara mengkonversi inputan yang bersifat kualitatif dan output yang lebih terukur. ',
            'help':'Masukkan nilai pengadaan beras PSO dan jumlah penduduk miskin untuk mendapatkan estimasi penyaluran Raskin / Rastra. Pilih metode fuzzy yang diinginkan (Tsukamoto atau Mamdani) untuk menjalankan perhitungan. Masukkan nilai pengadaan beras PSO setidaknya 2,000,000 dan jumlah penduduk miskin setidaknya 25.00. Hal tersebut diperlukan untuk menyesuaiakan dengan data yang ada pada laporan tahunan. Setelah itu, klik tombol "Jalankan Fuzzy" untuk mendapatkan estimasi penyaluran Raskin / Rastra. Hasil estimasi akan ditampilkan di bawah inputan.',
        }

        return fuzzy
    
    def make_box(self, parent, title, fill_mode="both", expand=True):
        box = tb.Frame(parent, width=600, height=180, bootstyle="secondary")
        box.pack(fill=fill_mode, expand=expand, padx=5, pady=5)

        # Label dalam box harus di-pack
        tb.Label(box, text=title, bootstyle="primary").pack(pady=10)
        return box

    def make_input(self, parent, label_text, default_value=0):
        frame = tb.Frame(parent)
        frame.pack(fill="x", padx=5, pady=5)

        tb.Label(frame, text=label_text).pack(side="left")
        var = tk.StringVar(value=str(default_value))
        entry = tb.Entry(frame, textvariable=var)
        entry.pack(side="right", fill="x", expand=True)
        entry.var = var  # Simpan variabel supaya bisa diakses
        def clear_placeholder(event):
            if entry.var.get() == default_value:
                entry.var.set("")  # Kosongkan text saat pengguna mulai mengetik

        def restore_placeholder(event):
            if entry.var.get() == "":
                entry.var.set(default_value)  # Kembalikan placeholder jika kosong
        
        def format_number(entry):
            """Format angka dengan koma setiap 3 digit."""
            value = entry.var.get().replace(",", "")  # Hapus koma lama sebelum diproses
            if value.isdigit():
                formatted_value = f"{int(value):,}"  # Format angka dengan koma
                entry.var.set(formatted_value)  # Masukkan hasil yang diformat


        entry.bind("<FocusIn>", clear_placeholder)
        entry.bind("<FocusOut>", restore_placeholder)
        entry.bind("<KeyRelease>", lambda e: format_number(entry))
        return entry
    def get_clean_value(self, entry):
        """Mengembalikan angka bersih tanpa koma."""
        value = entry.var.get().replace(",", "")  # Hapus semua koma
        return int(value) if value.isdigit() else float(value)

    def make_label(self, parent, text):
        label = tb.Label(parent, text=text)
        label.pack(pady=5)
        return label
    
    def fuzzy_rendah(self,x, a, b):  # monoton turun
        if x <= a:
            return 1
        elif x >= b:
            return 0
        else:
            return (b - x) / (b - a)

    def fuzzy_tinggi(self,x, a, b):  # monoton naik
        if x <= a:
            return 0
        elif x >= b:
            return 1
        else:
            return (x - a) / (b - a)

    def penyaluran_value_tinggi(self,alpha,a_min ,b_max ):
        value = a_min + (alpha*(b_max - a_min))
        return value

    def penyaluran_value_rendah(self,alpha,a_min ,b_max):
        value = b_max - (alpha*(b_max - a_min))
        return value

    def jalankan_fuzzy(self, *args, method='tsukamoto'):
        pengadaan = float(self.get_clean_value(self.input_pengadaan))
        rakyat    = float(self.get_clean_value(self.input_rakyat))
        # rakyat    = float(self.input_rakyat.var.get())
        metode    = self.method_var.get()
        q1_p, q3_p, low_p, high_p = self.get_quantil(self.df["Pengadaan Beras PSO (Ton)"])
        q1_m, q3_m, low_m, high_m = self.get_quantil(self.df["Jumlah Penduduk Miskin (Jt)"])
        q1_s, q3_s, low_s, high_s = self.get_quantil(self.df["Penyaluran Raskin / Rastra"])

        # Panggil fuzzy logic kamu di sini
        hasil = self.fuzzy_logic(
            x_pengadaan=pengadaan,
            x_rakyat=rakyat,
            v_maks_pengadaan=high_p,
            v_min_pengadaan=low_p,
            v_maks_rakyat=high_m,
            v_min_rakyat=low_m,
            low_s=low_s,
            high_s=high_s,
            fuzzy_method=metode.lower()  # Ambil metode dari tombol yang dipilih
            )
        # Tampilkan hasil ke output (yang readonly)
        self.output.config(state='normal')
        self.output.var.set(f"{hasil:.2f}")
        self.output.config(state='readonly')


    def fuzzy_logic(self,x_pengadaan, x_rakyat, v_maks_pengadaan, v_min_pengadaan, 
                    v_maks_rakyat, v_min_rakyat, low_s, high_s, fuzzy_method):
        # Alpha predikat
        a_pengadaan_tinggi = self.fuzzy_tinggi(x_pengadaan, v_min_pengadaan, v_maks_pengadaan)
        a_pengadaan_rendah = self.fuzzy_rendah(x_pengadaan, v_min_pengadaan, v_maks_pengadaan)
        a_rakyat_tinggi = self.fuzzy_tinggi(x_rakyat, v_min_rakyat, v_maks_rakyat)
        a_rakyat_rendah = self.fuzzy_rendah(x_rakyat, v_min_rakyat, v_maks_rakyat)
        # [A1] IF pengadaan BANYAK And rakyat miskin BANYAK
        # THEN penyaluran Barang BERTAMBAH ;
        alpha1 = min(a_pengadaan_tinggi,a_rakyat_tinggi)
        z1 = self.penyaluran_value_tinggi(alpha1, low_s, high_s)

        # [A2] IF pengadaan SEDIKIT And rakyat miskin SEDIKIT
        # THEN penyaluran Barang BERKURANG ;
        alpha2 = min(a_pengadaan_rendah,a_rakyat_rendah)
        z2 = self.penyaluran_value_rendah(alpha2, low_s, high_s)
        
        # [A3] IF pengadaan SEDIKIT And rakyat miskin BANYAK
        # THEN penyaluran Barang BERKURANG ;
        alpha3 = min(a_pengadaan_rendah,a_rakyat_tinggi)
        z3 = self.penyaluran_value_rendah(alpha3,low_s, high_s)

        # [A4] IF pengadaan BANYAK And rakyat miskin SEDIKIT
        # THEN penyaluran Barang BERTAMBAH ;
        alpha4 = min(a_pengadaan_tinggi,a_rakyat_rendah)
        z4 = self.penyaluran_value_tinggi(alpha4, low_s, high_s)

        #output
        if fuzzy_method == 'tsukamoto':
            output = self.defuzzyfikasi_tsukamoto(alpha1, alpha2, alpha3, alpha4, z1,z2,z3,z4)
        elif fuzzy_method == 'mamdani':
            # tahap 3 mamdani
            # max rendah dan tinggi
            new_alpha_penyaluran_bertambah = max(alpha1, alpha4) # 0.67
            new_alpha_penyaluran_berkurang = max(alpha2, alpha3) # 0.25
            if new_alpha_penyaluran_berkurang < new_alpha_penyaluran_bertambah:
                new_alpha1 = new_alpha_penyaluran_berkurang
                new_alpha2 = new_alpha_penyaluran_bertambah
            else:
                new_alpha1 = new_alpha_penyaluran_bertambah
                new_alpha2 = new_alpha_penyaluran_berkurang


            # komposisi antar aturan
            a1 = self.penyaluran_value_tinggi(new_alpha1, low_s, high_s)
            a2 = self.penyaluran_value_tinggi(new_alpha2, low_s, high_s)
            m1 = self.fungsi_baru_1(new_alpha1,new_alpha2,a1,a2,a1-1,high_s,low_s)
            m2 = self.fungsi_baru_1(new_alpha1,new_alpha2,a1,a2,a2-1,high_s,low_s)
            m3 = self.fungsi_baru_1(new_alpha1,new_alpha2,a1,a2,a2+1,high_s,low_s)


            l1 = a1*new_alpha1
            l2 = ((new_alpha1+new_alpha2) * (a2-a1))/2
            l3 = (high_s - a2) * new_alpha2

            output = self.defuzzyfikasi_mamdani(m1,m2,m3,l1,l2,l3)
        else :
            output = 1
        return output

    def defuzzyfikasi_tsukamoto(self,alpha1, alpha2, alpha3, alpha4, z1,z2,z3,z4):
        numerator = (alpha1 * z1) + (alpha2 * z2) + (alpha3 * z3) + (alpha4 * z4)
        pembagi = alpha1 + alpha2 + alpha3 + alpha4
        return numerator/pembagi

    def fungsi_baru_1(self,alpha1, alpha2, z_min, z_maks, z_input, output_maks, output_mins):
        x = sp.Symbol('x')
        if z_input <= z_min:
            fungsi = alpha1*x
            return sp.integrate(fungsi, (x, 0, z_min))
        elif z_input >= z_maks:
            fungsi = alpha2*x
            return sp.integrate(fungsi, (x, z_maks, output_maks))
        else:
            fungsi = ((x-output_mins)/(output_maks-output_mins))*x

            return sp.integrate(fungsi,(x, z_min, z_maks))
        
    def defuzzyfikasi_mamdani(self,m1,m2,m3,l1,l2,l3):
        numerator = m1+m2+m3
        pembagi = l1+l2+l3
        return numerator/pembagi   

    def get_quantil(self, series):
        series = series.loc[:10]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        min_val = series.min()
        max_val = series.max()
        return q1, q3, min_val, max_val
    
    def buat_fuzzy_from_quantil(self, series):
        q1, q3, min_val, max_val = self.get_quantil(series)
        x = np.linspace(min_val, max_val, 100)

        # Fungsi keanggotaan low dan high
        low = fuzz.trapmf(x, [min_val, min_val, q1, q3])
        high = fuzz.trapmf(x, [q1, q3, max_val, max_val])

        return x, low, high, q1, q3

    def plot_fuzzy_to_box(self, parent_frame, x, low, high, title, q1, q3):
        # 1. Buat figure
        fig = Figure(figsize=(4, 3), dpi=100)

        ax = fig.add_subplot(1, 1, 1)

        # 2. Plot data
        ax.plot(x, low, label="Low", color="blue")
        ax.plot(x, high, label="High", color="red")
        ax.set_title(title, fontsize=10)
        ax.axvline(q1, color='green', linestyle='--', label='Q1')
        ax.axvline(q3, color='orange', linestyle='--', label='Q3')
        ax.tick_params(axis='both', labelsize=8)
        ax.legend(fontsize=8)

        # 3. Tempel ke frame GUI
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="none")

    def clear_current_plot(self):
        # Hapus semua widget dalam frame plot_area
        for widget in self.plot_area.winfo_children():
            widget.destroy()
    
    def get_data_x_low_high(self, col_name):
        x, low, high, q1, q3 = self.buat_fuzzy_from_quantil(self.df[col_name])
        return x, low, high, q1, q3
    
    def visualisasi(self, col_name="Pengadaan Beras PSO (Ton)"):
        self.clear_current_plot()
        x, low, high, q1, q3 = self.get_data_x_low_high(col_name)
        self.plot_fuzzy_to_box(self.plot_area, x, low, high, col_name, q1, q3)

if __name__ == "__main__":
    root = tb.Window(themename="pulse")
    app = FuzzyInterface(root)
    root.mainloop()
