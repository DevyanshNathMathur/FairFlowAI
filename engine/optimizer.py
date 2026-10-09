import random

from engine.simulation import (
    run_simulation
)


MAX_COUNTERS_PER_STAGE = 20

DEFAULT_CANDIDATE_LIMIT = 2500


def calculate_score(
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

    largest_stage_wait = max(

        float(
            stage[
                "average_wait"
            ]
        )

        for stage in
        simulation_result[
            "stages"
        ]

    )

    return (

        average_wait

        +
        0.50
        *
        max(
            fairness_gap,
            0.0
        )

        +
        0.25
        *
        largest_stage_wait

    )


def _count_bounded_allocations(
    total_counters,
    stage_count,
    max_per_stage
):

    ways = (
        [0]
        *
        (
            total_counters
            +
            1
        )
    )

    ways[0] = 1

    for _ in range(
        stage_count
    ):

        next_ways = (

            [0]
            *
            (
                total_counters
                +
                1
            )

        )

        for current_total, count in enumerate(
            ways
        ):

            if count == 0:
                continue

            for counters in range(

                1,

                max_per_stage
                +
                1

            ):

                new_total = (

                    current_total
                    +
                    counters

                )

                if (
                    new_total
                    >
                    total_counters
                ):

                    break

                next_ways[
                    new_total
                ] += count

        ways = (
            next_ways
        )

    return ways[
        total_counters
    ]


def _enumerate_allocations(
    total_counters,
    stage_count,
    max_per_stage
):

    allocations = []

    def recurse(
        prefix,
        remaining,
        slots_left
    ):

        if slots_left == 1:

            if (
                1
                <=
                remaining
                <=
                max_per_stage
            ):

                allocations.append(

                    prefix
                    +
                    [
                        remaining
                    ]

                )

            return

        minimum_for_rest = (

            slots_left
            -
            1

        )

        maximum_for_current = min(

            max_per_stage,

            remaining
            -
            minimum_for_rest

        )

        minimum_for_current = max(

            1,

            remaining
            -
            (
                max_per_stage
                *
                minimum_for_rest
            )

        )

        for counters in range(

            minimum_for_current,

            maximum_for_current
            +
            1

        ):

            recurse(

                prefix
                +
                [
                    counters
                ],

                remaining
                -
                counters,

                slots_left
                -
                1

            )

    recurse(

        [],

        total_counters,

        stage_count

    )

    return allocations


def _random_valid_allocation(
    rng,
    total_counters,
    stage_count,
    max_per_stage
):

    remaining = (
        total_counters
    )

    allocation = []

    for index in range(
        stage_count
        -
        1
    ):

        slots_after = (

            stage_count
            -
            index
            -
            1

        )

        minimum = max(

            1,

            remaining
            -
            (
                max_per_stage
                *
                slots_after
            )

        )

        maximum = min(

            max_per_stage,

            remaining
            -
            slots_after

        )

        counters = (
            rng.randint(
                minimum,
                maximum
            )
        )

        allocation.append(
            counters
        )

        remaining -= (
            counters
        )

    allocation.append(
        remaining
    )

    return allocation


def _balanced_allocation(
    total_counters,
    stage_count,
    max_per_stage
):

    allocation = (

        [1]
        *
        stage_count

    )

    remaining = (

        total_counters
        -
        stage_count

    )

    index = 0

    while remaining > 0:

        if (
            allocation[
                index
            ]
            <
            max_per_stage
        ):

            allocation[
                index
            ] += 1

            remaining -= 1

        index = (

            (
                index
                +
                1
            )
            %
            stage_count

        )

    return allocation


def generate_allocations(
    total_counters,
    stage_count,
    max_per_stage=
        MAX_COUNTERS_PER_STAGE,
    limit=
        DEFAULT_CANDIDATE_LIMIT,
    random_seed=42,
    baseline_allocation=None
):

    """
    Generate feasible allocations while preserving
    the total number of counters.

    Small search spaces are evaluated completely.
    Large spaces are sampled deterministically so
    2-6 stage workflows remain responsive.
    """

    total_counters = int(
        total_counters
    )

    stage_count = int(
        stage_count
    )

    max_per_stage = int(
        max_per_stage
    )

    limit = max(
        1,
        int(
            limit
        )
    )

    if stage_count < 1:
        return []

    if (
        total_counters
        <
        stage_count
    ):
        return []

    if (
        total_counters
        >
        (
            stage_count
            *
            max_per_stage
        )
    ):
        return []

    exact_count = (
        _count_bounded_allocations(

            total_counters=
                total_counters,

            stage_count=
                stage_count,

            max_per_stage=
                max_per_stage

        )
    )

    if exact_count <= limit:

        return _enumerate_allocations(

            total_counters=
                total_counters,

            stage_count=
                stage_count,

            max_per_stage=
                max_per_stage

        )

    candidates = set()

    if (
        baseline_allocation
        is not None
    ):

        baseline = tuple(

            int(
                value
            )

            for value in
            baseline_allocation

        )

        if (

            len(
                baseline
            )
            ==
            stage_count

            and

            sum(
                baseline
            )
            ==
            total_counters

            and

            all(

                1
                <=
                value
                <=
                max_per_stage

                for value
                in baseline

            )

        ):

            candidates.add(
                baseline
            )

            for donor in range(
                stage_count
            ):

                for receiver in range(
                    stage_count
                ):

                    if (
                        donor
                        ==
                        receiver
                    ):

                        continue

                    max_shift = min(

                        3,

                        baseline[
                            donor
                        ]
                        -
                        1,

                        max_per_stage
                        -
                        baseline[
                            receiver
                        ]

                    )

                    for shift in range(

                        1,

                        max_shift
                        +
                        1

                    ):

                        changed = list(
                            baseline
                        )

                        changed[
                            donor
                        ] -= shift

                        changed[
                            receiver
                        ] += shift

                        candidates.add(
                            tuple(
                                changed
                            )
                        )

    candidates.add(

        tuple(

            _balanced_allocation(

                total_counters=
                    total_counters,

                stage_count=
                    stage_count,

                max_per_stage=
                    max_per_stage

            )

        )

    )

    rng = random.Random(
        random_seed
    )

    attempts = 0

    max_attempts = (
        limit
        *
        40
    )

    while (

        len(
            candidates
        )
        <
        limit

        and

        attempts
        <
        max_attempts

    ):

        attempts += 1

        allocation = (
            _random_valid_allocation(

                rng=
                    rng,

                total_counters=
                    total_counters,

                stage_count=
                    stage_count,

                max_per_stage=
                    max_per_stage

            )
        )

        candidates.add(
            tuple(
                allocation
            )
        )

    ordered = sorted(
        candidates
    )

    if (
        baseline_allocation
        is not None
    ):

        baseline_tuple = tuple(

            int(
                value
            )

            for value
            in baseline_allocation

        )

        if (
            baseline_tuple
            in candidates
        ):

            ordered.remove(
                baseline_tuple
            )

            ordered.insert(
                0,
                baseline_tuple
            )

    return [

        list(
            item
        )

        for item in
        ordered[
            :limit
        ]

    ]


def _build_candidate_stages(
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


def optimize_staffing(
    visitor_count,
    session_hours,
    stages,
    group_mix,
    candidate_limit=500
):

    baseline_allocation = [

        int(
            stage[
                "counters"
            ]
        )

        for stage in stages

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
                candidate_limit,

            baseline_allocation=
                baseline_allocation

        )
    )

    best_result = None

    best_score = None

    best_allocation = None

    for allocation in allocations:

        candidate_stages = (
            _build_candidate_stages(

                stages=
                    stages,

                allocation=
                    allocation

            )
        )

        result = (
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

        score = (
            calculate_score(
                result
            )
        )

        if (

            best_score
            is None

            or

            score
            <
            best_score

        ):

            best_score = (
                score
            )

            best_result = (
                result
            )

            best_allocation = (
                allocation
            )

    return {

        "optimized":
            best_result,

        "optimized_score":
            (
                round(
                    best_score,
                    4
                )

                if best_score
                is not None

                else None
            ),

        "optimized_allocation":
            best_allocation,

        "configurations_evaluated":
            len(
                allocations
            )

    }