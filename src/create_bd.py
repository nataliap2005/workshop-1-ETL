from connection_bd import get_conn, get_conn_db


DDL = """
DROP DATABASE IF EXISTS hiring_dw;
CREATE DATABASE hiring_dw;
"""

TABLES = [
    
"""
CREATE TABLE IF NOT EXISTS dim_date (
  date_id    INT AUTO_INCREMENT PRIMARY KEY,
  full_date  DATE NOT NULL UNIQUE,
  year       INT NOT NULL,
  month      TINYINT  NOT NULL,
  day        TINYINT  NOT NULL,
  INDEX idx_date_year_month (year, month),
  INDEX idx_full_date (full_date)
) ENGINE=InnoDB;

""",
"""
CREATE TABLE IF NOT EXISTS dim_country (
  country_id INT AUTO_INCREMENT PRIMARY KEY,
  country    VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;
""",
"""
-- Tecnología
CREATE TABLE IF NOT EXISTS dim_technology (
  technology_id INT AUTO_INCREMENT PRIMARY KEY,
  technology    VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;
""",

"""
CREATE TABLE IF NOT EXISTS dim_seniority (
  seniority_id   INT AUTO_INCREMENT PRIMARY KEY,
  seniority      VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS dim_candidate (
  candidate_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name   VARCHAR(100),
  last_name    VARCHAR(100),
  email        VARCHAR(255) NOT NULL UNIQUE,
  yoe          TINYINT
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS fact_selection (
  selection_id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  date_id                  INT        NOT NULL,
  candidate_id             INT        NOT NULL,
  country_id               INT   NOT NULL,
  technology_id            INT   NOT NULL,
  seniority_id             INT    NOT NULL,
  code_challenge_score     DECIMAL(4,1),
  interview_score          DECIMAL(4,1),
  hired                    TINYINT UNSIGNED NOT NULL DEFAULT 0,
  CONSTRAINT chk_hired_01 CHECK (hired IN (0,1)),

  CONSTRAINT fk_fs_date     FOREIGN KEY (date_id)      REFERENCES dim_date(date_id),
  CONSTRAINT fk_fs_cand     FOREIGN KEY (candidate_id) REFERENCES dim_candidate(candidate_id),
  CONSTRAINT fk_fs_country  FOREIGN KEY (country_id)   REFERENCES dim_country(country_id),
  CONSTRAINT fk_fs_tech     FOREIGN KEY (technology_id)REFERENCES dim_technology(technology_id),
  CONSTRAINT fk_fs_sen      FOREIGN KEY (seniority_id) REFERENCES dim_seniority(seniority_id),

  INDEX ix_fs_date      (date_id),
  INDEX ix_fs_country   (country_id),
  INDEX ix_fs_tech      (technology_id),
  INDEX ix_fs_seniority (seniority_id),
  INDEX ix_fs_hired     (hired)
) ENGINE=InnoDB;
"""
]

def create_db():
    with get_conn() as conn:
        cur = conn.cursor()
        for statement in DDL.split(";"):
            if statement.strip():
                cur.execute(statement)
        conn.commit()
        print("✔ Base de datos eliminada y recreada {hiring_dw}")

    with get_conn_db() as conn:
        cur = conn.cursor()
        for sql in TABLES:
            cur.execute(sql)
        conn.commit()
        print("✔ Tablas creadas.")