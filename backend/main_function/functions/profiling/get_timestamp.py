
import polars as pl
from datetime import date


def add_time_info(df: pl.DataFrame) -> pl.DataFrame:
    """
    Adds or updates the time_info column based on bom_delay_count.

    Kategori:
    - Normal  : < 7 hari
    - Urgent  : 7 - 14 hari
    - Overdue : > 14 hari
    - Completed : Jika delay count bernilai strip (-) -> Engineer sudah OK
    """
    # 1. Ambil teks asli dari bom_delay_count dan bersihkan spasi
    delay_col = pl.col("bom_delay_count").cast(pl.String).str.strip_chars()
    # 2. Ekstrak khusus angka murni untuk dihitung (jika ada huruf/simbol aneh akan aman)
    delay_int = (
        delay_col
        .str.extract(r"(-?\d+)") # Hanya ambil kelompok angka (mendukung angka minus jika ada)
        .cast(pl.Int32)          # Ubah menjadi integer
        .fill_null(0)            # Jika berupa "+**", NULL, atau string kosong, otomatis jadikan 0
    )

    # 3. Klasifikasikan berdasarkan perhitungan integer yang aman
    return df.with_columns(
        # Tangani dulu yang sudah "Closed" (ditandai dengan "-")
        pl.when(delay_col == "-").then(pl.lit("Completed")) 
        # PENTING: Gunakan .when() (dengan awalan titik), BUKAN pl.when() untuk menyambung!
        .when(delay_int < 7).then(pl.lit("Normal"))
        .when((delay_int >= 7) & (delay_int <= 14)).then(pl.lit("Urgent"))
        .when(delay_int > 14).then(pl.lit("Overdue"))
        .otherwise(pl.lit(None))
        .alias("time_info")
    )


def calculate_bom_delay(df):
    """
    Calculates the bom_delay_count based on bom_release_date and the current date.

    """

    # Define the current date as 2026-09-25
    # current_date = date(2026, 9, 25)
    current_date = date.today()

    # 1. Tentukan kondisi apakah Case SUDAH selesai (Closed).
    # Menggunakan contains("OK") secara case-insensitive untuk menangkap "OK" dan "Self Check Ok".
    # Sisanya (-, NG, Retest, null, dll) dianggap belum selesai.
    is_closed = (
        pl.col("engineer_confirmation").is_not_null() & 
        pl.col("engineer_confirmation").str.to_uppercase().str.contains("OK")
    )
    # 2. Handle mixed date formats using pl.coalesce and strict=False
    parsed_date = pl.coalesce(
        pl.col("bom_release_date").str.to_date("%m/%d/%Y", strict=False),
        pl.col("bom_release_date")
        .str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False)
        .dt.date(),
        pl.col("bom_release_date").str.to_date("%Y-%m-%d", strict=False)
    )

    # 3. Hitung base delay MURNI dari Release Date (tanpa dikurangi 14 hari)
    days_difference = (pl.lit(current_date) - parsed_date).dt.total_days()
    # 4. Update logika penjelasan status agar selaras dengan kategori baru
    bom_delay_status_logic = (
        pl.when(days_difference > 14).then(pl.lit("Overdue (> 2 weeks)"))
        .when(days_difference >= 7).then(pl.lit("Urgent (1-2 weeks)"))
        .when(days_difference < 7).then(pl.lit("Normal (< 1 week)"))
        .otherwise(pl.lit(None))
    )
    # 5. Update kolom pada dataframe
    updated_df = df.with_columns(
        # Jika sudah Closed -> strip (-). Jika belum -> hitung delay
        pl.when(is_closed)
        .then(pl.lit("-"))
        .otherwise(days_difference.cast(pl.String))
        .alias("bom_delay_count"),

        # Update status logic-nya juga
        pl.when(is_closed)
        .then(pl.lit("Case Closed"))
        .otherwise(bom_delay_status_logic)
        .alias("bom_delay_status")
    ).with_columns(
        # Pastikan tidak ada null tersisa
        pl.col("bom_delay_count")
        .fill_null("0")
        .cast(pl.String)
        .alias("bom_delay_count")
    )

    # 7. Add time_info using separate function
    updated_df = add_time_info(updated_df)

    return updated_df