import pprint
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.pipeline import Pipeline
from sklearn import metrics


def main():
    data = pd.read_csv("data/model-ready.csv")

    data["A_winperc"] = data["AW"] / (data["AW"] + data["AL"])
    data["B_winperc"] = data["BW"] / (data["BW"] + data["BL"])
    data.drop(columns=["Year", "OT", "AW", "AL", "BW", "BL"], inplace=True)

    X, y = (
        data.loc[:, [c for c in data.columns if c != "A_team_wins"]],
        data.loc[:, "A_team_wins"],
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y.ravel(), test_size=0.2)

    ct = ColumnTransformer(
        [
            (
                "numericals",
                StandardScaler(),
                make_column_selector(dtype_include=np.number),
            ),
            ("bools", "passthrough", make_column_selector(dtype_include=bool)),
        ],
    )
    pipe = Pipeline(
        [
            ("preprocessing", ct),
            ("impute", SimpleImputer(strategy="mean")),
            ("log_reg", LogisticRegressionCV(max_iter=5000, n_jobs=-1)),
        ],
        verbose=True,
    )
    pipe.fit(X_train, y_train)
    print("coeffiecients:")
    pprint.pprint(
        dict(
            zip(pipe[:-2].get_feature_names_out(), pipe.named_steps["log_reg"].coef_[0])
        )
    )
    print(metrics.accuracy_score(y_test, pipe.predict(X_test)))


if __name__ == "__main__":
    main()
