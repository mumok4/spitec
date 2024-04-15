from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from enum import Enum
from .languages import languages
from datetime import datetime, date, timedelta
from ..processing import DataProducts, DataProducta


language = languages["en"]


class ProjectionType(Enum):
    MERCATOR = "mercator"
    ROBINSON = "robinson"
    ORTHOGRAPHIC = "orthographic"


class PointColor(Enum):
    SILVER = "silver"
    RED = "red"
    GREEN = "green"


def create_layout(
    site_map: go.Figure,
    site_data: go.Figure,
    projection_radio: dbc.RadioItems,
    time_slider: dcc.RangeSlider,
    checkbox_site: dbc.Checkbox,
    selection_data_types: dbc.Select,
) -> html.Div:
    left_side = _create_left_side(site_map, projection_radio, checkbox_site)
    data_tab = _create_data_tab(site_data, time_slider, selection_data_types)
    tab_lat_lon = _create_selection_tab_lat_lon()
    tab_great_circle_distance = _create_selection_tab_great_circle_distance()

    size_map = 5
    size_data = 7
    layout = html.Div(
        [
            dcc.Store(id="site-names-store", storage_type="session"),
            dcc.Store(id="local-file-store", storage_type="session"),
            dbc.Row(
                [
                    dbc.Col(
                        left_side,
                        width={"size": size_map},
                        style={"padding-left": "0px"},
                    ),
                    dbc.Col(
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    data_tab,
                                    label=language["data-tab"]["label"],
                                    tab_style={"marginLeft": "auto"},
                                    label_style={"color": "gray"},
                                    active_label_style={
                                        "font-weight": "bold",
                                        "color": "#2C3E50",
                                    },
                                ),
                                dbc.Tab(
                                    tab_lat_lon,
                                    label=language["tab-lat-lon"]["label"],
                                    label_style={"color": "gray"},
                                    active_label_style={
                                        "font-weight": "bold",
                                        "color": "#2C3E50",
                                    },
                                    style={"text-align": "center"},
                                ),
                                dbc.Tab(
                                    tab_great_circle_distance,
                                    label=language[
                                        "tab-great-circle-distance"
                                    ]["label"],
                                    label_style={"color": "gray"},
                                    active_label_style={
                                        "font-weight": "bold",
                                        "color": "#2C3E50",
                                    },
                                    style={"text-align": "center"},
                                ),
                            ],
                        ),
                        width={"size": size_data},
                        style={"padding-right": "0px"},
                    ),
                ]
            ),
        ],
        style={
            "margin-top": "30px",
            "margin-left": "50px",
            "margin-right": "50px",
        },
    )
    return layout


def _create_left_side(
    site_map: go.Figure,
    projection_radio: dbc.RadioItems,
    checkbox_site: dbc.Checkbox,
) -> list[dbc.Row]:
    download_window = _create_download_window()
    open_window = _create_open_window()
    left_side = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        download_window,
                        html.Div(
                            open_window,
                            style={"margin-left": "15px"},
                        ),
                        html.Div(
                            dbc.Button(
                                language["buttons"]["settings"],
                                id="settings",
                            ),
                            style={"margin-left": "15px"},
                        ),
                    ],
                    style={"display": "flex", "justify-content": "flex-start"},
                ),
            ],
        ),
        dbc.Row(
            html.Div(
                checkbox_site,
                style={
                    "display": "flex",
                    "justify-content": "flex-end",
                    "fontSize": "16px",
                    "margin-top": "-3px",
                    "margin-left": "-95px",
                },
            ),
        ),
        dbc.Row(
            dcc.Graph(id="graph-site-map", figure=site_map),
        ),
        dbc.Row(
            html.Div(projection_radio),
            style={
                "margin-top": "25px",
                "text-align": "center",
                "fontSize": "18px",
            },
        ),
    ]
    return left_side


