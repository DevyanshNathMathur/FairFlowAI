import math

from pathlib import Path


import joblib

import numpy as np

import sklearn


from sklearn.ensemble import (
    ExtraTreesRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    median_absolute_error,
    r2_score
)

from sklearn.model_selection import (
    train_test_split
)


from engine.simulation import (
    run_simulation
)


MAX_STAGES = 6


MODEL_VERSION = (
    "fairflow-wait-model-v2-dynamic-stages"
)


TRAINING_SAMPLE_COUNT = 6000

TRAINING_RANDOM_SEED = 42


PROJECT_ROOT = (
    Path(
        __file__
    )
    .resolve()
    .parent
    .parent
)


MODEL_DIRECTORY = (
    PROJECT_ROOT
    /
    "models"
)


MODEL_PATH = (
    MODEL_DIRECTORY
    /
    "fairflow_wait_model.joblib"
)



# =========================================================
# FEATURES
# =========================================================

FEATURE_NAMES = [

    "visitor_count",

    "session_hours",

    "visitors_per_hour",

    "stage_count"

]


for stage_index in range(
    1,
    MAX_STAGES + 1
):

    FEATURE_NAMES.extend(

        [

            f"stage_{stage_index}_active",

            f"stage_{stage_index}_counters",

            f"stage_{stage_index}_service_time",

            f"stage_{stage_index}_capacity_per_hour",

            f"stage_{stage_index}_pressure"

        ]

    )


FEATURE_NAMES.extend(

    [

        "general_percent",

        "elderly_percent",

        "pregnant_percent",

        "mobility_percent",

        "priority_percent",

        "total_counters",

        "maximum_stage_pressure",

        "average_stage_pressure",

        "minimum_stage_pressure",

        "total_nominal_service_time"

    ]

)



_MODEL_BUNDLE = None



# =========================================================
# CAPACITY
# =========================================================

def calculate_stage_capacity(
    counters,
    service_time
):

    counters = float(
        counters
    )

    service_time = float(
        service_time
    )

    if (

        counters <= 0

        or

        service_time <= 0

    ):

        return 0.0

    return (

        counters

        *
        (
            60.0
            /
            service_time
        )

    )



# =========================================================
# FEATURE VECTOR
# =========================================================

def build_feature_vector(
    visitor_count,
    session_hours,
    stages,
    group_mix
):

    visitor_count = float(
        visitor_count
    )

    session_hours = float(
        session_hours
    )

    if session_hours <= 0:

        raise ValueError(

            "session_hours must be greater than 0"

        )

    if not (

        1
        <=
        len(
            stages
        )
        <=
        MAX_STAGES

    ):

        raise ValueError(

            "The ML model supports between "
            f"1 and {MAX_STAGES} stages."

        )

    visitors_per_hour = (

        visitor_count
        /
        session_hours

    )

    features = [

        visitor_count,

        session_hours,

        visitors_per_hour,

        float(
            len(
                stages
            )
        )

    ]

    stage_pressures = []

    total_counters = 0.0

    total_nominal_service_time = 0.0

    for stage_index in range(
        MAX_STAGES
    ):

        if (
            stage_index
            <
            len(
                stages
            )
        ):

            stage = stages[
                stage_index
            ]

            counters = float(

                stage[
                    "counters"
                ]

            )

            service_time = float(

                stage[
                    "service_time"
                ]

            )

            capacity = (
                calculate_stage_capacity(

                    counters=
                        counters,

                    service_time=
                        service_time

                )
            )

            pressure = (

                visitors_per_hour
                /
                capacity

                if capacity > 0

                else 0.0

            )

            stage_pressures.append(
                pressure
            )

            total_counters += (
                counters
            )

            total_nominal_service_time += (
                service_time
            )

            features.extend(

                [

                    1.0,

                    counters,

                    service_time,

                    capacity,

                    pressure

                ]

            )

        else:

            features.extend(

                [

                    0.0,

                    0.0,

                    0.0,

                    0.0,

                    0.0

                ]

            )

    general = float(

        group_mix.get(
            "general",
            0.0
        )

    )

    elderly = float(

        group_mix.get(
            "elderly",
            0.0
        )

    )

    pregnant = float(

        group_mix.get(
            "pregnant",
            0.0
        )

    )

    mobility = float(

        group_mix.get(
            "mobility",
            0.0
        )

    )

    priority = (

        elderly
        +
        pregnant
        +
        mobility

    )

    maximum_pressure = (

        max(
            stage_pressures
        )

        if stage_pressures

        else 0.0

    )

    average_pressure = (

        sum(
            stage_pressures
        )
        /
        len(
            stage_pressures
        )

        if stage_pressures

        else 0.0

    )

    minimum_pressure = (

        min(
            stage_pressures
        )

        if stage_pressures

        else 0.0

    )

    features.extend(

        [

            general,

            elderly,

            pregnant,

            mobility,

            priority,

            total_counters,

            maximum_pressure,

            average_pressure,

            minimum_pressure,

            total_nominal_service_time

        ]

    )

    return features



