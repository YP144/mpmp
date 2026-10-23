import pandas as pd
from sqlalchemy import create_engine, text
from utils.link import memberURL


def check_user(userIc: str, userId: str) -> dict:

    engine = create_engine(memberURL)

    print(
        f"[AUTH] Looking up userId={userId!r}, userIc={userIc!r}",
        flush=True
    )

    query = text("""
        SELECT
            "ID",
            "Emp_No",
            "Email",
            "Name",
            "Auth"
        FROM "user_list"
        WHERE LOWER(TRIM("ID")) = LOWER(TRIM(:userId))
          AND LOWER(TRIM("Emp_No")) = LOWER(TRIM(:userIc))
    """)

    df = pd.read_sql(
        query,
        con=engine,
        params={
            "userId": userId,
            "userIc": userIc,
        }
    )

    print(
        f"[AUTH] Matching rows: {len(df)}",
        flush=True
    )

    if df.empty:
        print(
            "[AUTH] USER NOT FOUND",
            flush=True
        )

        return {
            "name": userId,
            "empNo": userIc,
            "email": None,
            "userName": None,
            "user_state": "not exist",
            "auth": "no",
            "authority": "no",
        }

    row = df.iloc[0]

    print(
        f"[AUTH] USER FOUND: "
        f"ID={row['ID']!r}, "
        f"Emp_No={row['Emp_No']!r}, "
        f"Name={row['Name']!r}, "
        f"Auth={row['Auth']!r}",
        flush=True
    )

    auth_value = row["Auth"]

    if auth_value is None or pd.isna(auth_value):
        auth_status = "no"
    elif str(auth_value).strip().upper() in ("Y", "S", "NULL"):
        auth_status = "yes"
    else:
        auth_status = "no"

    return {
        "name": row["ID"],
        "empNo": row["Emp_No"],
        "email": row["Email"],
        "userName": row["Name"],
        "user_state": "exist",
        "auth": auth_status,
        "authority": auth_status,
    }