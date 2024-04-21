from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
# from ..view import PointColor, ProjectionType, languages
from ..view import *
from ..processing import *
from .figure import create_map_with_sites, create_site_data_with_values
from datetime import datetime, timezone
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from pathlib import Path
from numpy.typing import NDArray
import numpy as np


language = languages["en"]
FILE_FOLDER = Path("data")


def register_callbacks(
    app: dash.Dash
) -> None:
    @app.callback(
        Output("graph-site-map", "figure", allow_duplicate=True),
        [Input("projection-radio", "value")],
        [
            State("hide-show-site", "value"),
            State("region-site-names-store", "data"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_map_projection(
        projection_value: ProjectionType, 
        check_value: bool,
        region_site_names: list[str],
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str]
    ) -> go.Figure:
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, site_data_store)
        return site_map

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("graph-site-map", "clickData"),
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("time-slider", "disabled", allow_duplicate=True),
            Output("site-data-store", "data", allow_duplicate=True)
        ],
        [Input("graph-site-map", "clickData")],
        [
            State("local-file-store", "data"),
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("region-site-names-store", "data"),
            State("site-coords-store", "data"),
            State("selection-data-types", "value"),
            State("site-data-store", "data"),
            State("time-slider", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_site_data(
        clickData: dict[str, list[dict[str, float | str | dict]]],
        local_file: str,
        projection_value: ProjectionType, 
        check_value: bool,
        region_site_names: list[str],
        site_coords: dict[Site, dict[Coordinate, float]],
        data_types: str,
        site_data_store: list[str],
        time_value: list[int],
    ) -> list[go.Figure | None | bool | dcc.RangeSlider]:
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, site_data_store)
        
        if clickData is not None:
            site_name = clickData["points"][0]["text"]
            if site_data_store is None:
                site_data_store = []
            
            site_idx = clickData["points"][0]["pointIndex"]
            site_color = site_map.data[0].marker.color[site_idx]
            if (
                site_color == PointColor.SILVER.value
                or site_color == PointColor.GREEN.value
            ):
                site_data_store.append(site_name)
            elif site_color == PointColor.RED.value:
                site_data_store.remove(site_name)
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, site_data_store)
        site_data = create_site_data_with_values(site_data_store, data_types, local_file, time_value)

        disabled = True if len(site_data.data) == 0 else False

        site_data_store = site_data.layout.yaxis.ticktext
        return site_map, None, site_data, disabled, site_data_store


    @app.callback(
        [
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("time-slider", "disabled", allow_duplicate=True),
        ],
        [Input("time-slider", "value")],
        [
            State("selection-data-types", "value"),
            State("site-data-store", "data"),
            State("local-file-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def change_xaxis(
        time_value: list[int],
        data_types: str,
        site_data_store: list[str],
        local_file: str,
    ) -> list[go.Figure | dcc.RangeSlider]:
        site_data = create_site_data_with_values(site_data_store, data_types, local_file, time_value)
        disabled = True if len(site_data.data) == 0 else False
        return site_data, disabled

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("time-slider", "disabled", allow_duplicate=True),
            Output("site-data-store", "data", allow_duplicate=True),
        ],
        [Input("clear-all", "n_clicks")],
        [
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("region-site-names-store", "data"),
            State("site-coords-store", "data"),
         ],
        prevent_initial_call=True,
    )
    def clear_all(
        n: int,
        projection_value: ProjectionType, 
        check_value: bool,
        region_site_names: list[str],
        site_coords: dict[Site, dict[Coordinate, float]],
    ) -> list[go.Figure | dcc.RangeSlider]:
        site_data = create_site_data_with_values(None, None, None, None)
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, None)
        disabled = True 
        return site_map, site_data, disabled, None


    @app.callback(
        Output("graph-site-map", "figure", allow_duplicate=True),
        [Input("hide-show-site", "value")],
        [
            State("projection-radio", "value"),
            State("region-site-names-store", "data"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def hide_show_site(
        check_value: bool, 
        projection_value: ProjectionType,
        region_site_names: list[str],
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str]
    ) -> go.Figure:
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, site_data_store)
        return site_map

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("min-lat", "invalid"),
            Output("max-lat", "invalid"),
            Output("min-lon", "invalid"),
            Output("max-lon", "invalid"),
            Output("region-site-names-store", "data", allow_duplicate=True),
        ],
        [Input("apply-lat-lon", "n_clicks")],
        [
            State("min-lat", "value"),
            State("max-lat", "value"),
            State("min-lon", "value"),
            State("max-lon", "value"),
            State("region-site-names-store", "data"),
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def apply_selection_by_region(
        n: int,
        min_lat: int,
        max_lat: int,
        min_lon: int,
        max_lon: int,
        region_site_names: list[str],
        projection_value: ProjectionType,
        check_value: bool,
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str]
    ) -> list[go.Figure | bool | list[str]]:
        return_value_list = [None, False, False, False, False, region_site_names]
        sites = region_site_names

        check_region_value(min_lat, 1, return_value_list)
        check_region_value(max_lat, 2, return_value_list)
        check_region_value(min_lon, 3, return_value_list)
        check_region_value(max_lon, 4, return_value_list)

        if True in return_value_list or site_coords is None:
            return_value_list[0] = create_map_with_sites(site_coords, projection_value, check_value, sites, site_data_store)
            return return_value_list
        else:
            sites_by_region = select_sites_by_region(
                site_coords, min_lat, max_lat, min_lon, max_lon
            )
            sites, _, _ = get_namelatlon_arrays(sites_by_region)
            return_value_list[-1] = sites
        return_value_list[0] = create_map_with_sites(site_coords, projection_value, check_value, sites, site_data_store)
        return return_value_list

    def check_region_value(
        value: int,
        idx: int,
        return_value_list: dict[str, go.Figure | bool],
    ) -> None:
        if value is None:
            return_value_list[idx] = True

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("distance", "invalid"),
            Output("center-point-lat", "invalid"),
            Output("center-point-lon", "invalid"),
            Output("region-site-names-store", "data", allow_duplicate=True),
        ],
        [Input("apply-great-circle-distance", "n_clicks")],
        [
            State("distance", "value"),
            State("center-point-lat", "value"),
            State("center-point-lon", "value"),
            State("region-site-names-store", "data"),
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def apply_great_circle_distance(
        n: int,
        distance: int,
        lat: int,
        lon: int,
        region_site_names: list[str],
        projection_value: ProjectionType,
        check_value: bool,
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str]
    ) -> list[go.Figure | bool | list[str]]:
        return_value_list = [None, False, False, False, region_site_names]
        sites = region_site_names

        check_region_value(distance, 1, return_value_list)
        check_region_value(lat, 2, return_value_list)
        check_region_value(lon, 3, return_value_list)

        if True in return_value_list or site_coords is None:
            return_value_list[0] = create_map_with_sites(site_coords, projection_value, check_value, sites, site_data_store)
            return return_value_list
        else:
            central_point = dict()
            central_point[Coordinate.lat.value] = lat
            central_point[Coordinate.lon.value] = lon
            sites_by_region = select_sites_in_circle(
                site_coords, central_point, distance
            )
            sites, _, _ = get_namelatlon_arrays(sites_by_region)
            return_value_list[-1] = sites
        return_value_list[0] = create_map_with_sites(site_coords, projection_value, check_value, sites, site_data_store)
        return return_value_list

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("region-site-names-store", "data", allow_duplicate=True),
        ],
        [
            Input("clear-selection-by-region1", "n_clicks"),
            Input("clear-selection-by-region2", "n_clicks"),
        ],
        [
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def clear_selection_by_region(
        n1: int, 
        n2: int,
        projection_value: ProjectionType,
        check_value: bool,
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str]
    ) -> list[go.Figure | None]:
        site_map = create_map_with_sites(site_coords, projection_value, check_value, None, site_data_store)
        return site_map, None

    @app.callback(
        [
            Output("download-window", "is_open"),
            Output("downloaded", "style", allow_duplicate=True),
            Output("downloaded", "children", allow_duplicate=True),
        ],
        [Input("download", "n_clicks")],
        [State("download-window", "is_open")],
        prevent_initial_call=True,
    )
    def open_close_download_window(
        n1: int, is_open: bool
    ) -> list[bool | dict[str, str] | str]:
        style = {"visibility": "hidden"}
        return not is_open, style, ""

    @app.callback(
        [
            Output("downloaded", "style", allow_duplicate=True),
            Output("downloaded", "children", allow_duplicate=True),
        ],
        [Input("download-file", "n_clicks")],
        [State("date-selection", "date")],
        prevent_initial_call=True,
    )
    def download_file(n1: int, date: str) -> list[dict[str, str] | str]:
        text = language["download_window"]["successаfuly"]
        color = "green"
        if date is None:
            text = language["download_window"]["unsuccessаfuly"]
        else:
            if not FILE_FOLDER.exists():
                FILE_FOLDER.mkdir()
            local_file = FILE_FOLDER / (date + ".h5")
            if local_file.exists():
                text = language["download_window"]["repeat-action"]
            else:
                local_file.touch()
                if not load_data(date, local_file):
                    text = language["download_window"]["error"]
                    local_file.unlink()
        if text != language["download_window"]["successаfuly"]:
            color = "red"
        style = {
            "text-align": "center",
            "margin-top": "20px",
            "color": color,
        }
        return style, text
    
    @app.callback(
        Output("file-size", "children"),
        [Input("check-file-size", "n_clicks")],
        [State("date-selection", "date")],
        prevent_initial_call=True,
    )
    def change_data_types(n: int, date: str) -> str:
        text = language["download_window"]["file-size"]
        if date is None:
           text += "none"
        else:
            Mb = сheck_file_size(date)
            if Mb is None:
                text += "none"
            elif Mb == 0:
                text += language["download_window"]["unknown"]
            else:
                text += str(Mb)
        return text

    @app.callback(
        [
            Output("open-window", "is_open", allow_duplicate=True),
            Output("select-file", "options"),
        ],
        [Input("open", "n_clicks")],
        [State("open-window", "is_open")],
        prevent_initial_call=True,
    )
    def open_close_open_window(
        n1: int, is_open: bool
    ) -> list[bool | list[dict[str, str]]]:
        options = []
        if FILE_FOLDER.exists():
            for file_path in FILE_FOLDER.iterdir():
                if file_path.is_file():
                    options.append(
                        {"label": file_path.name, "value": file_path.name}
                    )
        return not is_open, options

    @app.callback(
        [
            Output("open-window", "is_open"),
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("local-file-store", "data"),
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("time-slider", "disabled", allow_duplicate=True),
            Output("site-coords-store", "data"),
            Output("region-site-names-store", "data"),
            Output("site-data-store", "data"),
        ],
        [Input("open-file", "n_clicks")],
        [
            State("select-file", "value"),
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
        ],
        prevent_initial_call=True,
    )
    def open_close_open_window(
        n1: int, 
        filename: str, 
        projection_value: ProjectionType, 
        check_value: bool,
    ) -> list[bool | go.Figure | str | dcc.RangeSlider | None]:
        local_file = FILE_FOLDER / filename
        site_coords = get_sites_coords(local_file)
        
        site_map = create_map_with_sites(site_coords, projection_value, check_value, None, None)

        site_data = create_site_data()

        return (
            False,
            site_map,
            str(local_file),
            site_data,
            True,
            site_coords,
            None,
            None
        )

    @app.callback(
        Output("graph-site-data", "figure", allow_duplicate=True),
        [Input("selection-data-types", "value")],
        [
            State("local-file-store", "data"),
            State("site-data-store", "data"),
            State("time-slider", "value"),
        ],
        prevent_initial_call=True,
    )
    def change_data_types(
        data_types: str, 
        local_file: str,
        site_data_store: list[str],
        time_value: list[int],
    ) -> go.Figure:
        site_data = create_site_data_with_values(site_data_store, data_types, local_file, time_value)
        return site_data

    @app.callback(
        [
            Output("graph-site-map", "figure"),
            Output("graph-site-data", "figure"),
            Output("time-slider", "disabled"),
        ],
        [Input("url", "pathname")],
        [
            State("projection-radio", "value"),
            State("hide-show-site", "value"),
            State("region-site-names-store", "data"),
            State("site-coords-store", "data"),
            State("site-data-store", "data"),
            State("local-file-store", "data"),
            State("time-slider", "value"),
            State("selection-data-types", "value"),
         ]
    )
    def update_all(
        pathname: str,
        projection_value: ProjectionType, 
        check_value: bool,
        region_site_names: list[str],
        site_coords: dict[Site, dict[Coordinate, float]],
        site_data_store: list[str],
        local_file: str,
        time_value: list[int],
        data_types: str, 
    ) -> go.Figure:
        site_map = create_map_with_sites(site_coords, projection_value, check_value, region_site_names, site_data_store)
        site_data = create_site_data_with_values(site_data_store, data_types, local_file, time_value)
        disabled = True if len(site_data.data) == 0 else False
        return site_map, site_data, disabled
    
    
