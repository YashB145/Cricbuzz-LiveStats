import sqlite3
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, r2_score


DB_PATH = "cricket.db"


# ============================================================
# 1. LOAD REAL INTERNATIONAL CRICKET DATA
# ============================================================

def load_match_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        match_id,
        match_date,
        format,
        gender,
        team1,
        team2,
        venue,
        winner,
        team1_runs,
        team2_runs
    FROM ml_international_matches
    WHERE winner IS NOT NULL
      AND winner != ''
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


# ============================================================
# 2. PREPARE DATA
# ============================================================

def prepare_data(df):
    df = df.copy()

    # Keep only matches where winner is one of the two teams
    df = df[
        df["winner"].isin(df["team1"])
        | df["winner"].isin(df["team2"])
    ].copy()

    # Winner target:
    # 1 = Team 1 wins
    # 0 = Team 2 wins
    df["target"] = (df["winner"] == df["team1"]).astype(int)

    # Remove rows without required categorical information
    df = df.dropna(
        subset=[
            "format",
            "gender",
            "team1",
            "team2",
            "venue"
        ]
    )

    return df


# ============================================================
# 3. CREATE PREPROCESSOR
# ============================================================

def create_preprocessor():
    categorical_features = [
        "format",
        "gender",
        "team1",
        "team2",
        "venue"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ]
    )

    return preprocessor


# ============================================================
# 4. CREATE WINNER CLASSIFICATION MODEL
# ============================================================

def create_winner_model():
    model = Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1
                )
            )
        ]
    )

    return model


# ============================================================
# 5. CREATE SCORE REGRESSION MODEL
# ============================================================

def create_score_model():
    model = Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                )
            )
        ]
    )

    return model


# ============================================================
# 6. TRAIN ALL MODELS
# ============================================================

def train_models():

    df = load_match_data()

    if df.empty:
        raise ValueError(
            "No completed international match data found in the database."
        )

    df = prepare_data(df)

    if len(df) < 20:
        raise ValueError(
            "Not enough international match data available for ML training."
        )

    features = [
        "format",
        "gender",
        "team1",
        "team2",
        "venue"
    ]

    # --------------------------------------------------------
    # WINNER MODEL
    # --------------------------------------------------------

    X = df[features]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    winner_model = create_winner_model()

    winner_model.fit(X_train, y_train)

    winner_predictions = winner_model.predict(X_test)

    winner_metrics = {
        "accuracy": accuracy_score(
            y_test,
            winner_predictions
        ),
        "precision": precision_score(
            y_test,
            winner_predictions,
            average="macro",
            zero_division=0
        ),
        "recall": recall_score(
            y_test,
            winner_predictions,
            average="macro",
            zero_division=0
        ),
        "f1": f1_score(
            y_test,
            winner_predictions,
            average="macro",
            zero_division=0
        )
    }

    # --------------------------------------------------------
    # SCORE MODELS
    # --------------------------------------------------------

    score_df = df.dropna(
        subset=[
            "team1_runs",
            "team2_runs"
        ]
    ).copy()

    if len(score_df) >= 20:

        X_score = score_df[features]

        y_team1 = score_df["team1_runs"]
        y_team2 = score_df["team2_runs"]

        (
            X_train_score,
            X_test_score,
            y1_train,
            y1_test,
            y2_train,
            y2_test
        ) = train_test_split(
            X_score,
            y_team1,
            y_team2,
            test_size=0.20,
            random_state=42
        )

        team1_model = create_score_model()
        team2_model = create_score_model()

        team1_model.fit(
            X_train_score,
            y1_train
        )

        team2_model.fit(
            X_train_score,
            y2_train
        )

        team1_predictions = team1_model.predict(
            X_test_score
        )

        team2_predictions = team2_model.predict(
            X_test_score
        )

        team1_r2 = r2_score(
            y1_test,
            team1_predictions
        )

        team2_r2 = r2_score(
            y2_test,
            team2_predictions
        )

    else:
        team1_model = None
        team2_model = None
        team1_r2 = None
        team2_r2 = None

    # --------------------------------------------------------
    # FINAL MODELS — TRAIN ON ALL AVAILABLE DATA
    # --------------------------------------------------------

    final_winner_model = create_winner_model()

    final_winner_model.fit(
        X,
        y
    )

    if len(score_df) >= 20:

        final_team1_model = create_score_model()
        final_team2_model = create_score_model()

        final_team1_model.fit(
            X_score,
            y_team1
        )

        final_team2_model.fit(
            X_score,
            y_team2
        )

    else:
        final_team1_model = None
        final_team2_model = None

    # --------------------------------------------------------
    # AVAILABLE FILTER VALUES
    # --------------------------------------------------------

    teams = sorted(
        set(df["team1"].dropna())
        | set(df["team2"].dropna())
    )

    formats = sorted(
        df["format"].dropna().unique().tolist()
    )

    genders = sorted(
        df["gender"].dropna().unique().tolist()
    )

    venues = sorted(
        df["venue"].dropna().unique().tolist()
    )

    return {
        "winner_model": final_winner_model,
        "team1_model": final_team1_model,
        "team2_model": final_team2_model,

        "winner_metrics": winner_metrics,

        "score_metrics": {
            "team1_r2": team1_r2,
            "team2_r2": team2_r2
        },

        "teams": teams,
        "formats": formats,
        "genders": genders,
        "venues": venues,

        "training_matches": len(df),
        "score_training_matches": len(score_df)
    }


