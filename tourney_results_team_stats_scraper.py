from typing import Any, Callable, Dict, List, Optional, Sequence
from urllib.parse import urljoin
import requests
import re
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


def get_team_stats(table: Tag) -> Dict[str, Any]:
    row = table.find("tbody").find("tr")
    if row.find("th").string != "Team":
        return dict()
    stats = {
        t["data-stat"]: float("nan")
        if t.string is None
        else int(t.string)
        if t["data-stat"] == "g"
        else float(t.string)
        for t in row.find_all("td")
    }
    return stats


def get_teams_stats(root_url: str, append_urls: Sequence[str]) -> List[Dict[str, Any]]:
    urls = map(lambda url: urljoin(root_url, url), append_urls)
    stats = []
    for url in tqdm.tqdm(list(urls)):
        team_stats = {}
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        per_game_tables = soup.find_all("table", id="schools_per_game")
        if len(per_game_tables) == 0:
            continue
        header = soup.find_all("h1", itemprop="name")[0].find_all("span")
        team_stats["year"] = header[0].string
        team_stats["team"] = header[1].string
        team_stats["stats"] = get_team_stats(per_game_tables[0])
        stats.append(team_stats)
    return stats


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

    def is_early_appearance(r: Tag) -> bool:
        rnd = r.find("td", **{"data-stat": "round"})
        if rnd is None:
            return False
        return rnd.string in {"First Round", "First Four"}

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
    game_res_data = []
    url_search = re.compile("^/cbb/schools/")
    team_stats_data = []
    pbar = tqdm.tqdm()
    try:
        while True:
            params["offset"] = offset
            r = requests.get(url, params=params)
            soup = BeautifulSoup(r.content, "html.parser")
            tables = soup.find_all("table")
            if len(tables) == 0:
                break

            # Get tournament game results
            page_data = get_table_data(tables[0], parsers=parsers)
            game_res_data.extend(page_data)

            # Get team data
            nested_urls = [
                [t["href"] for t in r.find_all(href=url_search)]
                for r in filter(is_early_appearance, tables[0].find_all("tr"))
            ]
            team_stats = get_teams_stats(
                "https://www.sports-reference.com",
                [url for game in nested_urls for url in game],
            )
            team_stats_data.extend(team_stats)

            offset += offset_by
            pbar.update()
    except Exception as e:
        print(f"error ocurred at offset {offset} - saving intermediate data:\n{e}")

    pbar.close()

    with open("data/tourney-results.json", "w") as f:
        json.dump(game_res_data, f)

    with open("data/team-stats.json", "w") as f:
        json.dump(team_stats_data, f)


if __name__ == "__main__":
    main()
