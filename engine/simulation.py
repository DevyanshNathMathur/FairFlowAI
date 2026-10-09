import heapq
import random


SERVICE_MULTIPLIERS = {
    "general": 1.00,
    "elderly": 1.15,
    "pregnant": 1.10,
    "mobility": 1.20,
}

GROUP_ORDER = [
    "general",
    "elderly",
    "pregnant",
    "mobility",
]


def choose_group(rng, group_mix):
    weights = [
        max(
            0.0,
            float(
                group_mix.get(
                    group,
                    0.0
                )
            )
        )
        for group in GROUP_ORDER
    ]

    total = sum(weights)

    if total <= 0:
        return "general"

    threshold = (
        rng.random()
        * total
    )

    cumulative = 0.0

    for group, weight in zip(
        GROUP_ORDER,
        weights
    ):

        cumulative += weight

        if threshold <= cumulative:
            return group

    return GROUP_ORDER[-1]


def _validate_inputs(
    visitor_count,
    session_hours,
    stages
):

    if int(visitor_count) < 1:
        raise ValueError(
            "visitor_count must be at least 1"
        )

    if float(session_hours) <= 0:
        raise ValueError(
            "session_hours must be greater than 0"
        )

    if len(stages) < 1:
        raise ValueError(
            "At least one service stage is required"
        )

    for stage in stages:

        if int(
            stage["counters"]
        ) < 1:

            raise ValueError(
                "Each stage must have at least one counter"
            )

        if float(
            stage["service_time"]
        ) <= 0:

            raise ValueError(
                "Each stage service time must be greater than 0"
            )


