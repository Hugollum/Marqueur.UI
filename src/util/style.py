import streamlit as st
from dataclasses import dataclass
from pathlib import Path
import base64


@dataclass()
class Color:
    hex: str
    rgb: tuple[int, int, int]

@dataclass()
class TeamColor:
    abbreviation: str
    primary: Color
    secondary: Color

team_colors = {
    'ANA': TeamColor('ANA', Color("#F47A38", (252, 76, 2)),		    Color("#B9975B", (185, 151, 91))),
    'BOS': TeamColor('BOS', Color("#FFB81C", (252, 181, 20)),		Color("#000000", (17, 17, 17))),
    'BUF': TeamColor('BUF', Color("#003087", (0, 48, 135)),		    Color("#FFB81C", (255, 184, 28))),
    'CGY': TeamColor('CGY', Color("#D2001C", (210, 0, 28)),		    Color("#FAAF19", (250, 175, 25))),
    'CAR': TeamColor('CAR', Color("#CE1126", (206, 17, 38)),		Color("#A4A9AD", (164, 169, 173))),
    'CHI': TeamColor('CHI', Color("#CF0A2C", (207, 10, 44)),		Color("#FF671B", (255, 103, 27))),
    'COL': TeamColor('COL', Color("#6F263D", (111, 38, 61)),		Color("#236192", (35, 97, 146))),
    'CBJ': TeamColor('CBJ', Color("#002654", (0, 38, 84)),			Color("#ce1126", (206,17,38))),
    'DAL': TeamColor('DAL', Color("#006847", (0, 104, 71)),		    Color("#8F8F8C", (143, 143, 140))),
    'DET': TeamColor('DET', Color("#ce1126", (206, 17, 38)),		Color("#FFFFFF", (255, 255, 255))),
    'EDM': TeamColor('EDM', Color("#041E42", (4, 30, 66)),			Color("#FF4C00", (252, 76, 0))),
    'FLA': TeamColor('FLA', Color("#041E42", (4, 30, 66)),			Color("#c8102E", (200, 16, 46))),
    'LAK': TeamColor('LAK', Color("#111111", (17, 17, 17)),			Color("#A2AAAD", (162, 170, 173))),
    'MIN': TeamColor('MIN', Color("#A6192E", (175, 35, 36)),		Color("#154734", (2, 73, 48))),
    'MTL': TeamColor('MTL', Color("#AF1E2D", (175, 30, 45)),		Color("#192168", (25, 33, 104))),
    'NSH': TeamColor('NSH', Color("#FFB81C", (255, 184, 28)),		Color("#041E42", (4, 30, 66))),
    'NJD': TeamColor('NJD', Color("#CE1126", (206, 17, 38)),		Color("#000000", (0, 0, 0))),
    'NYI': TeamColor('NYI', Color("#00539b", (0, 83, 155)),			Color("#f47d30", (244, 125, 48))),
    'NYR': TeamColor('NYR', Color("#0038A8", (0, 56, 168)),			Color("#CE1126", (206,17,38))),
    'OTT': TeamColor('OTT', Color("#000000", (0, 0, 0)),			Color("#DA1A32", (218, 26, 50))),
    'PHI': TeamColor('PHI', Color("#F74902", (247, 73, 2)),		    Color("#000000", (0, 0, 0))),
    'PIT': TeamColor('PIT', Color("#000000", (0, 0, 0)),			Color("#CFC493", (207, 196, 147))),
    'SLT': TeamColor('SLT', Color("#002F87", (0, 47, 135)),		    Color("#FCB514", (252, 181, 20))),
    'SJS': TeamColor('SJS', Color("#006D75", (0, 109, 117)),		Color("#EA7200", (234, 114, 0))),
    'SEA': TeamColor('SEA', Color("#001628", (0, 22, 40)),			Color("#99d9d9", (153, 217, 217))),
    'TBL': TeamColor('TBL', Color("#002868", (0, 40, 104)),		    Color("#FFFFFF", (255, 255, 255))),
    'TOR': TeamColor('TOR', Color("#00205b", (0, 32, 91)),			Color("#FFFFFF", (255, 255, 255))),
    'UTA': TeamColor('UTA', Color("#71AFE5", (0, 32, 91)),			Color("#090909", (9, 9, 9))),
    'VAN': TeamColor('VAN', Color("#00205B", (0, 32, 91)),			Color("#00843d", (10, 134, 61))),
    'VGK': TeamColor('VGK', Color("#B4975A", (185, 151, 91)),		Color("#333f42", (51, 63, 72))),
    'WSH': TeamColor('WSH', Color("#041E42", (4, 30, 66)),			Color("#C8102E", (200, 16, 46))),
    'WPG': TeamColor('WPG', Color("#041E42", (4, 30, 66)),			Color("#004C97", (0, 76, 151))) ,
}


@st.cache_data()
def _load_team_images():
    def open_image(path: str):
        with open(path, "rb") as p:
            file = p.read()
            return f"data:image/png;base64,{base64.b64encode(file).decode()}"

    dir_path = Path(r"assets/img/teams")
    files = [file for file in dir_path.iterdir() if file.is_file()]
    return {file.stem: open_image(f"{dir_path}/{file.name}") for file in files if file.suffix == ".png"}

team_images = _load_team_images()


def image_sizing_ratio(target_size, fig_width, fig_height, x_range, y_range):
    x_pixels_per_unit = fig_width / (x_range[1] - x_range[0])
    y_pixels_per_unit = fig_height / (y_range[1] - y_range[0])
    return target_size / x_pixels_per_unit, target_size / y_pixels_per_unit
