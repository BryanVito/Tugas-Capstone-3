# prompts.py
# Tujuan: mengambil prompt dari Langfuse (bukan ditulis di dalam kode).
#
# Kenapa prompt ada di Langfuse (Session 17, "Prompt Management"):
#   - Ganti prompt tanpa mengubah kode dan tanpa deploy ulang
#   - Ada riwayat versi (v1, v2, ...) dan bisa kembali ke versi lama
#   - Aturan capstone: SEMUA prompt harus ada di Langfuse, dan Langfuse dibuka di video
#
# Teks prompt yang pertama kali diunggah ada di 08_upload_prompts_to_langfuse.py.
# Setelah itu, prompt bisa diedit langsung di website Langfuse (menu Prompts).

import config
from langfuse import get_client


def load_prompt(prompt_name, **variables):
    """Mengambil satu prompt dari Langfuse (versi berlabel 'production'),
    lalu mengisi variabel {{nama}} di dalamnya.

    Contoh: load_prompt("capstone-film-agent", dialect="sqlite", top_k="5")
    """
    config.check_keys(["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])
    langfuse = get_client()

    try:
        prompt = langfuse.get_prompt(prompt_name, label=config.PROMPT_LABEL, type="text")
    except Exception as error:
        raise RuntimeError(
            "Prompt '" + prompt_name + "' tidak bisa diambil dari Langfuse.\n"
            "Kemungkinan: (1) belum diunggah -> jalankan: python 08_upload_prompts_to_langfuse.py\n"
            "             (2) kunci atau LANGFUSE_HOST salah -> jalankan: python 01_test_connection.py\n"
            "Pesan asli: " + str(error)
        ) from error

    # compile() mengganti {{dialect}}, {{top_k}}, dst dengan nilai yang kita kirim
    return prompt.compile(**variables)