def run_simulation(
    visitor_count,
    session_hours,
    stages,
    group_mix,
    random_seed=42
):

    """
    Simulate visitors moving through an ordered list
    of service stages.

    Stage names are fully customizable. The order of
    the stages in the list defines the visitor journey.
    """

    visitor_count = int(
        visitor_count
    )

    session_hours = float(
        session_hours
    )

    normalized_stages = [

        {
            "name":
                str(
                    stage["name"]
                ).strip(),

            "counters":
                int(
                    stage["counters"]
                ),

            "service_time":
                float(
                    stage["service_time"]
                )
        }

        for stage in stages

    ]

    _validate_inputs(

        visitor_count=
            visitor_count,

        session_hours=
            session_hours,

        stages=
            normalized_stages

    )

    rng = random.Random(
        random_seed
    )

    session_minutes = (
        session_hours
        * 60.0
    )

    arrivals = sorted(

        rng.uniform(
            0.0,
            session_minutes
        )

        for _ in range(
            visitor_count
        )

    )

    visitors = []

    for visitor_id, arrival_time in enumerate(
        arrivals
    ):

        group = choose_group(
            rng,
            group_mix
        )

        visitors.append(

            {
                "id":
                    visitor_id,

                "group":
                    group,

                "arrival_time":
                    arrival_time,

                "ready_time":
                    arrival_time,

                "total_wait":
                    0.0
            }

        )

    stage_results = []

    for stage in normalized_stages:

        counter_count = (
            stage["counters"]
        )

        base_service_time = (
            stage["service_time"]
        )

        counter_available = (
            [0.0]
            * counter_count
        )

        stage_waits = []

        total_busy_time = 0.0

        max_queue = 0

        pending_start_times = []

        ordered_visitors = sorted(

            visitors,

            key=lambda item: (
                item["ready_time"],
                item["id"]
            )

        )

        for visitor in ordered_visitors:

            arrival_to_stage = (
                visitor[
                    "ready_time"
                ]
            )

            while (
                pending_start_times
                and
                pending_start_times[0]
                <= arrival_to_stage
            ):

                heapq.heappop(
                    pending_start_times
                )

            counter_index = min(

                range(
                    counter_count
                ),

                key=
                    counter_available
                    .__getitem__

            )

            service_start = max(

                arrival_to_stage,

                counter_available[
                    counter_index
                ]

            )

            wait_time = max(

                0.0,

                service_start
                -
                arrival_to_stage

            )

            if wait_time > 0:

                heapq.heappush(

                    pending_start_times,

                    service_start

                )

                max_queue = max(

                    max_queue,

                    len(
                        pending_start_times
                    )

                )

            group_multiplier = (

                SERVICE_MULTIPLIERS
                .get(
                    visitor[
                        "group"
                    ],
                    1.0
                )

            )

            service_duration = (

                base_service_time

                * group_multiplier

                * rng.uniform(
                    0.85,
                    1.15
                )

            )

            service_end = (

                service_start
                +
                service_duration

            )

            counter_available[
                counter_index
            ] = service_end

            total_busy_time += (
                service_duration
            )

            visitor[
                "ready_time"
            ] = service_end

            visitor[
                "total_wait"
            ] += wait_time

            stage_waits.append(
                wait_time
            )

        average_wait = (

            sum(
                stage_waits
            )
            /
            len(
                stage_waits
            )

            if stage_waits

            else 0.0

        )

        maximum_wait = (

            max(
                stage_waits
            )

            if stage_waits

            else 0.0

        )

        stage_end = (

            max(
                counter_available
            )

            if counter_available

            else 0.0

        )

        observed_window = max(

            session_minutes,

            stage_end,

            1.0

        )

        utilization = (

            total_busy_time

            /
            (
                counter_count
                *
                observed_window
            )

            * 100.0

        )

        utilization = max(

            0.0,

            min(
                utilization,
                100.0
            )

        )

        stage_results.append(

            {
                "name":
                    stage[
                        "name"
                    ],

                "counters":
                    counter_count,

                "service_time":
                    round(
                        base_service_time,
                        2
                    ),

                "average_wait":
                    round(
                        average_wait,
                        2
                    ),

                "maximum_wait":
                    round(
                        maximum_wait,
                        2
                    ),

                "max_queue":
                    int(
                        max_queue
                    ),

                "utilization":
                    round(
                        utilization,
                        1
                    )
            }

        )

    total_waits = [

        visitor[
            "total_wait"
        ]

        for visitor in visitors

    ]

    overall_average_wait = (

        sum(
            total_waits
        )
        /
        len(
            total_waits
        )

        if total_waits

        else 0.0

    )

    overall_maximum_wait = (

        max(
            total_waits
        )

        if total_waits

        else 0.0

    )

    bottleneck = max(

        stage_results,

        key=lambda item:
            item[
                "average_wait"
            ]

    )[
        "name"
    ]

    group_results = []

    for group in GROUP_ORDER:

        group_waits = [

            visitor[
                "total_wait"
            ]

            for visitor in visitors

            if visitor[
                "group"
            ] == group

        ]

        group_results.append(

            {
                "group":
                    group,

                "visitors":
                    len(
                        group_waits
                    ),

                "average_wait":
                    round(

                        (
                            sum(
                                group_waits
                            )
                            /
                            len(
                                group_waits
                            )

                            if group_waits

                            else 0.0
                        ),

                        2

                    )
            }

        )

    general_waits = [

        visitor[
            "total_wait"
        ]

        for visitor in visitors

        if visitor[
            "group"
        ] == "general"

    ]

    priority_waits = [

        visitor[
            "total_wait"
        ]

        for visitor in visitors

        if visitor[
            "group"
        ] != "general"

    ]

    general_average = (

        sum(
            general_waits
        )
        /
        len(
            general_waits
        )

        if general_waits

        else 0.0

    )

    priority_average = (

        sum(
            priority_waits
        )
        /
        len(
            priority_waits
        )

        if priority_waits

        else 0.0

    )

    fairness_gap = (

        priority_average
        -
        general_average

        if (
            general_waits
            and
            priority_waits
        )

        else 0.0

    )

    return {

        "summary": {

            "visitors":
                visitor_count,

            "average_wait":
                round(
                    overall_average_wait,
                    2
                ),

            "maximum_wait":
                round(
                    overall_maximum_wait,
                    2
                ),

            "bottleneck":
                bottleneck,

            "fairness_gap":
                round(
                    fairness_gap,
                    2
                )

        },

        "stages":
            stage_results,

        "groups":
            group_results

    }


if __name__ == "__main__":

    demo = run_simulation(

        visitor_count=160,

        session_hours=6,

        stages=[

            {
                "name":
                    "Reception",

                "counters":
                    2,

                "service_time":
                    2
            },

            {
                "name":
                    "Triage",

                "counters":
                    1,

                "service_time":
                    3
            },

            {
                "name":
                    "Consultation",

                "counters":
                    3,

                "service_time":
                    4
            }

        ],

        group_mix={

            "general":
                60,

            "elderly":
                15,

            "pregnant":
                15,

            "mobility":
                10

        }

    )

    print(
        demo
    )