# =========================================================
# TRAINING SCENARIOS
# =========================================================

def generate_training_scenario(
    rng
):

    stage_count = int(

        rng.integers(
            2,
            MAX_STAGES + 1
        )

    )

    visitor_count = int(

        rng.integers(
            50,
            1001
        )

    )

    session_hours = round(

        float(

            rng.uniform(
                2.0,
                12.0
            )

        ),

        1

    )

    stages = []

    for stage_index in range(
        stage_count
    ):

        counters = int(

            rng.integers(
                1,
                9
            )

        )

        if (
            float(
                rng.random()
            )
            <
            0.05
        ):

            service_time = float(

                rng.uniform(
                    15.0,
                    60.0
                )

            )

        else:

            service_time = float(

                rng.uniform(
                    0.5,
                    15.0
                )

            )

        stages.append(

            {

                "name":
                    f"Stage {stage_index + 1}",

                "counters":
                    counters,

                "service_time":
                    round(
                        service_time,
                        1
                    )

            }

        )

    mix = (

        rng.dirichlet(

            np.array(
                [
                    5.0,
                    1.3,
                    1.2,
                    0.9
                ]
            )

        )

        *
        100.0

    )

    group_mix = {

        "general":
            float(
                mix[0]
            ),

        "elderly":
            float(
                mix[1]
            ),

        "pregnant":
            float(
                mix[2]
            ),

        "mobility":
            float(
                mix[3]
            )

    }

    return (

        visitor_count,

        session_hours,

        stages,

        group_mix

    )



def generate_training_data(

    sample_count=
        TRAINING_SAMPLE_COUNT,

    random_seed=
        TRAINING_RANDOM_SEED

):

    rng = (
        np.random.default_rng(
            random_seed
        )
    )

    feature_rows = []

    wait_targets = []

    for index in range(
        sample_count
    ):

        (

            visitor_count,

            session_hours,

            stages,

            group_mix

        ) = generate_training_scenario(
            rng
        )

        result = run_simulation(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stages=
                stages,

            group_mix=
                group_mix,

            random_seed=
                10000
                +
                index

        )

        features = (
            build_feature_vector(

                visitor_count=
                    visitor_count,

                session_hours=
                    session_hours,

                stages=
                    stages,

                group_mix=
                    group_mix

            )
        )

        average_wait = float(

            result[
                "summary"
            ][
                "average_wait"
            ]

        )

        feature_rows.append(
            features
        )

        wait_targets.append(
            average_wait
        )

    X = np.array(

        feature_rows,

        dtype=float

    )

    y_wait = np.array(

        wait_targets,

        dtype=float

    )

    return (
        X,
        y_wait
    )



# =========================================================
# TRAIN MODEL
# =========================================================

