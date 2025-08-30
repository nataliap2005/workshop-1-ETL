from create_bd import create_db
from etl import run_etl
from visualizations import create_app


def main():
    print("Creando BD/tablas…")
    create_db()
    print("Iniciando ETL")
    run_etl("candidates.csv", ";")
    
    app = create_app()
    app.run(debug=True, port=8050) 

if __name__ == "__main__":
    main()




