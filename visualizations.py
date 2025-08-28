# import pandas as pd
# import plotly.express as px
# from dash import Dash, dcc, html, dash_table, Input, Output, State, no_update
# from dash.exceptions import PreventUpdate
# import queries_db as q
# from connection_bd import get_engine_db

# # ---------------- Helpers ----------------
# def get_all_countries(db="hiring_dw"):
#     eng = get_engine_db(db)
#     return pd.read_sql("SELECT country FROM dim_country ORDER BY country", eng)["country"].tolist()

# def load_all(focus_countries=None, min_apps=5, top=10, db="hiring_dw"):
#     return {
#         "total_hires": q.total_hires(db),
#         "hire_rate_overall": q.hire_rate_overall(db),
#         "by_tech": q.hires_by_technology(db),
#         "by_year": q.hires_by_year(db),
#         "by_seniority": q.hires_by_seniority(db),
#         "by_country_year": q.hires_by_country_over_years(db, focus=focus_countries or []),
#         "avg_sen": q.avg_scores_by_seniority(db),
#         "avg_tech": q.avg_scores_by_technology(db),
#         "top_countries": q.top_countries_by_hire_rate(db, min_applications=min_apps, top=top)
#     }

# def build_figures(data, focus_note=""):
#     figs = {}
#     df = data["by_tech"].copy()
#     figs["tech"] = px.bar(df, x="technology", y="hires", title="Hires by Technology")
#     df = data["by_year"].copy()
#     figs["year"] = px.line(df, x="year", y="hires", markers=True, title="Hires by Year")
#     df = data["by_seniority"].copy()
#     figs["seniority"] = px.bar(df, x="seniority", y="hires", title="Hires by Seniority")
#     df = data["by_country_year"].copy()
#     title = "Hires by Country Over Years"
#     if focus_note:
#         title += f" — Focus: {focus_note}"
#     figs["country_year"] = px.line(df, x="year", y="hires", color="country", markers=True, title=title)
#     df = data["avg_sen"].copy()
#     df_long = df.melt(id_vars="seniority", value_vars=["avg_code", "avg_interview"],
#                       var_name="score_type", value_name="score")
#     figs["avg_sen"] = px.bar(df_long, x="seniority", y="score", color="score_type",
#                              barmode="group", title="Average Scores by Seniority")
#     df = data["avg_tech"].copy()
#     if len(df) > 20:
#         df = df.sort_values("technology").head(20)
#     df_long = df.melt(id_vars="technology", value_vars=["avg_code", "avg_interview"],
#                       var_name="score_type", value_name="score")
#     figs["avg_tech"] = px.bar(df_long, x="technology", y="score", color="score_type",
#                               barmode="group", title="Average Scores by Technology")
#     return figs

# # ---------------- App factory ----------------
# def create_app():
#     DEFAULT_MIN_APPS = 5
#     DEFAULT_TOP = 10
#     ALL_COUNTRIES = get_all_countries()

#     preferred = ["USA", "Brazil", "Colombia", "Ecuador"]
#     default_focus = [c for c in preferred if c in ALL_COUNTRIES] or ALL_COUNTRIES[:4]

#     DATA = load_all(focus_countries=default_focus, min_apps=DEFAULT_MIN_APPS, top=DEFAULT_TOP)
#     FIGS = build_figures(DATA, focus_note=", ".join(default_focus) if default_focus else "All")

#     app = Dash(__name__)
#     app.title = "Hiring DW Dashboard"

#     def kpi_card(title, value):
#         return html.Div(
#             [html.Div(title, className="kpi-title"), html.Div(value, className="kpi-value")],
#             style={"padding":"12px 16px","border":"1px solid #eee","borderRadius":"10px",
#                    "boxShadow":"0 1px 4px rgba(0,0,0,0.06)","minWidth":"200px","textAlign":"center","flex":"1"}
#         )

#     # -------- Layout (controles movidos debajo de las gráficas) --------
#     app.layout = html.Div([
#         html.H2("Hiring Dashboard"),
#         html.Div("Data Warehouse: hiring_dw", style={"color":"#666","marginBottom":"8px"}),

