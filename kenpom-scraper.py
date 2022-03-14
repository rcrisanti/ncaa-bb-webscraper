from typing import Callable, Dict, List, Optional, Sequence
import requests
import json
import tqdm
from bs4 import BeautifulSoup
from bs4.element import Tag


def build_col_names(headers: Sequence[Tag]) -> List[str]:
    cols = []
    for levels in zip(*[header.find_all("th") for header in headers]):
        texts = ["_".join(l.get_text().split()) for l in levels]
        cols.append("_".join(filter(lambda t: t != "", texts)))
    return cols


def get_row_data(
    col_names: Sequence[str],
    row_data: Tag,
    parsers: Optional[Dict[str, Callable]] = None,
) -> Dict[str, str]:
    if parsers is None:
        parsers = dict()

    row = dict()
    for col, cell in zip(col_names, row_data.find_all("td")):
        row[col] = parsers.get(col, lambda x: x)(cell.get_text())
    return row


def is_tourney_team(r) -> bool:
    tds = r.find_all("td")
    if len(tds) < 2:
        return False

    spans = tds[1].find_all("span")
    if len(spans) == 0:
        return False

    return "seed" in spans[0]["class"]


def get_tourney_team_data(
    content: bytes, parsers: Optional[Dict[str, Callable]] = None
) -> List[Dict[str, str]]:
    soup = BeautifulSoup(content, "html.parser")

    table_rows = soup.find_all("tr")
    cols = build_col_names([table_rows.pop(0), table_rows.pop(0)])

    data = []
    for team in filter(is_tourney_team, table_rows):
        data.append(get_row_data(cols, team, parsers))
    return data


def main():
    def split_team_seed(t: str) -> List[str]:
        s = t.split()
        seed = s.pop()
        return [" ".join(s), int(seed)]

    parsers = {
        "Rk": int,
        "Team": split_team_seed,
        "W-L": lambda x: list(map(int, x.split("-"))),
        "AdjEM": float,
        "AdjO": float,
        "Strength_of_Schedule_AdjD": int,
        "NCSOS_AdjT": float,
    }

    data = {}
    for year in tqdm.trange(2002, 2023):
        if year == 2020:
            continue
        year_content = requests.get(
            "https://kenpom.com/index.php", params=dict(y=year)
        ).content
        year_data = get_tourney_team_data(year_content, parsers=parsers)
        data[year] = year_data

    with open("data/kenpom-data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
