import json
import pandas as pd
from merge_data import (
    TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP,
    TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP,
)
from tourney_results_team_stats_scraper import get_teams_stats

CUSTOM_NAME_CHANGE = {
    "saint-marys": "saint-marys-ca",
    "uconn": "connecticut",
    "lsu": "louisiana-state",
    "unc": "north-carolina",
    "tcu": "texas-christian",
    "usc": "southern-california",
    "uab": "alabama-birmingham",
    "texas-am-corpus-chris": "texas-am-corpus-christi",
}


def format_team_name(name: str) -> str:
    remove = ["'", "(", ")", "&"]
    name = name.lower().replace("st.", "state")
    for char in remove:
        name = name.replace(char, "")
    name = name.replace(" ", "-")

    custom = CUSTOM_NAME_CHANGE.get(name)
    if custom is None:
        return name
    else:
        return custom


def main():
    YEAR = 2022
    kenpom = pd.read_csv("data/kenpom-data.csv")
    kenpom = kenpom[kenpom.Year == YEAR]
    team_names = kenpom.Team.replace(
        {v: k for k, v in TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP.items()}
    ).replace({v: k for k, v in TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP.items()})
    names = map(format_team_name, team_names)
    urls = list(map(lambda n: f"{n}/{YEAR}.html", names))

    team_stats = get_teams_stats("https://www.sports-reference.com/cbb/schools/", urls)
    print(f"got stats for {len(team_stats)} of {len(urls)} teams")

    with open("data/team-stats.json", "r") as f:
        other_team_stats = json.load(f)

    other_team_stats.extend(team_stats)

    with open("data/team-stats-with-current-year.json", "w") as f:
        json.dump(other_team_stats, f)


if __name__ == "__main__":
    main()
