import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from config.db_config import get_connection

def get_machine_data(page=1, page_size=50):
    offset = (page - 1) * page_size

    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT
        `Target Model`,
        `Development Model`,
        `Initial Model`,
        `Circuit PIC`,
        `Structure`,
        `Part`,
        `Tool Option`,
        `HW Option`,
        `PCB Check`,
        `Confirmation`,
        `Additional Remark`,
        `Final`,
        `Year`
    FROM hw_dept.bom_management_db
    LIMIT %s OFFSET %s
    """
    #WHERE `Circuit PIC` LIKE '%%Ahmad Ifandi%%'

    cursor.execute(query, (page_size, offset))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_total_count():
    """
    Mengambil total jumlah row di tabel
    Digunakan untuk menghitung total page pagination
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM hw_dept.bom_management_db")
    # WHERE `Circuit PIC` LIKE '%%Ahmad Ifandi%%'
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result["total"]


if __name__ == "__main__":
    get_machine_data()
    print(result)