#         # KPI cards
#         html.Div([
#             kpi_card("Total Hires", f"{DATA['total_hires']:,}"),
#             kpi_card("Hire Rate Global", f"{DATA['hire_rate_overall']:.2%}"),
#         ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"20px"}),

#         # Gráficas
#         html.Div([
#             dcc.Graph(id="fig-tech", figure=FIGS["tech"]),
#             dcc.Graph(id="fig-year", figure=FIGS["year"]),
#             dcc.Graph(id="fig-seniority", figure=FIGS["seniority"]),
#             dcc.Graph(id="fig-country-year", figure=FIGS["country_year"]),
#         ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"16px"}),

#         # ---- Controles AHORA acá (entre gráficas y tabla) ----
#         html.Hr(),
#         html.Div([
#             html.Div([
#                 html.Label("Focus countries (country-over-years)"),
#                 dcc.Dropdown(
#                     id="focus-countries",
#                     options=[{"label": c, "value": c} for c in ALL_COUNTRIES],
#                     value=default_focus,
#                     multi=True,
#                     placeholder="Select countries…"
#                 ),
#             ], style={"width":"320px"}),

#             html.Div([
#                 html.Label("Min. Applications"),
#                 dcc.Input(id="min-apps", type="number", min=1, value=DEFAULT_MIN_APPS, style={"width":"100%"}),
#             ], style={"width":"180px"}),

#             html.Div([
#                 html.Label("Top N Countries"),
#                 dcc.Input(id="top-n", type="number", min=1, value=DEFAULT_TOP, style={"width":"100%"}),
#             ], style={"width":"180px"}),

#             html.Div([
#                 html.Label(" "),
#                 html.Button("Refresh", id="btn-refresh", n_clicks=0, style={"width":"100%","height":"38px"})
#             ], style={"width":"140px","alignSelf":"flex-end"})
#         ], style={"display":"flex","gap":"12px","flexWrap":"wrap","marginTop":"12px","marginBottom":"8px"}),

#         # Tabla
#         html.H3("Top Countries by Hire Rate", style={"marginTop":"12px"}),
#         dash_table.DataTable(
#             id="table-top-countries",
#             columns=[
#                 {"name":"country","id":"country"},
#                 {"name":"hires","id":"hires","type":"numeric"},
#                 {"name":"applications","id":"applications","type":"numeric"},
#                 {"name":"hire_rate","id":"hire_rate","type":"numeric"},
#             ],
#             data=DATA["top_countries"].to_dict("records"),
#             style_table={"overflowX":"auto"},
#             style_cell={"padding":"8px","fontFamily":"system-ui,-apple-system,Segoe UI,Roboto,Arial","fontSize":"14px"},
#             style_header={"fontWeight":"600","backgroundColor":"#f7f7f7"},
#             sort_action="native",
#             page_size=10
#         ),

#         html.Div(id="status", style={"color":"#888","marginTop":"10px"}),
#     ], style={"maxWidth":"1280px","margin":"24px auto","padding":"0 16px"})

#     # ---------------- Callback ----------------
#     @app.callback(
#         [
#             Output("fig-tech","figure"),
#             Output("fig-year","figure"),
#             Output("fig-seniority","figure"),
#             Output("fig-country-year","figure"),
#             Output("fig-avg-sen","figure", allow_duplicate=True),
#             Output("fig-avg-tech","figure", allow_duplicate=True),
#             Output("table-top-countries","data"),
#             Output("status","children"),
#         ],
#         [Input("btn-refresh","n_clicks"), Input("focus-countries","value")],
#         [State("min-apps","value"), State("top-n","value")],
#         prevent_initial_call=True
#     )
#     def refresh_dashboard(n_clicks, focus_countries, min_apps, top_n):
#         try:
#             min_apps = int(min_apps or 5)
#             top_n = int(top_n or 10)
#             focus = focus_countries or []

#             data = load_all(focus_countries=focus, min_apps=min_apps, top=top_n)