def train_ml_model(

    sample_count=
        TRAINING_SAMPLE_COUNT,

    random_seed=
        TRAINING_RANDOM_SEED

):

    X, y_wait = (
        generate_training_data(

            sample_count=
                sample_count,

            random_seed=
                random_seed

        )
    )

    y_log = (
        np.log1p(
            y_wait
        )
    )

    (

        X_train,

        X_test,

        y_train_log,

        y_test_log,

        y_train_wait,

        y_test_wait

    ) = train_test_split(

        X,

        y_log,

        y_wait,

        test_size=
            0.20,

        random_state=
            random_seed

    )

    model = (
        ExtraTreesRegressor(

            n_estimators=
                350,

            max_depth=
                20,

            min_samples_leaf=
                2,

            max_features=
                0.9,

            random_state=
                random_seed,

            n_jobs=
                -1

        )
    )

    model.fit(

        X_train,

        y_train_log

    )

    predicted_log = (
        model.predict(
            X_test
        )
    )

    predicted_wait = (
        np.expm1(
            predicted_log
        )
    )

    predicted_wait = (
        np.maximum(
            predicted_wait,
            0.0
        )
    )

    wait_mae = (
        mean_absolute_error(

            y_test_wait,

            predicted_wait

        )
    )

    wait_median_ae = (
        median_absolute_error(

            y_test_wait,

            predicted_wait

        )
    )

    wait_r2 = (
        r2_score(

            y_test_wait,

            predicted_wait

        )
    )

    log_r2 = (
        r2_score(

            y_test_log,

            predicted_log

        )
    )

    metrics = {

        "training_samples":
            int(
                len(
                    X_train
                )
            ),

        "test_samples":
            int(
                len(
                    X_test
                )
            ),

        "total_samples":
            int(
                len(
                    X
                )
            ),

        "wait_mae":
            round(
                float(
                    wait_mae
                ),
                2
            ),

        "wait_median_ae":
            round(
                float(
                    wait_median_ae
                ),
                2
            ),

        "wait_r2":
            round(
                float(
                    wait_r2
                ),
                3
            ),

        "wait_log_r2":
            round(
                float(
                    log_r2
                ),
                3
            )

    }

    return {

        "model":
            model,

        "metrics":
            metrics,

        "feature_names":
            list(
                FEATURE_NAMES
            ),

        "model_version":
            MODEL_VERSION,

        "training_sample_count":
            int(
                sample_count
            ),

        "training_random_seed":
            int(
                random_seed
            ),

        "sklearn_version":
            sklearn.__version__

    }



# =========================================================
# MODEL PERSISTENCE
# =========================================================

def is_model_bundle_compatible(
    bundle
):

    if not isinstance(
        bundle,
        dict
    ):

        return False

    required_keys = {

        "model",

        "metrics",

        "feature_names",

        "model_version",

        "training_sample_count",

        "training_random_seed",

        "sklearn_version"

    }

    if not (
        required_keys
        .issubset(
            bundle.keys()
        )
    ):

        return False

    if (
        bundle[
            "model_version"
        ]
        !=
        MODEL_VERSION
    ):

        return False

    if (
        bundle[
            "feature_names"
        ]
        !=
        FEATURE_NAMES
    ):

        return False

    if (
        int(
            bundle[
                "training_sample_count"
            ]
        )
        !=
        TRAINING_SAMPLE_COUNT
    ):

        return False

    if (
        int(
            bundle[
                "training_random_seed"
            ]
        )
        !=
        TRAINING_RANDOM_SEED
    ):

        return False

    if (
        bundle[
            "sklearn_version"
        ]
        !=
        sklearn.__version__
    ):

        return False

    return True



def save_model_bundle(
    bundle
):

    MODEL_DIRECTORY.mkdir(

        parents=True,

        exist_ok=True

    )

    temporary_path = (

        MODEL_PATH
        .with_suffix(

            MODEL_PATH.suffix
            +
            ".tmp"

        )

    )

    joblib.dump(

        bundle,

        temporary_path,

        compress=3

    )

    temporary_path.replace(
        MODEL_PATH
    )



def load_saved_model_bundle():

    if not (
        MODEL_PATH.exists()
    ):

        return None

    try:

        bundle = (
            joblib.load(
                MODEL_PATH
            )
        )

    except Exception:

        return None

    if not (
        is_model_bundle_compatible(
            bundle
        )
    ):

        return None

    return bundle



def delete_saved_model():

    global _MODEL_BUNDLE

    _MODEL_BUNDLE = None

    if (
        MODEL_PATH.exists()
    ):

        MODEL_PATH.unlink()



