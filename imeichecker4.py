from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import os

# 🔐 Ganti dengan akun kamu
EMAIL = "uremail"
PASSWORD = "upassword"

# Pastikan folder logs tersedia
if not os.path.exists("logs"):
    os.makedirs("logs")

def check_single_imei(imei):
    print(f"\n🔍 Mengecek IMEI: {imei}")
    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    try:
        # 1️⃣ Login Xiaomi
        driver.get("https://account.xiaomi.com/fe/service/login/password")
        time.sleep(2)

        driver.find_element(By.NAME, "account").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(4)

        # 2️⃣ Arahkan ke halaman redeem
        driver.get("https://www.mi.co.id/id/imei-redemption/")
        time.sleep(5)

        # 3️⃣ Isi IMEI dan email
        driver.find_element(By.CSS_SELECTOR, 'input.input__element[placeholder="Silakan masukkan IMEI/SN Anda"]').send_keys(imei)
        driver.find_element(By.CSS_SELECTOR, 'input.input__element[type="email"]').send_keys(EMAIL)

        # 4️⃣ Centang dan klik "Kirim"
        driver.find_element(By.CSS_SELECTOR, 'span.submit__checkmark').click()
        driver.find_element(By.CSS_SELECTOR, 'a.input__action').click()
        print("📩 Kode verifikasi dikirim.")

        # 5️⃣ Tunggu input verifikasi
        verif_input = None
        for _ in range(30):
            try:
                verif_input = driver.find_element(By.XPATH, '//input[@type="text" and contains(@placeholder, "kode verifikasi")]')
                break
            except:
                time.sleep(1)

        if not verif_input:
            print("❌ Gagal menemukan input kode verifikasi.")
            return

        # 6️⃣ Tunggu sampai user input 4 karakter
        print("⌨️ Isi kode verifikasi di browser...")
        while True:
            kode = verif_input.get_attribute("value")
            if len(kode.strip()) == 4:
                print(f"✅ Kode terdeteksi: {kode}")
                break
            time.sleep(0.5)

        # 7️⃣ Klik tombol Lanjut
        driver.find_element(By.CSS_SELECTOR, 'button.submit__button[type="submit"]').click()
        time.sleep(4)

        # 8️⃣ Cek notifikasi GAGAL
        try:
            notif = driver.find_element(By.CSS_SELECTOR, 'main.alert-modal-v4__main span.alert-modal-v4__message')
            msg = notif.text.strip()
            if "Tidak ditemukan aktivitas" in msg:
                print(f"❌ GAGAL: {msg}")
                with open("logs/imei_gagal.txt", "a", encoding="utf-8") as f:
                    f.write(f"{imei} | {EMAIL} | GAGAL: {msg}\n")
                return
        except:
            pass

        # 9️⃣ Cek BERHASIL
        try:
            hadiah = driver.find_element(By.CSS_SELECTOR, 'div.card-item-info__prize-item.prize-item')
            hadiah_nama = hadiah.find_element(By.CLASS_NAME, 'prize-item__type-name').text.strip()
            hadiah_desc = hadiah.find_element(By.CLASS_NAME, 'prize-item__prize-desc').text.strip()

            if "Kupon" in hadiah_nama and "Rp 75.000" in hadiah_desc:
                print(f"🎉 BERHASIL: 4 Bulan Spotify ({hadiah_desc})")
                with open("logs/imei_berhasil.txt", "a", encoding="utf-8") as f:
                    f.write(f"{imei} | {EMAIL} | BERHASIL: 4 Bulan Spotify ({hadiah_desc})\n")
            else:
                print("❓ Hadiah tidak terdeteksi.")
        except:
            print("❌ Tidak ada info hadiah ditemukan.")

        time.sleep(1)
    except Exception as e:
        print(f"🚨 Error saat proses IMEI {imei}: {e}")
    finally:
        driver.quit()

def main():
    # 📂 Baca IMEI dari file
    if not os.path.exists("imeis.txt"):
        print("❌ File 'imeis.txt' tidak ditemukan.")
        return

    with open("imeis.txt", "r") as file:
        imei_list = [line.strip() for line in file if line.strip()]

    for imei in imei_list:
        check_single_imei(imei)
        print("⏳ Istirahat sejenak sebelum lanjut ke IMEI berikutnya...\n")
        time.sleep(2)

    print("✅ Selesai semua IMEI!")

if __name__ == "__main__":
    main()