#             if data["by_country_year"].empty and focus:
#                 data = load_all(focus_countries=[], min_apps=min_apps, top=top_n)
#                 focus_note = "All (fallback—no matches)"
#             else:
#                 focus_note = ", ".join(focus) if focus else "All"

#             figs = build_figures(data, focus_note=focus_note)
#             status = f"Updated (focus={focus_note}, min_apps={min_apps}, top={top_n})"

#             return (
#                 figs["tech"], figs["year"], figs["seniority"], figs["country_year"],
#                 figs["avg_sen"], figs["avg_tech"],
#                 data["top_countries"].to_dict("records"),
#                 status
#             )
#         except Exception as e:
#             return no_update, no_update, no_update, no_update, no_update, no_update, no_update, f"⚠️ Error: {e}"

#     return app
# visualizations.py
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import queries_db as q
from connection_bd import get_engine_db

# ---------------- Helpers ----------------
def get_all_countries(db="hiring_dw"):
    eng = get_engine_db(db)
    return pd.read_sql("SELECT country FROM dim_country ORDER BY country", eng)["country"].tolist()

def load_all(focus_countries=None, min_apps=5, top=10, db="hiring_dw"):
    focus = focus_countries or []  # lista (o vacío)
    return {
        "total_hires": q.total_hires(db),
        "hire_rate_overall": q.hire_rate_overall(db),
        "by_tech": q.hires_by_technology(db),
        "by_year": q.hires_by_year(db),
        "by_seniority": q.hires_by_seniority(db),
        "by_country_year": q.hires_by_country_over_years(db, focus=focus),
        # 👇 AHORA la tabla también respeta el focus
        "top_countries": q.top_countries_by_hire_rate(db, min_applications=min_apps, top=top, focus=focus),
    }

def build_figures(data, focus_note=""):
    figs = {}
    df = data["by_tech"].copy()
    figs["tech"] = px.bar(df, x="technology", y="hires", title="Hires by Technology")

    df = data["by_year"].copy()
    figs["year"] = px.line(df, x="year", y="hires", markers=True, title="Hires by Year")

    df = data["by_seniority"].copy()
    figs["seniority"] = px.bar(df, x="seniority", y="hires", title="Hires by Seniority")

    df = data["by_country_year"].copy()
    title = "Hires by Country Over Years"
    if focus_note:
        title += f" — Focus: {focus_note}"
    figs["country_year"] = px.line(df, x="year", y="hires", color="country", markers=True, title=title)

    return figs