def _create_download_window() -> html.Div:
    download_window = html.Div(
        [
            dbc.Button(language["buttons"]["download"], id="download"),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(language["buttons"]["download"])
                    ),
                    dbc.ModalBody(
                        [
                            dbc.Label(
                                language["download_window"]["label"],
                                style={"font-size": "18px"},
                            ),
                            dcc.DatePickerSingle(
                                id="date-selection",
                                min_date_allowed=date(1998, 1, 1),
                                max_date_allowed=datetime.now()
                                - timedelta(days=1),
                                display_format="YYYY-MM-DD",
                                placeholder="YYYY-MM-DD",
                                date=datetime.now().strftime("%Y-%m-%d"),
                                style={"margin-left": "15px"},
                            ),
                            html.Div(
                                language["download_window"]["file-size"],
                                id="file-size",
                                style={"font-size": "18px", "margin-top": "20px"},
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        language["buttons"]["check-file-size"],
                                        id="check-file-size",
                                        style={"margin-right": "10px"}
                                    ),
                                    dbc.Button(
                                        language["buttons"]["download"],
                                        id="download-file",
                                        style={"margin-left": "10px"}
                                    ),
                                ],
                                style={
                                    "text-align": "center",
                                    "margin-top": "20px",
                                },
                            ),
                            html.Div(
                                "",
                                id="downloaded",
                                style={
                                    "visibility": "hidden",
                                },
                            ),
                        ]
                    ),
                ],
                id="download-window",
                is_open=False,
            ),
        ]
    )
    return download_window


def _create_open_window() -> html.Div:
    open_window = html.Div(
        [
            dbc.Button(language["buttons"]["open"], id="open"),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(language["buttons"]["open"])
                    ),
                    dbc.ModalBody(
                        [
                            html.Div(
                                [
                                    dbc.Label(
                                        language["open_window"]["label"],
                                        style={
                                            "font-size": "18px",
                                            "margin-top": "5px",
                                        },
                                    ),
                                    dbc.Select(
                                        id="select-file",
                                        options=[],
                                        style={
                                            "width": "50%",
                                            "margin-left": "15px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "flex-start",
                                },
                            ),
                            html.Div(
                                dbc.Button(
                                    language["buttons"]["open"],
                                    id="open-file",
                                ),
                                style={
                                    "text-align": "center",
                                    "margin-top": "20px",
                                },
                            ),
                        ]
                    ),
                ],
                id="open-window",
                is_open=False,
            ),
        ]
    )
    return open_window


def create_site_map() -> go.Figure:
    site_map = go.Scattergeo(
        mode="markers+text",
        marker=dict(size=8, line=dict(color="gray", width=1)),
        hoverlabel=dict(bgcolor="white"),
        textposition="top center",
        hoverinfo="lat+lon",
    )

    figure = go.Figure(site_map)
    figure.update_layout(
        title=language["graph-site-map"]["title"],
        title_font=dict(size=24, color="black"),
        margin=dict(l=0, t=60, r=0, b=0),
        geo=dict(projection_type=ProjectionType.MERCATOR.value),
    )
    figure.update_geos(
        landcolor="white",
        # landcolor="LightGreen",
        # showocean=True,
        # oceancolor="LightBlue",
        # showcountries=True,
        # countrycolor="Black",
    )

    return figure


def create_projection_radio() -> dbc.RadioItems:
    options = [
        {
            "label": language["projection-radio"][projection.value],
            "value": projection.value,
        }
        for projection in ProjectionType
    ]
    radio_items = dbc.RadioItems(
        options=options,
        id="projection-radio",
        inline=True,
        value=ProjectionType.MERCATOR.value,
    )
    return radio_items


def create_checkbox_site() -> dbc.Checkbox:
    checkbox = dbc.Checkbox(
        id="hide-show-site", label=language["hide-show-site"], value=True
    )
    return checkbox


def _create_data_tab(
    site_data: go.Figure,
    time_slider: dcc.RangeSlider,
    selection_data_types: dbc.Select,
) -> list[dbc.Row]:
    data_tab = [
        dbc.Row(
            dcc.Graph(id="graph-site-data", figure=site_data),
            style={"margin-top": "28px"},
        ),
        dbc.Row(
            html.Div(time_slider, id="div-time-slider"),
            style={"margin-top": "25px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        selection_data_types,
                        dbc.Button(
                            language["buttons"]["clear-all"],
                            id="clear-all",
                        ),
                    ],
                    style={"display": "flex", "justify-content": "flex-end"},
                ),
            ],
            style={
                "margin-top": "20px",
            },
        ),
    ]
    return data_tab


