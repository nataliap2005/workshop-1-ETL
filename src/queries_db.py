# src/queries_db.py
import pandas as pd
from connection_bd import get_engine_db

def hires_by_technology(db="hiring_dw"):
    sql = """
    SELECT t.technology, SUM(f.hired) AS hires
    FROM fact_selection f
    JOIN dim_technology t ON f.technology_id = t.technology_id
    GROUP BY t.technology
    ORDER BY hires DESC;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def hires_by_year(db="hiring_dw"):
    sql = """
    SELECT d.year, SUM(f.hired) AS hires
    FROM fact_selection f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year
    ORDER BY d.year;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def hires_by_seniority(db="hiring_dw"):
    sql = """
    SELECT s.seniority, SUM(f.hired) AS hires
    FROM fact_selection f
    JOIN dim_seniority s ON f.seniority_id = s.seniority_id
    GROUP BY s.seniority
    ORDER BY hires DESC;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def hires_by_country_over_years(db="hiring_dw", focus=None):
    where = ""
    if focus:
        in_list = ", ".join([f"'{c}'" for c in focus])
        where = f"WHERE c.country IN ({in_list})"
    sql = f"""
    SELECT d.year, c.country, SUM(f.hired) AS hires
    FROM fact_selection f
    JOIN dim_date d    ON f.date_id = d.date_id
    JOIN dim_country c ON f.country_id = c.country_id
    {where}
    GROUP BY d.year, c.country
    ORDER BY d.year, hires DESC;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def avg_scores_by_seniority(db="hiring_dw"):
    sql = """
    SELECT s.seniority,
           ROUND(AVG(f.code_challenge_score),2) AS avg_code,
           ROUND(AVG(f.interview_score),2)      AS avg_interview
    FROM fact_selection f
    JOIN dim_seniority s ON f.seniority_id = s.seniority_id
    GROUP BY s.seniority
    ORDER BY s.seniority;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def avg_scores_by_technology(db="hiring_dw"):
    sql = """
    SELECT t.technology,
           ROUND(AVG(f.code_challenge_score),2) AS avg_code,
           ROUND(AVG(f.interview_score),2)      AS avg_interview
    FROM fact_selection f
    JOIN dim_technology t ON f.technology_id = t.technology_id
    GROUP BY t.technology
    ORDER BY t.technology;
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)

def top_countries_by_hire_rate(db="hiring_dw", min_applications=5, top=5, focus=None):
    where_countries = ""
    if focus:
        in_list = ", ".join([f"'{c}'" for c in focus])
        where_countries = f"WHERE c.country IN ({in_list})"

    sql = f"""
    SELECT c.country,
           SUM(f.hired) AS hires,
           COUNT(*)     AS applications,
           ROUND(SUM(f.hired)/COUNT(*), 4) AS hire_rate
    FROM fact_selection f
    JOIN dim_country c ON f.country_id = c.country_id
    {where_countries}
    GROUP BY c.country
    HAVING COUNT(*) >= {int(min_applications)}
    ORDER BY hire_rate DESC, applications DESC
    LIMIT {int(top)};
    """
    eng = get_engine_db(db)
    return pd.read_sql(sql, eng)


def total_hires(db="hiring_dw"):
    sql = "SELECT SUM(hired) AS total_hires FROM fact_selection;"
    eng = get_engine_db(db)
    df = pd.read_sql(sql, eng)
    return int(df.iloc[0,0] or 0)

def hire_rate_overall(db="hiring_dw"):
    sql = "SELECT ROUND(SUM(hired)/COUNT(*), 4) AS hire_rate FROM fact_selection;"
    eng = get_engine_db(db)
    df = pd.read_sql(sql, eng)
    return float(df.iloc[0,0] or 0.0)