# ---------------- App factory ----------------
def create_app():
    DEFAULT_MIN_APPS = 5
    DEFAULT_TOP = 10
    ALL_COUNTRIES = get_all_countries()

    preferred = ["USA", "Brazil", "Colombia", "Ecuador"]
    default_focus = [c for c in preferred if c in ALL_COUNTRIES] or ALL_COUNTRIES[:4]

    DATA = load_all(focus_countries=default_focus, min_apps=DEFAULT_MIN_APPS, top=DEFAULT_TOP)
    FIGS = build_figures(DATA, focus_note=", ".join(default_focus) if default_focus else "All")

    app = Dash(__name__)
    app.title = "Hiring DW Dashboard"

    def kpi_card(title, value):
        return html.Div(
            [html.Div(title, className="kpi-title"), html.Div(value, className="kpi-value")],
            style={"padding":"12px 16px","border":"1px solid #eee","borderRadius":"10px",
                   "boxShadow":"0 1px 4px rgba(0,0,0,0.06)","minWidth":"200px","textAlign":"center","flex":"1"}
        )

    # -------- Layout --------
    app.layout = html.Div([
        html.H2("Hiring Dashboard"),
        html.Div("Data Warehouse: hiring_dw", style={"color":"#666","marginBottom":"8px"}),

        # KPI cards
        html.Div([
            kpi_card("Total Hires", f"{DATA['total_hires']:,}"),
            kpi_card("Hire Rate Global", f"{DATA['hire_rate_overall']:.2%}"),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"20px"}),

        # Gráficas
        html.Div([
            dcc.Graph(id="fig-tech", figure=FIGS["tech"]),
            dcc.Graph(id="fig-year", figure=FIGS["year"]),
            dcc.Graph(id="fig-seniority", figure=FIGS["seniority"]),
            dcc.Graph(id="fig-country-year", figure=FIGS["country_year"]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"16px"}),

        # Controles entre gráficas y tabla
        html.Hr(),
        html.Div([
            html.Div([
                html.Label("Focus countries (country-over-years)"),
                dcc.Dropdown(
                    id="focus-countries",
                    options=[{"label": c, "value": c} for c in ALL_COUNTRIES],
                    value=default_focus,
                    multi=True,
                    placeholder="Select countries…"
                ),
            ], style={"width":"320px"}),

            html.Div([
                html.Label("Min. Applications"),
                dcc.Input(id="min-apps", type="number", min=1, value=DEFAULT_MIN_APPS, style={"width":"100%"}),
            ], style={"width":"180px"}),

            html.Div([
                html.Label("Top N Countries"),
                dcc.Input(id="top-n", type="number", min=1, value=DEFAULT_TOP, style={"width":"100%"}),
            ], style={"width":"180px"}),

            html.Div([
                html.Label(" "),
                html.Button("Refresh", id="btn-refresh", n_clicks=0, style={"width":"100%","height":"38px"})
            ], style={"width":"140px","alignSelf":"flex-end"})
        ], style={"display":"flex","gap":"12px","flexWrap":"wrap","marginTop":"12px","marginBottom":"8px"}),

        # Tabla
        html.H3("Top Countries by Hire Rate", style={"marginTop":"12px"}),
        dash_table.DataTable(
            id="table-top-countries",
            columns=[
                {"name":"country","id":"country"},
                {"name":"hires","id":"hires","type":"numeric"},
                {"name":"applications","id":"applications","type":"numeric"},
                {"name":"hire_rate","id":"hire_rate","type":"numeric"},
            ],
            data=DATA["top_countries"].to_dict("records"),
            style_table={"overflowX":"auto"},
            style_cell={"padding":"8px","fontFamily":"system-ui,-apple-system,Segoe UI,Roboto,Arial","fontSize":"14px"},
            style_header={"fontWeight":"600","backgroundColor":"#f7f7f7"},
            sort_action="native",
            page_size=10
        ),

        html.Div(id="status", style={"color":"#888","marginTop":"10px"}),
    ], style={"maxWidth":"1280px","margin":"24px auto","padding":"0 16px"})

    # -------- Callback (sin IDs inexistentes) --------
    @app.callback(
        [
            Output("fig-tech","figure"),
            Output("fig-year","figure"),
            Output("fig-seniority","figure"),
            Output("fig-country-year","figure"),
            Output("table-top-countries","data"),
            Output("status","children"),
        ],
        [Input("btn-refresh","n_clicks"), Input("focus-countries","value")],
        [State("min-apps","value"), State("top-n","value")],
        prevent_initial_call=True
    )
    def refresh_dashboard(n_clicks, focus_countries, min_apps, top_n):
        try:
            min_apps = int(min_apps or 5)
            top_n = int(top_n or 10)
            focus = focus_countries or []

            data = load_all(focus_countries=focus, min_apps=min_apps, top=top_n)

            # Si el gráfico por país queda vacío (nombres no matchean), fallback a All
            if data["by_country_year"].empty and focus:
                data = load_all(focus_countries=[], min_apps=min_apps, top=top_n)
                focus_note = "All (fallback—no matches)"
            else:
                focus_note = ", ".join(focus) if focus else "All"

            figs = build_figures(data, focus_note=focus_note)
            status = f"Updated (focus={focus_note}, min_apps={min_apps}, top={top_n})"

            # la tabla ya viene filtrada por focus desde load_all()
            return (
                figs["tech"], figs["year"], figs["seniority"], figs["country_year"],
                data["top_countries"].to_dict("records"),
                status
            )
        except Exception as e:
            return no_update, no_update, no_update, no_update, no_update, f"⚠️ Error: {e}"

    return app
