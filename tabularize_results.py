import json
import numpy as np
import pandas as pd


def kenpom_to_tabular(file: str) -> pd.DataFrame:
    with open(file, "r") as f:
        d = json.load(f)

    frames = []
    for year, data in d.items():
        df = pd.DataFrame(data)
        df["Year"] = year
        df = df.join(
            pd.DataFrame(df["Team"].tolist(), columns=["Team", "Seed"]), lsuffix="_old"
        )
        df = df.join(pd.DataFrame(df["W-L"].tolist(), columns=["W", "L"]))
        df.drop(columns=["Team_old", "W-L"], inplace=True)
        df.set_index(["Year", "Team"], inplace=True)
        frames.append(df)
    return pd.concat(frames)


def tourney_res_to_tabular(file: str) -> pd.DataFrame:
    with open(file, "r") as f:
        d = json.load(f)

    df = pd.DataFrame(d)
    df = df.join(
        pd.DataFrame(df["School"].tolist(), columns=["WinningTeam", "WinningSeed"])
    )
    df = df.join(
        pd.DataFrame(df["Opponent"].tolist(), columns=["LosingTeam", "LosingSeed"])
    )
    df.drop(columns=["School", "Opponent"], inplace=True)
    return df


def team_stats_to_tabular(file: str) -> pd.DataFrame:
    with open(file, "r") as f:
        d = json.load(f)

    df = pd.json_normalize(d)
    df.rename(columns=lambda c: c.split(".")[-1], inplace=True)
    df.rename(columns={"team": "Team"}, inplace=True)
    df["Year"] = df["year"].apply(lambda y: int("20" + y.split("-")[-1]))
    df.drop(columns=["year"], inplace=True)
    return df


def main():
    kenpom = kenpom_to_tabular("data/kenpom-data.json")
    tourney_res = tourney_res_to_tabular("data/tourney-results.json")
    team_stats = team_stats_to_tabular("data/team-stats.json")
    
    kenpom.to_csv("data/kenpom-data.csv", index=True)
    tourney_res.to_csv("data/tourney-results.csv", index=False)
    team_stats.to_csv("data/team-stats.csv", index=False)


if __name__ == "__main__":
    main()
