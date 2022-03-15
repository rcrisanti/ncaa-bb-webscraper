from typing import Any, Callable, Dict, List, Optional, Sequence
from webbrowser import get
import requests
import json
import tqdm
from bs4 import BeautifulSoup
from bs4.element import Tag
from kenpom_scraper import get_row_data, build_col_names


def get_table_data(
    table: Tag,
    parsers: Optional[Dict[str, Callable]] = None,
) -> List[Dict[str, Any]]:
    header = table.find_all("thead")[0]
    body = table.find_all("tbody")[0]

    col_names = build_col_names([header])[1:]

    rows = []
    for row in body.find_all("tr"):
        if "thead" in row.get("class", []):
            continue
        rows.append(get_row_data(col_names=col_names, row_data=row, parsers=parsers))
    return rows


def main():
    params = dict(year_min=2002, year_max=2021, game_result="W")
    url = (
        "https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&"
        "match=single&round=&region=&location=&school_id=&conf_id=&opp_id=&opp_conf=&"
        "seed=&seed_cmp=eq&opp_seed=&opp_seed_cmp=eq&pts_diff=&pts_diff_cmp=eq&"
        "order_by=date_game&order_by_single=date_game&order_by_combined=g&order_by_asc=#stats"
    )

    def split_team_seed(t: str) -> List[str]:
        s = t.split("\xa0")
        seed = s.pop(0)
        return [" ".join(s), int(seed)]

    parsers = {
        "Rk": int,
        "Year": int,
        "School": split_team_seed,
        "PTS": int,
        "Opponent": split_team_seed,
        "PTS": int,
        "OT": lambda ot: ot == "OT",
        "Diff": int,
    }

    offset_by = 100
    offset = 0
    all_data = []
    pbar = tqdm.tqdm()
    try:
        while True:
            params["offset"] = offset
            r = requests.get(url, params=params)
            soup = BeautifulSoup(r.content, "html.parser")
            tables = soup.find_all("table")
            if len(tables) == 0:
                break

            page_data = get_table_data(tables[0], parsers=parsers)
            all_data.extend(page_data)

            offset += offset_by
            pbar.update()
    except:
        print(f"error ocurred at offset {offset} - saving intermediate data")

    pbar.close()

    with open("data/tourney-results.json", "w") as f:
        json.dump(all_data, f)


if __name__ == "__main__":
    main()