# ============================================================
# 7. GET MODEL BUNDLE
# ============================================================

_MODEL_BUNDLE = None


def get_model_bundle():

    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is None:
        _MODEL_BUNDLE = train_models()

    return _MODEL_BUNDLE


# ============================================================
# 8. PREDICT A MATCH
# ============================================================

def predict_match(
    team1,
    team2,
    match_format,
    venue,
    gender="men",
    bundle=None
):

    if team1 == team2:
        raise ValueError(
            "Team 1 and Team 2 must be different."
        )

    if bundle is None:
        bundle = get_model_bundle()

    winner_model = bundle["winner_model"]

    input_data = pd.DataFrame(
        [
            {
                "format": match_format,
                "gender": gender,
                "team1": team1,
                "team2": team2,
                "venue": venue
            }
        ]
    )

    # --------------------------------------------------------
    # WINNER PREDICTION
    # --------------------------------------------------------

    prediction = winner_model.predict(
        input_data
    )[0]

    probabilities = winner_model.predict_proba(
        input_data
    )[0]

    classes = winner_model.named_steps[
        "classifier"
    ].classes_

    probability_map = {
        int(cls): float(prob)
        for cls, prob in zip(
            classes,
            probabilities
        )
    }

    team1_probability = probability_map.get(
        1,
        0.0
    )

    team2_probability = probability_map.get(
        0,
        0.0
    )

    predicted_winner = (
        team1
        if prediction == 1
        else team2
    )

    confidence = max(
        team1_probability,
        team2_probability
    )

    # --------------------------------------------------------
    # SCORE PREDICTION
    # --------------------------------------------------------

    team1_model = bundle["team1_model"]
    team2_model = bundle["team2_model"]

    if (
        team1_model is not None
        and team2_model is not None
    ):

        team1_runs = float(
            team1_model.predict(
                input_data
            )[0]
        )

        team2_runs = float(
            team2_model.predict(
                input_data
            )[0]
        )

        # Prevent impossible negative scores
        team1_runs = max(
            0,
            team1_runs
        )

        team2_runs = max(
            0,
            team2_runs
        )

    else:

        team1_runs = None
        team2_runs = None

    return {
        "team1": team1,
        "team2": team2,

        "winner": predicted_winner,

        "confidence": confidence,

        "team1_probability": team1_probability,
        "team2_probability": team2_probability,

        "winner_probabilities": {
            team1: team1_probability,
            team2: team2_probability
        },

        "team1_runs": team1_runs,
        "team2_runs": team2_runs
    }


# ============================================================
# 9. TEST MODEL FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRICKET ML MODEL")
    print("Real International Cricket Data")
    print("=" * 60)

    bundle = get_model_bundle()

    print()
    print("ML model trained successfully.")
    print(
        f"Training matches: {bundle['training_matches']}"
    )
    print(
        f"Score training matches: "
        f"{bundle['score_training_matches']}"
    )
    print(
        f"Teams available: {len(bundle['teams'])}"
    )
    print(
        f"Formats available: {', '.join(bundle['formats'])}"
    )
    print(
        f"Genders available: {', '.join(bundle['genders'])}"
    )
    print(
        f"Venues available: {len(bundle['venues'])}"
    )

    print()
    print("-" * 60)
    print("WINNER MODEL PERFORMANCE")
    print("-" * 60)

    metrics = bundle["winner_metrics"]

    print(
        f"Accuracy: "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision (Macro): "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall (Macro): "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"F1 Score (Macro): "
        f"{metrics['f1'] * 100:.2f}%"
    )

    print()
    print("-" * 60)
    print("SCORE MODEL PERFORMANCE")
    print("-" * 60)

    score_metrics = bundle["score_metrics"]

    if score_metrics["team1_r2"] is not None:

        print(
            f"Team 1 Score R2: "
            f"{score_metrics['team1_r2']:.4f}"
        )

        print(
            f"Team 2 Score R2: "
            f"{score_metrics['team2_r2']:.4f}"
        )

    else:
        print(
            "Score metrics could not be calculated."
        )

    print()
    print("=" * 60)
    print("MODEL READY")
    print("=" * 60)