def get_ml_model(
    force_retrain=False
):

    global _MODEL_BUNDLE

    if force_retrain:

        _MODEL_BUNDLE = None

    if (

        _MODEL_BUNDLE
        is not None

        and

        not force_retrain

    ):

        return _MODEL_BUNDLE

    if not force_retrain:

        saved_bundle = (
            load_saved_model_bundle()
        )

        if (
            saved_bundle
            is not None
        ):

            print(

                "Loaded saved FairFlow AI ML model."

            )

            _MODEL_BUNDLE = (
                saved_bundle
            )

            return _MODEL_BUNDLE

    print(

        "Training FairFlow AI dynamic-stage ML model. "
        "This happens once for the new model version."

    )

    bundle = (
        train_ml_model(

            sample_count=
                TRAINING_SAMPLE_COUNT,

            random_seed=
                TRAINING_RANDOM_SEED

        )
    )

    save_model_bundle(
        bundle
    )

    _MODEL_BUNDLE = (
        bundle
    )

    print(

        "Saved FairFlow AI ML model to "
        f"{MODEL_PATH}."

    )

    return _MODEL_BUNDLE



# =========================================================
# PREDICTION
# =========================================================

def predict_wait(
    visitor_count,
    session_hours,
    stages,
    group_mix
):

    bundle = (
        get_ml_model()
    )

    features = (
        build_feature_vector(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stages=
                stages,

            group_mix=
                group_mix

        )
    )

    X = np.array(

        [
            features
        ],

        dtype=float

    )

    predicted_log = float(

        bundle[
            "model"
        ]
        .predict(
            X
        )[0]

    )

    predicted_wait = max(

        0.0,

        math.expm1(
            predicted_log
        )

    )

    return {

        "predicted_average_wait":
            round(
                predicted_wait,
                2
            ),

        "model_metrics":
            bundle[
                "metrics"
            ]

    }



def predict_wait_batch(
    visitor_count,
    session_hours,
    stage_variants,
    group_mix
):

    bundle = (
        get_ml_model()
    )

    if not stage_variants:

        return {

            "predictions":
                [],

            "model_metrics":
                bundle[
                    "metrics"
                ]

        }

    X = np.array(

        [

            build_feature_vector(

                visitor_count=
                    visitor_count,

                session_hours=
                    session_hours,

                stages=
                    stages,

                group_mix=
                    group_mix

            )

            for stages
            in stage_variants

        ],

        dtype=float

    )

    predicted_log = (

        bundle[
            "model"
        ]
        .predict(
            X
        )

    )

    predicted_wait = (
        np.expm1(
            predicted_log
        )
    )

    predicted_wait = (
        np.maximum(
            predicted_wait,
            0.0
        )
    )

    return {

        "predictions": [

            round(
                float(
                    value
                ),
                2
            )

            for value in
            predicted_wait

        ],

        "model_metrics":
            bundle[
                "metrics"
            ]

    }



def compare_prediction(
    visitor_count,
    session_hours,
    stages,
    group_mix
):

    prediction = (
        predict_wait(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stages=
                stages,

            group_mix=
                group_mix

        )
    )

    simulation = (
        run_simulation(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stages=
                stages,

            group_mix=
                group_mix,

            random_seed=42

        )
    )

    actual_wait = float(

        simulation[
            "summary"
        ][
            "average_wait"
        ]

    )

    predicted_wait = float(

        prediction[
            "predicted_average_wait"
        ]

    )

    return {

        "predicted_average_wait":
            predicted_wait,

        "simulated_average_wait":
            round(
                actual_wait,
                2
            ),

        "absolute_difference":
            round(

                abs(

                    actual_wait
                    -
                    predicted_wait

                ),

                2

            ),

        "model_metrics":
            prediction[
                "model_metrics"
            ]

    }



if __name__ == "__main__":

    bundle = (
        get_ml_model()
    )

    print(
        "\nMODEL EVALUATION"
    )

    print(
        bundle[
            "metrics"
        ]
    )

    print(
        f"\nModel file: {MODEL_PATH}"
    )