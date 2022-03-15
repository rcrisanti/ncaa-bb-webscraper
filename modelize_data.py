import numpy as np
import pandas as pd


def main():
    data = pd.read_csv("data/merged.csv")
    data.drop(
        columns=[
            "Region",
            "Round",
            "PTS",
            "Diff",
            "Location",
            "Team_x",
            "WinningConf",
            "LosingConf",
            "Team_y",
            "Team_x.1",
            "Team_y.1",
            "WinningSeed_y",
            "LosingSeed_y",
            "Date",
        ],
        inplace=True,
    )
    data.rename(
        columns={"WinningSeed_x": "WinningSeed", "LosingSeed_x": "LosingSeed"},
        inplace=True,
    )

    rng = np.random.default_rng()
    a_teams = np.where(rng.integers(0, 2, data.shape[0]), "Winning", "Losing")

    reformatted = []
    for a_team, (_, row) in zip(a_teams, data.iterrows()):
        row_data = {}
        for col in row.index:
            if col in {"Year", "Ot"}:
                row_data[col] = row[col]
            elif col.startswith(a_team):
                row_data[col.replace(a_team, "A")] = row[col]
            else:
                b_team = "Winning" if a_team == "Losing" else "Losing"
                row_data[col.replace(b_team, "B")] = row[col]
        row_data["A_team_wins"] = a_team == "Winning"
        reformatted.append(row_data)

    pd.DataFrame(reformatted).to_csv("data/model-ready.csv", index=False)


if __name__ == "__main__":
    main()