def create_selection_data_types() -> dbc.Select:
    options = [
        {
            "label": "2-10 minute TEC variations",
            "value": DataProducts.dtec_2_10.name,
        },
        {
            "label": "10-20 minute TEC variations",
            "value": DataProducts.dtec_10_20.name,
        },
        {
            "label": "20-60 minute TEC variations",
            "value": DataProducts.dtec_20_60.name,
        },
        {"label": "ROTI", "value": DataProducts.roti.name},
        {"label": "Adjusted TEC", "value": DataProducts.tec.name},
        {"label": "Elevation angle", "value": DataProducts.elevation.name},
        {"label": "Azimuth angle", "value": DataProducts.azimuth.name},
    ]
    select = dbc.Select(
        id="selection-data-types",
        options=options,
        value=DataProducts.dtec_2_10.name,
        style={"width": "250px", "margin-right": "20px"},
    )
    return select


def create_site_data() -> go.Figure:
    site_data = go.Figure()

    site_data.update_layout(
        title=language["data-tab"]["graph-site-data"]["title"],
        title_font=dict(size=24, color="black"),
        margin=dict(l=0, t=60, r=0, b=0),
        xaxis=dict(title=language["data-tab"]["graph-site-data"]["xaxis"]),
    )
    return site_data


def create_time_slider() -> dcc.RangeSlider:
    marks = {i: f"{i:02d}:00" if i % 3 == 0 else "" for i in range(25)}
    time_slider = dcc.RangeSlider(
        id="time-slider",
        min=0,
        max=24,
        step=1,
        marks=marks,
        value=[0, 24],
        allowCross=False,
        tooltip={
            "placement": "top",
            "style": {"fontSize": "18px"},
            "template": "{value}:00",
        },
        disabled=True,
    )
    return time_slider


def _create_selection_tab_lat_lon() -> list[dbc.Row]:
    tab_lat_lon = [
        dbc.Row(
            [
                dbc.Label(language["tab-lat-lon"]["min-lat"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="min-lat",
                        min=-90,
                        max=90,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
                dbc.Label(language["tab-lat-lon"]["max-lat"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="max-lat",
                        min=-90,
                        max=90,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
            ],
            style={"margin-top": "30px", "margin-left": "25px"},
        ),
        dbc.Row(
            [
                dbc.Label(language["tab-lat-lon"]["min-lon"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="min-lon",
                        min=-180,
                        max=180,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
                dbc.Label(language["tab-lat-lon"]["max-lon"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="max-lon",
                        min=-180,
                        max=180,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
            ],
            style={"margin-top": "15px", "margin-left": "25px"},
        ),
        dbc.Button(
            language["buttons"]["apply-selection-by-region"],
            id="apply-lat-lon",
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    language["buttons"]["clear-selection-by-region"],
                    id="clear-selection-by-region1",
                    style={"margin-top": "20px"},
                ),
                width={"size": 3, "offset": 9},
            ),
        ),
    ]
    return tab_lat_lon


def _create_selection_tab_great_circle_distance() -> list[dbc.Row]:
    tab_great_circle_distance = [
        dbc.Row(
            [
                dbc.Label(
                    language["tab-great-circle-distance"]["distance"], width=3
                ),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="distance",
                        min=0,
                        invalid=False,
                        style={"width": "97%"},
                    ),
                    width=4,
                    style={"margin-left": "-46px"},
                ),
            ],
            style={"margin-top": "30px", "margin-left": "20px"},
        ),
        dbc.Row(
            [
                dbc.Label(
                    language["tab-great-circle-distance"]["center-point-lat"],
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="center-point-lat",
                        min=-90,
                        max=90,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "5px"},
                ),
                dbc.Label(
                    language["tab-great-circle-distance"]["center-point-lon"],
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="center-point-lon",
                        min=-180,
                        max=180,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-25px"},
                ),
            ],
            style={"margin-top": "15px", "margin-left": "40px"},
        ),
        dbc.Button(
            language["buttons"]["apply-selection-by-region"],
            id="apply-great-circle-distance",
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    language["buttons"]["clear-selection-by-region"],
                    id="clear-selection-by-region2",
                    style={"margin-top": "20px"},
                ),
                width={"size": 3, "offset": 9},
            ),
        ),
    ]
    return tab_great_circle_distance
