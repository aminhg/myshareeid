"""Template Pesan"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Dapatkan pesan selamat datang"""
    msg = (
        f"🎉 Selamat datang, {full_name}!\n"
        "Anda berhasil mendaftar dan mendapatkan 1 poin.\n"
    )
    if invited_by:
        msg += "Terima kasih telah bergabung melalui tautan undangan, pengundang telah mendapatkan 2 poin.\n"

    msg += (
        "\nBot ini dapat menyelesaikan verifikasi SheerID secara otomatis.\n"
        "Cepat Mulai:\n"
        "/about - Tentang fitur bot\n"
        "/balance - Cek saldo poin\n"
        "/help - Lihat daftar perintah lengkap\n\n"
        "Dapatkan lebih banyak poin:\n"
        "/qd - Check-in harian\n"
        "/invite - Undang teman\n"
        f"Gabung saluran: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Dapatkan pesan tentang"""
    return (
        "🤖 Bot Verifikasi Otomatis SheerID\n"
        "\n"
        "Fitur:\n"
        "- Otomatis menyelesaikan verifikasi siswa/guru SheerID\n"
        "- Mendukung verifikasi Gemini One Pro\n"
        "\n"
        "Cara mendapatkan poin:\n"
        "- Hadiah pendaftaran: 1 poin\n"
        "- Check-in harian: +1 poin\n"
        "- Undang teman: +2 poin/orang\n"
        "- Gunakan Kode Kartu (sesuai aturan kartu)\n"
        f"- Gabung saluran: {CHANNEL_URL}\n"
        "\n"
        "Cara penggunaan:\n"
        "1. Mulai verifikasi di halaman web dan salin tautan verifikasi lengkap\n"
        "2. Kirim /verify diikuti dengan tautan tersebut\n"
        "3. Tunggu proses dan lihat hasilnya\n"
        "\n"
        "Untuk perintah lainnya kirim /help"
    )


def get_help_message(is_admin: bool = False) -> str:
    """Dapatkan pesan bantuan"""
    msg = (
        "📖 Bantuan Bot Verifikasi Otomatis SheerID\n"
        "\n"
        "Perintah Pengguna:\n"
        "/start - Mulai (Daftar)\n"
        "/about - Tentang fitur bot\n"
        "/balance - Cek saldo poin\n"
        "/qd - Check-in harian (+1 poin)\n"
        "/invite - Buat tautan undangan (+2 poin/orang)\n"
        "/use <kode> - Tukar poin menggunakan kode kartu\n"
        f"/verify <link> - Verifikasi Gemini One Pro (-{VERIFY_COST} poin)\n"
        "/help - Lihat pesan bantuan ini\n"
        "/tutorial - Panduan solusi jika verifikasi gagal\n"
    )

    if is_admin:
        msg += (
            "\nPerintah Admin:\n"
            "/addbalance <ID> <poin> - Tambah poin pengguna\n"
            "/block <ID> - Blokir pengguna\n"
            "/white <ID> - Buka blokir pengguna\n"
            "/blacklist - Lihat daftar hitam\n"
            "/genkey <kode> <poin> [kali] [hari] - Buat kode kartu\n"
            "/listkeys - Lihat daftar kode kartu\n"
            "/broadcast <teks> - Kirim pesan siaran ke semua pengguna\n"
        )

    return msg


def get_tutorial_message() -> str:
    """Dapatkan pesan tutorial/bantuan kegagalan"""
    return (
        "📚 **Panduan Solusi Masalah Verifikasi**\n\n"
        "Jika verifikasi gagal, jangan panik! Coba langkah berikut:\n\n"
        "1. **Link Hangus / Kadaluwarsa** 💀\n"
        "   - Link SheerID hanya bisa dipakai **1 kali**.\n"
        "   - Jika gagal sekali, link itu sudah \"hangus/rusak\".\n"
        "   - **Solusi:** Tutup tab, buka lagi halaman penawaran (YouTube/Gemini/dll), dan ambil link verifikasi BARU.\n\n"
        "2. **Limit Verifikasi** 🚫\n"
        "   - Terlalu banyak mencoba dalam waktu singkat bikin SheerID memblokir sementara.\n"
        "   - **Solusi:** Ganti email, ganti browser, atau tunggu 30-60 menit.\n\n"
        "3. **Data Tidak Cocok** 📝\n"
        "   - Pastikan Nama Depan & Belakang di akun target SAMA dengan data yang mungkin Anda input.\n\n"
        "4. **Rotasi Otomatis** 🔄\n"
        "   - Bot otomatis mengganti dokumen (Jadwal/Tuition) dan Kampus (Michigan/UF) setiap kali mencoba.\n"
        "   - **Solusi:** Cukup kirim link baru. Jangan kirim link yang sama berkali-kali.\n\n"
        "💡 **Tips Gacor:**\n"
        "Ambil link baru -> Kirim ke Bot -> Tunggu -> Profit! 🚀"
    )


def get_insufficient_balance_message(current_balance: int) -> str:
    """Dapatkan pesan saldo tidak cukup"""
    return (
        f"Poin tidak cukup! Butuh {VERIFY_COST} poin, saat ini {current_balance} poin.\n\n"
        "Cara mendapatkan poin:\n"
        "- Check-in harian /qd\n"
        "- Undang teman /invite\n"
        "- Gunakan kode kartu /use <kode>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Dapatkan panduan penggunaan perintah verifikasi"""
    return (
        f"Cara penggunaan: {command} <Link SheerID>\n\n"
        "Contoh:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "Cara mendapatkan link verifikasi:\n"
        f"1. Kunjungi halaman verifikasi {service_name}\n"
        "2. Mulai proses verifikasi\n"
        "3. Salin URL lengkap dari bilah alamat browser\n"
        f"4. Kirim menggunakan perintah {command}"
    )
