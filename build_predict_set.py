from typing import Set, Tuple
import pandas as pd
from merge_data import (
    TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP,
    TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP,
)

EXTRA_TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP = {
    "Boise State": "Boise St.",
    "South Dakota State": "South Dakota St.",
    "New Mexico State": "New Mexico St.",
    "Jacksonville State": "Jacksonville St.",
    "Cal State Fullerton": "Cal St. Fullerton",
    "Wright State": "Wright St.",
    "Texas A&M-Corpus Christi": "Texas A&M Corpus Chris",
}

EXTRA_TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP = {
    "Kansas": "Kansas Jayhawks",
    "San Francisco": "San Francisco Dons",
    "Boise St.": "Boise State",
    "South Dakota St.": "South Dakota State",
    "New Mexico St.": "New Mexico State",
    "Saint Peter's": "St. Peter's Peacocks",
    "Montana St.": "Montana State Bobcats",
    "Longwood": "Longwood Lancers",
    "Delaware": "Delaware Fightin' Blue Hens",
    "Jacksonville St.": "Jacksonville State",
    "Cal St. Fullerton": "Cal State Fullerton'",
    "Wright St.": "Wright State",
    "Bryant": "Bryant Bulldogs",
    "Texas A&M Corpus Chris": "Texas A&M-Corpus Christi",
}


bracket_2022_matchups = {
    ("Colorado State", "Michigan"),
    ("Providence", "South Dakota State"),
    ("Boise State", "Memphis"),
    ("Baylor", "Norfolk State"),
    ("Tennessee", "Longwood"),
    ("Iowa", "Richmond"),
    ("Gonzaga", "Georgia State"),
    ("UNC", "Marquette"),
    ("UConn", "New Mexico State"),
    ("Kentucky", "Saint Peter's"),
    # ("Saint Mary's", "") # Result of play-in
    ("San Diego State", "Creighton"),
    ("Arkansas", "Vermont"),
    ("Murray State", "San Francisco"),
    ("UCLA", "Akron"),
    # ("Kansas", "")  # Result of play-in
    ("Ohio State", "Loyola (IL)"),
    ("Auburn", "Jacksonville State"),
    ("Texas Tech", "Montana St."),
    ("Purdue", "Yale"),
    ("Villanova", "Delaware"),
    ("USC", "Miami (FL)"),
    # ("Alabama", "")
    ("Texas", "Virginia Tech"),
    ("Illinois", "Chattanooga"),
    ("Duke", "Cal State Fullerton"),
    ("LSU", "Iowa State"),
    # ("Arizona", "")
    ("Houston", "UAB"),
    ("Michigan State", "Davidson"),
    ("Wisconsin", "Colgate"),
    ("Seton Hall", "TCU"),
}


def rename_col(name: str, prefix: str) -> str:
    if name[0].isupper():
        return f"{prefix}{name}"
    else:
        return f"{prefix}_{name}"


def create_matchups(
    matchups: Set[Tuple[str, str]], stats: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for team_a, team_b in matchups:
        game = pd.concat(
            (
                stats.loc[team_a].rename(lambda c: rename_col(c, "A")),
                stats.loc[team_b].rename(lambda c: rename_col(c, "B")),
            )
        )
        game["ATeam"] = team_a
        game["BTeam"] = team_b
        rows.append(game)
    return pd.concat(rows, axis=1).T


def main():
    # kenpom = pd.read_csv("data/kenpom-data.csv")
    # team_stats = pd.read_csv("data/team-stats-with-current-year.csv")

    # kenpom = kenpom.loc[kenpom.Year == 2022].drop(columns=["Year"])
    # team_stats = team_stats.loc[team_stats.Year == 2022].drop(columns=["Year"])

    # TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP.update(
    #     EXTRA_TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP
    # )
    # kenpom["Team"] = kenpom.Team.replace(
    #     {v: k for k, v in TOURNEY_RES_TO_KENPOM_TEAM_NAME_MAP.items()}
    # )
    # TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP.update(
    #     EXTRA_TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP
    # )
    # team_stats["Team"] = team_stats.Team.replace(
    #     {v: k for k, v in TOURNEY_RES_TO_TEAM_STATS_TEAM_NAME_MAP.items()}
    # )

    # merged = pd.merge(kenpom, team_stats, how="inner", on="Team")

    # assert merged.shape[0] == kenpom.shape[0] == team_stats.shape[0], "imperfect merge"

    # merged.to_csv("data/kenpom-team-stats-2022.csv", index=False)

    stats_2022 = pd.read_csv("data/kenpom-team-stats-2022.csv", index_col="Team")
    round_matchups = create_matchups(bracket_2022_matchups, stats_2022)

    # Get cols in same order
    train_data = pd.read_csv("data/model-ready.csv")
    train_data.drop(columns=["A_team_wins", "Year", "OT"], inplace=True)
    round_matchups[train_data.columns].to_csv(
        "data/2022-first-round-matchups.csv", index=False
    )


if __name__ == "__main__":
    main()
