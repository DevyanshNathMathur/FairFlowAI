from engine.ml_model import (
    predict_wait,
    predict_wait_batch
)

from engine.optimizer import (
    generate_allocations
)

from engine.simulation import (
    run_simulation
)


MAX_COUNTERS_PER_STAGE = 20

ML_CANDIDATE_LIMIT = 2500


def build_candidate_stages(
    stages,
    allocation
):

    return [

        {
            "name":
                stage[
                    "name"
                ],

            "counters":
                int(
                    allocation[
                        index
                    ]
                ),

            "service_time":
                float(
                    stage[
                        "service_time"
                    ]
                )
        }

        for index, stage
        in enumerate(
            stages
        )

    ]


def calculate_decision_score(
    simulation_result
):

    average_wait = float(

        simulation_result[
            "summary"
        ][
            "average_wait"
        ]

    )

    fairness_gap = float(

        simulation_result[
            "summary"
        ][
            "fairness_gap"
        ]

    )

    bottleneck_wait = max(

        float(
            stage[
                "average_wait"
            ]
        )

        for stage
        in simulation_result[
            "stages"
        ]

    )

    utilization_penalty = sum(

        max(

            0.0,

            float(
                stage[
                    "utilization"
                ]
            )
            -
            90.0

        )

        for stage
        in simulation_result[
            "stages"
        ]

    )

    return (

        average_wait

        +
        0.60
        *
        max(
            fairness_gap,
            0.0
        )

        +
        0.25
        *
        bottleneck_wait

        +
        0.03
        *
        utilization_penalty

    )


def build_stage_changes(
    stages,
    baseline_allocation,
    recommended_allocation
):

    changes = []

    for index, stage in enumerate(
        stages
    ):

        before = int(

            baseline_allocation[
                index
            ]

        )

        after = int(

            recommended_allocation[
                index
            ]

        )

        changes.append(

            {
                "name":
                    stage[
                        "name"
                    ],

                "before":
                    before,

                "after":
                    after,

                "difference":
                    after
                    -
                    before
            }

        )

    return changes


def _plural_counter(
    value
):

    return (

        "counter"

        if abs(
            int(
                value
            )
        ) == 1

        else "counters"

    )


def build_recommendation_text(
    stage_changes,
    baseline_result,
    recommended_result
):

    changed = any(

        item[
            "difference"
        ]
        !=
        0

        for item
        in stage_changes

    )

    current_wait = float(

        baseline_result[
            "summary"
        ][
            "average_wait"
        ]

    )

    recommended_wait = float(

        recommended_result[
            "summary"
        ][
            "average_wait"
        ]

    )

    if not changed:

        headline = (

            "Keep the current staffing allocation."

        )

        explanation = (

            "FairFlow did not identify a stronger staffing "
            "reallocation within the configurations screened "
            "and verified. The current distribution of counters "
            "remains the recommended setup for the submitted "
            "assumptions."

        )

        return (
            headline,
            explanation
        )

    receivers = [

        item

        for item
        in stage_changes

        if item[
            "difference"
        ] > 0

    ]

    donors = [

        item

        for item
        in stage_changes

        if item[
            "difference"
        ] < 0

    ]

    if (
        len(
            receivers
        )
        ==
        1
    ):

        headline = (

            "Reallocate staffing toward "
            f"{receivers[0]['name']}."

        )

    else:

        headline = (

            "Rebalance staffing across the service flow."

        )

    if (

        len(
            donors
        )
        ==
        1

        and

        len(
            receivers
        )
        ==
        1

    ):

        moved = min(

            abs(
                donors[0][
                    "difference"
                ]
            ),

            receivers[0][
                "difference"
            ]

        )

        change_text = (

            f"moving {moved} "
            f"{_plural_counter(moved)} "
            f"from {donors[0]['name']} "
            f"toward {receivers[0]['name']}"

        )

    else:

        change_parts = []

        for item in stage_changes:

            difference = (
                item[
                    "difference"
                ]
            )

            if difference == 0:
                continue

            sign = (

                "+"

                if difference > 0

                else ""

            )

            change_parts.append(

                f"{item['name']} "
                f"{sign}{difference}"

            )

        change_text = (

            "rebalancing counters across stages "
            f"({'; '.join(change_parts)})"

        )

    if current_wait > 0:

        reduction = max(

            0.0,

            (
                current_wait
                -
                recommended_wait
            )
            /
            current_wait
            *
            100.0

        )

    else:

        reduction = 0.0

    explanation = (

        f"FairFlow recommends {change_text}. "
        "The simulated average waiting time changes "
        f"from {current_wait:.2f} minutes to "
        f"{recommended_wait:.2f} minutes, representing "
        f"an estimated {reduction:.1f}% reduction while "
        "keeping the total number of counters unchanged."

    )

    return (
        headline,
        explanation
    )


