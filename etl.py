import os
import pandas as pd
# from load_db import load_to_mysql
from connection_bd import get_conn_db



EXPECTED_COLS = [
    "First Name","Last Name","Email","Application Date","Country",
    "YOE","Seniority","Technology","Code Challenge Score","Technical Interview Score"
]

def extract_from_csv(file: str, sep: str = ";") -> pd.DataFrame:
    df = pd.read_csv(file, sep=sep)
    #Verifica columnas esperadas (solo alerta, no rompe)
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        print(f"Faltan columnas: {missing}")
    
    return df   

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df["code"]      = pd.to_numeric(df["Code Challenge Score"], errors="coerce")
    df["interview"] = pd.to_numeric(df["Technical Interview Score"], errors="coerce")
    df["YOE"]       = pd.to_numeric(df["YOE"], errors="coerce")
    df["hired"]     = ((df["code"] >= 7) & (df["interview"] >= 7)).astype(int)
    df["full_date"] = pd.to_datetime(df["Application Date"], errors="coerce")
    return df

def build_tables(df: pd.DataFrame):
    dim_date = (df[["full_date"]].dropna().drop_duplicates()
                .assign(year=lambda x: x.full_date.dt.year.astype(int),
                        month=lambda x: x.full_date.dt.month.astype(int),
                        day=lambda x: x.full_date.dt.day.astype(int)))

    dim_country    = pd.DataFrame({"country":    sorted(df["Country"].dropna().unique())})
    dim_technology = pd.DataFrame({"technology": sorted(df["Technology"].dropna().unique())})
    dim_seniority  = pd.DataFrame({"seniority":  sorted(df["Seniority"].dropna().unique())})

    dim_candidate  = (df[["First Name","Last Name","Email","YOE"]]
                      .drop_duplicates(subset="Email")
                      .rename(columns={"First Name":"first_name",
                                       "Last Name":"last_name",
                                       "Email":"email",
                                       "YOE":"yoe"}))

    fact_stage = (df.rename(columns={"Country":"country",
                                     "Technology":"technology",
                                     "Seniority":"seniority"})
                    [["full_date","Email","country","technology","seniority",
                      "code","interview","hired"]]
                  .rename(columns={"Email":"email",
                                   "code":"code_challenge_score",
                                   "interview":"interview_score"}))

    dims = {
        "dim_date": dim_date,
        "dim_country": dim_country,
        "dim_technology": dim_technology,
        "dim_seniority": dim_seniority,
        "dim_candidate": dim_candidate
    }
    return dims, fact_stage




def load_to_mysql(dims, fact_stage, db="hiring_dw"):
    cn = get_conn_db(db)
    cur = cn.cursor()

    def _ins(table, cols, df):
        if df.empty: 
            return
        # 👇 Conversión segura de fechas a tipo date de Python para MySQL
        df = df.copy()
        if "full_date" in df.columns:
            df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce").dt.date
        ph = ", ".join(["%s"]*len(cols))
        sql = f"INSERT IGNORE INTO {table} ({', '.join(cols)}) VALUES ({ph})"
        cur.executemany(sql, df[cols].where(pd.notnull(df), None).values.tolist())

    _ins("dim_country",    ["country"],                          dims["dim_country"])
    _ins("dim_technology", ["technology"],                       dims["dim_technology"])
    _ins("dim_seniority",  ["seniority"],                        dims["dim_seniority"])
    _ins("dim_candidate",  ["first_name","last_name","email","yoe"], dims["dim_candidate"])
    _ins("dim_date",       ["full_date","year","month","day"],   dims["dim_date"])  # ← ya convierte full_date
    cn.commit()

    # ---- Mapas valor→ID (tipos consistentes) ----
    def m(id_col, val_col, table):
        cur.execute(f"SELECT {id_col}, {val_col} FROM {table}")
        return {v: k for k, v in cur.fetchall()}

    date_m  = m("date_id","full_date","dim_date")       # full_date llega como date (OK)
    country = m("country_id","country","dim_country")
    tech    = m("technology_id","technology","dim_technology")
    sen     = m("seniority_id","seniority","dim_seniority")
    cur.execute("SELECT candidate_id, email FROM dim_candidate")
    cand = {v: k for k, v in cur.fetchall()}

    f = pd.DataFrame({
        # 👇 usa .dt.date para empatar con las keys del dict date_m
        "date_id":       pd.to_datetime(fact_stage["full_date"], errors="coerce").dt.date.map(date_m),
        "candidate_id":  fact_stage["email"].map(cand),
        "country_id":    fact_stage["country"].map(country),
        "technology_id": fact_stage["technology"].map(tech),
        "seniority_id":  fact_stage["seniority"].map(sen),
        "code_challenge_score": fact_stage["code_challenge_score"].round(1),
        "interview_score":      fact_stage["interview_score"].round(1),
        "hired":                fact_stage["hired"].astype(int)
    }).dropna()

    cur.executemany("""
        INSERT INTO fact_selection
        (date_id,candidate_id,country_id,technology_id,seniority_id,
         code_challenge_score,interview_score,hired)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, f.values.tolist())
    cn.commit(); cur.close(); cn.close()
    print(f"✅ Cargado fact_selection: {len(f)} filas")



def run_etl(csv_path: str, sep: str = ";"):
    df = extract_from_csv(csv_path, sep)
    df = transform(df)
    dims, fact_stage = build_tables(df)
    load_to_mysql(dims, fact_stage)
    