def build_fairness_insight(
    baseline_fairness_gap,
    recommended_fairness_gap
):

    baseline_fairness_gap = float(
        baseline_fairness_gap
    )

    recommended_fairness_gap = float(
        recommended_fairness_gap
    )

    if (

        recommended_fairness_gap

        <
        baseline_fairness_gap
        -
        0.01

    ):

        return (

            "The recommended setup also reduces the "
            "waiting-time disadvantage experienced by "
            "priority visitor groups."

        )

    if (

        recommended_fairness_gap

        >
        baseline_fairness_gap
        +
        0.01

    ):

        return (

            "The recommendation improves operational "
            "performance, although the simulated fairness "
            "gap is slightly higher and should be reviewed "
            "before implementation."

        )

    return (

        "The recommendation keeps the simulated fairness "
        "gap broadly similar to the current setup."

    )


def generate_ai_recommendation(
    visitor_count,
    session_hours,
    stages,
    group_mix,
    verification_limit=5
):

    baseline_result = (
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

    baseline_allocation = [

        int(
            stage[
                "counters"
            ]
        )

        for stage
        in stages

    ]

    total_counters = sum(
        baseline_allocation
    )

    allocations = (
        generate_allocations(

            total_counters=
                total_counters,

            stage_count=
                len(
                    stages
                ),

            max_per_stage=
                MAX_COUNTERS_PER_STAGE,

            limit=
                ML_CANDIDATE_LIMIT,

            random_seed=42,

            baseline_allocation=
                baseline_allocation

        )
    )

    if not allocations:

        allocations = [
            baseline_allocation
        ]

    stage_variants = [

        build_candidate_stages(

            stages=
                stages,

            allocation=
                allocation

        )

        for allocation
        in allocations

    ]

    batch_prediction = (
        predict_wait_batch(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stage_variants=
                stage_variants,

            group_mix=
                group_mix

        )
    )

    model_metrics = (
        batch_prediction[
            "model_metrics"
        ]
    )

    predictions = (
        batch_prediction[
            "predictions"
        ]
    )

    ranked_candidates = sorted(

        zip(

            allocations,

            stage_variants,

            predictions

        ),

        key=lambda item:
            item[2]

    )

    verification_limit = max(

        1,

        int(
            verification_limit
        )

    )

    selected = (
        ranked_candidates[
            :verification_limit
        ]
    )

    baseline_tuple = tuple(
        baseline_allocation
    )

    if not any(

        tuple(
            item[0]
        )
        ==
        baseline_tuple

        for item
        in selected

    ):

        baseline_index = next(

            (

                index

                for index, allocation
                in enumerate(
                    allocations
                )

                if tuple(
                    allocation
                )
                ==
                baseline_tuple

            ),

            None

        )

        if (
            baseline_index
            is not None
        ):

            selected.append(

                (

                    allocations[
                        baseline_index
                    ],

                    stage_variants[
                        baseline_index
                    ],

                    predictions[
                        baseline_index
                    ]

                )

            )

    verified_candidates = []

    for (
        allocation,
        candidate_stages,
        ml_prediction
    ) in selected:

        simulation_result = (
            run_simulation(

                visitor_count=
                    visitor_count,

                session_hours=
                    session_hours,

                stages=
                    candidate_stages,

                group_mix=
                    group_mix,

                random_seed=42

            )
        )

        verified_candidates.append(

            {

                "allocation":
                    allocation,

                "stages":
                    candidate_stages,

                "ml_predicted_wait":
                    float(
                        ml_prediction
                    ),

                "simulation":
                    simulation_result,

                "decision_score":
                    calculate_decision_score(
                        simulation_result
                    )

            }

        )

    best_candidate = min(

        verified_candidates,

        key=lambda item:
            item[
                "decision_score"
            ]

    )

    recommended_result = (
        best_candidate[
            "simulation"
        ]
    )

    recommended_allocation = (
        best_candidate[
            "allocation"
        ]
    )

    baseline_score = (
        calculate_decision_score(
            baseline_result
        )
    )

    recommended_score = float(

        best_candidate[
            "decision_score"
        ]

    )

    baseline_prediction = (

        predict_wait(

            visitor_count=
                visitor_count,

            session_hours=
                session_hours,

            stages=
                stages,

            group_mix=
                group_mix

        )[
            "predicted_average_wait"
        ]

    )

    stage_changes = (
        build_stage_changes(

            stages=
                stages,

            baseline_allocation=
                baseline_allocation,

            recommended_allocation=
                recommended_allocation

        )
    )

    (
        headline,
        explanation

    ) = build_recommendation_text(

        stage_changes=
            stage_changes,

        baseline_result=
            baseline_result,

        recommended_result=
            recommended_result

    )

    baseline_wait = float(

        baseline_result[
            "summary"
        ][
            "average_wait"
        ]

    )

    recommended_wait = float(

        recommended_result[
            "summary"
        ][
            "average_wait"
        ]

    )

    wait_improvement_percent = (

        max(

            0.0,

            (
                baseline_wait
                -
                recommended_wait
            )
            /
            baseline_wait
            *
            100.0

        )

        if baseline_wait > 0

        else 0.0

    )

    baseline_fairness_gap = float(

        baseline_result[
            "summary"
        ][
            "fairness_gap"
        ]

    )

    recommended_fairness_gap = float(

        recommended_result[
            "summary"
        ][
            "fairness_gap"
        ]

    )

    fairness_insight = (
        build_fairness_insight(

            baseline_fairness_gap=
                baseline_fairness_gap,

            recommended_fairness_gap=
                recommended_fairness_gap

        )
    )

    return {

        "baseline":
            baseline_result,

        "recommended":
            recommended_result,

        "baseline_score":
            round(
                baseline_score,
                4
            ),

        "recommended_score":
            round(
                recommended_score,
                4
            ),

        "baseline_allocation":
            baseline_allocation,

        "recommended_allocation":
            list(
                recommended_allocation
            ),

        "stage_changes":
            stage_changes,

        "changed":
            (
                baseline_allocation
                !=
                list(
                    recommended_allocation
                )
            ),

        "wait_improvement_percent":
            round(
                wait_improvement_percent,
                1
            ),

        "baseline_fairness_gap":
            round(
                baseline_fairness_gap,
                2
            ),

        "recommended_fairness_gap":
            round(
                recommended_fairness_gap,
                2
            ),

        "baseline_ml_predicted_wait":
            round(
                float(
                    baseline_prediction
                ),
                2
            ),

        "recommended_ml_predicted_wait":
            round(

                float(

                    best_candidate[
                        "ml_predicted_wait"
                    ]

                ),

                2

            ),

        "configurations_screened_by_ml":
            len(
                allocations
            ),

        "configurations_verified_by_simulation":
            len(
                verified_candidates
            ),

        "model_metrics":
            model_metrics,

        "headline":
            headline,

        "explanation":
            explanation,

        "fairness_insight":
            fairness_insight,

        "verified_candidates":
            verified_candidates

    }