import math


from flask import (
    Flask,
    render_template,
    request,
    send_file
)


from engine.ai_engine import (
    generate_ai_recommendation
)

from engine.report_generator import (
    build_analysis_report
)


app = Flask(
    __name__
)


COPYRIGHT_TEXT = (

    "© 2026 Devyansh Nath Mathur. "
    "FairFlow AI. All rights reserved."

)


MIN_STAGES = 2

MAX_STAGES = 6

MAX_COUNTERS_PER_STAGE = 20



# =========================================================
# DEFAULT FORM
# =========================================================

def default_form_data():

    return {

        "visitor_count":
            "",

        "session_hours":
            "",

        "general":
            "",

        "elderly":
            "",

        "pregnant":
            "",

        "mobility":
            "",

        "stages": [

            {

                "name":
                    "Registration",

                "counters":
                    "",

                "service_time":
                    ""

            },

            {

                "name":
                    "Verification",

                "counters":
                    "",

                "service_time":
                    ""

            },

            {

                "name":
                    "Service",

                "counters":
                    "",

                "service_time":
                    ""

            }

        ]

    }



# =========================================================
# PRESERVE FORM DATA
# =========================================================

def form_to_template_data(
    form
):

    names = (
        form.getlist(
            "stage_name"
        )
    )

    counters = (
        form.getlist(
            "stage_counters"
        )
    )

    service_times = (
        form.getlist(
            "stage_time"
        )
    )

    row_count = max(

        len(
            names
        ),

        len(
            counters
        ),

        len(
            service_times
        )

    )

    stages = []

    for index in range(
        row_count
    ):

        stages.append(

            {

                "name":
                    (
                        names[
                            index
                        ]

                        if index
                        <
                        len(
                            names
                        )

                        else ""
                    ),

                "counters":
                    (
                        counters[
                            index
                        ]

                        if index
                        <
                        len(
                            counters
                        )

                        else ""
                    ),

                "service_time":
                    (
                        service_times[
                            index
                        ]

                        if index
                        <
                        len(
                            service_times
                        )

                        else ""
                    )

            }

        )

    return {

        "visitor_count":
            form.get(
                "visitor_count",
                ""
            ),

        "session_hours":
            form.get(
                "session_hours",
                ""
            ),

        "general":
            form.get(
                "general",
                ""
            ),

        "elderly":
            form.get(
                "elderly",
                ""
            ),

        "pregnant":
            form.get(
                "pregnant",
                ""
            ),

        "mobility":
            form.get(
                "mobility",
                ""
            ),

        "stages":
            stages

    }



# =========================================================
# GLOBAL HTML ENHANCEMENTS
# =========================================================

@app.after_request
def enhance_html_pages(
    response
):

    content_type = (
        response.headers.get(
            "Content-Type",
            ""
        )
    )

    if (
        "text/html"
        not in content_type
    ):

        return response

    try:

        html = (
            response.get_data(
                as_text=True
            )
        )

    except Exception:

        return response


    # -----------------------------------------------------
    # COPYRIGHT
    # -----------------------------------------------------

    if (
        "fairflow-copyright-footer"
        not in html
    ):

        footer_markup = f"""

        <style>

            #fairflow-copyright-footer {{

                width: 100%;

                padding: 18px 24px;

                border-top:
                    1px solid #dedfd9;

                background:
                    #ffffff;

                color:
                    #697477;

                text-align:
                    center;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;

                font-size:
                    11px;

                line-height:
                    1.5;

            }}

        </style>


        <div
            id="fairflow-copyright-footer"
        >
            {COPYRIGHT_TEXT}
        </div>

        """

        if (
            "</body>"
            in html
        ):

            html = html.replace(

                "</body>",

                footer_markup
                +
                "\n</body>",

                1

            )


    # -----------------------------------------------------
    # ANALYSIS LOADER
    # -----------------------------------------------------

    if (

        request.path
        ==
        "/simulate"

        and

        "fairflow-analysis-loader"
        not in html

    ):

        loader_markup = """

        <style>

            #fairflow-analysis-loader {

                position: fixed;

                inset: 0;

                z-index: 99999;

                display: none;

                align-items: center;

                justify-content: center;

                padding: 24px;

                background:
                    rgba(
                        247,
                        245,
                        239,
                        0.94
                    );

                backdrop-filter:
                    blur(4px);

            }


            #fairflow-analysis-loader.visible {

                display: flex;

            }


            .fairflow-analysis-loader-card {

                width:
                    min(
                        460px,
                        100%
                    );

                padding:
                    38px;

                border:
                    1px solid #d9ddd7;

                background:
                    #ffffff;

                box-shadow:
                    0 20px 55px
                    rgba(
                        24,
                        48,
                        55,
                        0.10
                    );

            }


            .fairflow-analysis-loader-brand {

                margin-bottom:
                    18px;

                color:
                    #087e78;

                font-family:
                    Georgia,
                    "Times New Roman",
                    serif;

                font-size:
                    15px;

                font-weight:
                    700;

            }


            .fairflow-analysis-loader-card h2 {

                margin:
                    0 0 12px;

                color:
                    #183037;

                font-family:
                    Georgia,
                    "Times New Roman",
                    serif;

                font-size:
                    28px;

                line-height:
                    1.15;

                font-weight:
                    500;

            }


            .fairflow-analysis-loader-card p {

                margin: 0;

                color:
                    #687579;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;

                font-size:
                    13px;

                line-height:
                    1.65;

            }


            .fairflow-analysis-loader-status {

                display: flex;

                align-items: center;

                gap: 11px;

                margin-top:
                    25px;

                color:
                    #183037;

                font-family:
                    "Segoe UI",
                    Arial,
                    sans-serif;

                font-size:
                    11px;

                font-weight:
                    600;

            }


            .fairflow-analysis-spinner {

                width:
                    18px;

                height:
                    18px;

                border:
                    2px solid #d9e2df;

                border-top-color:
                    #087e78;

                border-radius:
                    50%;

                animation:
                    fairflowSpin
                    0.8s
                    linear
                    infinite;

            }


            .fairflow-analysis-progress {

                width:
                    100%;

                height:
                    3px;

                margin-top:
                    21px;

                overflow:
                    hidden;

                background:
                    #e8ece8;

            }


            .fairflow-analysis-progress span {

                display: block;

                width:
                    42%;

                height:
                    100%;

                background:
                    #087e78;

                animation:
                    fairflowProgress
                    1.35s
                    ease-in-out
                    infinite;

            }


            @keyframes fairflowSpin {

                to {

                    transform:
                        rotate(
                            360deg
                        );

                }

            }


            @keyframes fairflowProgress {

                0% {

                    transform:
                        translateX(
                            -110%
                        );

                }

                55% {

                    transform:
                        translateX(
                            90%
                        );

                }

                100% {

                    transform:
                        translateX(
                            250%
                        );

                }

            }

        </style>


        <div
            id="fairflow-analysis-loader"
            aria-hidden="true"
        >

            <div
                class="fairflow-analysis-loader-card"
            >

                <div
                    class="fairflow-analysis-loader-brand"
                >
                    FairFlow AI
                </div>


                <h2>
                    Analyzing service flow
                </h2>


                <p>

                    Simulating visitor flow,
                    screening staffing configurations
                    and verifying the recommendation.

                </p>


                <div
                    class="fairflow-analysis-loader-status"
                >

                    <span
                        class="fairflow-analysis-spinner"
                        aria-hidden="true"
                    >
                    </span>

                    <span>
                        Processing configuration
                    </span>

                </div>


                <div
                    class="fairflow-analysis-progress"
                    aria-hidden="true"
                >

                    <span>
                    </span>

                </div>


            </div>

        </div>


        <script>

            (() => {


                const analysisForm =
                    document.getElementById(
                        "serviceSetupForm"
                    );


                const loadingOverlay =
                    document.getElementById(
                        "fairflow-analysis-loader"
                    );


                if (
                    !analysisForm
                    ||
                    !loadingOverlay
                ) {

                    return;

                }


                const submitButton =
                    analysisForm.querySelector(
                        'button[type="submit"]'
                    );


                const originalButtonText =
                    submitButton
                        ? submitButton.textContent
                        : "";


                analysisForm.addEventListener(
                    "submit",
                    event => {


                        if (
                            event.defaultPrevented
                        ) {

                            return;

                        }


                        event.preventDefault();


                        loadingOverlay
                            .classList
                            .add(
                                "visible"
                            );


                        loadingOverlay
                            .setAttribute(
                                "aria-hidden",
                                "false"
                            );


                        if (
                            submitButton
                        ) {

                            submitButton.disabled =
                                true;


                            submitButton.textContent =
                                "Analyzing service flow...";

                        }


                        requestAnimationFrame(
                            () => {


                                setTimeout(
                                    () => {


                                        HTMLFormElement
                                            .prototype
                                            .submit
                                            .call(
                                                analysisForm
                                            );


                                    },
                                    90
                                );


                            }
                        );


                    }
                );


                window.addEventListener(
                    "pageshow",
                    () => {


                        loadingOverlay
                            .classList
                            .remove(
                                "visible"
                            );


                        loadingOverlay
                            .setAttribute(
                                "aria-hidden",
                                "true"
                            );


                        if (
                            submitButton
                        ) {

                            submitButton.disabled =
                                false;


                            submitButton.textContent =
                                originalButtonText;

                        }


                    }
                );


            })();

        </script>

        """

        if (
            "</body>"
            in html
        ):

            html = html.replace(

                "</body>",

                loader_markup
                +
                "\n</body>",

                1

            )

    response.set_data(
        html
    )

    return response



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )



# =========================================================
# VALIDATION HELPERS
# =========================================================

def parse_integer_value(
    raw_value,
    label,
    minimum=1,
    maximum=None
):

    value = str(
        raw_value
    ).strip()

    if value == "":

        return (
            None,
            f"{label} is required."
        )

    try:

        number_float = float(
            value
        )

    except ValueError:

        return (

            None,

            f"{label} must be a whole number."

        )

    if not (
        math.isfinite(
            number_float
        )
    ):

        return (

            None,

            f"{label} must be a finite whole number."

        )

    if not (
        number_float.is_integer()
    ):

        return (

            None,

            f"{label} must be a whole number."

        )

    number = int(
        number_float
    )

    if number < minimum:

        return (

            None,

            f"{label} must be at least {minimum}."

        )

    if (

        maximum
        is not None

        and

        number
        >
        maximum

    ):

        return (

            None,

            f"{label} cannot be greater than {maximum}."

        )

    return (
        number,
        None
    )



def parse_number_value(
    raw_value,
    label,
    minimum=0.0,
    maximum=None
):

    value = str(
        raw_value
    ).strip()

    if value == "":

        return (
            None,
            f"{label} is required."
        )

    try:

        number = float(
            value
        )

    except ValueError:

        return (

            None,

            f"{label} must be a valid number."

        )

    if not (
        math.isfinite(
            number
        )
    ):

        return (

            None,

            f"{label} must be a finite number."

        )

    if number < minimum:

        return (

            None,

            f"{label} must be at least {minimum}."

        )

    if (

        maximum
        is not None

        and

        number
        >
        maximum

    ):

        return (

            None,

            f"{label} cannot be greater than {maximum}."

        )

    return (
        number,
        None
    )



def parse_service_time_value(
    raw_value,
    label
):

    value = str(
        raw_value
    ).strip()

    if value == "":

        return (
            None,
            f"{label} is required."
        )

    try:

        number = float(
            value
        )

    except ValueError:

        return (

            None,

            f"{label} must be a valid number."

        )

    if not (
        math.isfinite(
            number
        )
    ):

        return (

            None,

            f"{label} must be a finite number."

        )

    if number < 0:

        return (

            None,

            f"{label} cannot be negative."

        )

    if number == 0:

        return (

            None,

            f"{label} must be greater than 0 minutes."

        )

    return (
        number,
        None
    )



# =========================================================
# PARSE FORM
# =========================================================

def parse_analysis_form(
    form
):

    errors = []


    visitor_count, error = (
        parse_integer_value(

            form.get(
                "visitor_count",
                ""
            ),

            "Expected visitors",

            minimum=1,

            maximum=10000

        )
    )

    if error:

        errors.append(
            error
        )


    session_hours, error = (
        parse_number_value(

            form.get(
                "session_hours",
                ""
            ),

            "Session duration",

            minimum=0.1,

            maximum=24

        )
    )

    if error:

        errors.append(
            error
        )


    stage_names = (
        form.getlist(
            "stage_name"
        )
    )

    stage_counters = (
        form.getlist(
            "stage_counters"
        )
    )

    stage_times = (
        form.getlist(
            "stage_time"
        )
    )


    if not (

        len(
            stage_names
        )
        ==
        len(
            stage_counters
        )
        ==
        len(
            stage_times
        )

    ):

        errors.append(

            "The submitted service-stage data is "
            "incomplete. Please review the stage rows."

        )


    stage_count = min(

        len(
            stage_names
        ),

        len(
            stage_counters
        ),

        len(
            stage_times
        )

    )


    if (
        stage_count
        <
        MIN_STAGES
    ):

        errors.append(

            f"At least {MIN_STAGES} "
            "service stages are required."

        )


    if (
        stage_count
        >
        MAX_STAGES
    ):

        errors.append(

            f"A maximum of {MAX_STAGES} service stages "
            "can be analysed at one time."

        )


    stages = []

    seen_names = set()


    for index in range(
        stage_count
    ):

        position = (
            index
            +
            1
        )

        name = (
            stage_names[
                index
            ]
            .strip()
        )


        if not name:

            errors.append(

                f"Stage {position} name is required."

            )

        elif (
            len(
                name
            )
            >
            50
        ):

            errors.append(

                f"Stage {position} name cannot be "
                "longer than 50 characters."

            )

        else:

            normalized_name = (
                name.casefold()
            )

            if (
                normalized_name
                in seen_names
            ):

                errors.append(

                    f'Stage name "{name}" is duplicated. '
                    "Each stage must have a unique name."

                )

            else:

                seen_names.add(
                    normalized_name
                )


        display_label = (

            name

            if name

            else f"Stage {position}"

        )


        counters, counter_error = (
            parse_integer_value(

                stage_counters[
                    index
                ],

                f"{display_label} counters",

                minimum=1,

                maximum=
                    MAX_COUNTERS_PER_STAGE

            )
        )

        if counter_error:

            errors.append(
                counter_error
            )


        service_time, time_error = (
            parse_service_time_value(

                stage_times[
                    index
                ],

                f"{display_label} service time"

            )
        )

        if time_error:

            errors.append(
                time_error
            )


        stages.append(

            {

                "name":
                    name,

                "counters":
                    counters,

                "service_time":
                    service_time

            }

        )


    general, error = (
        parse_number_value(

            form.get(
                "general",
                ""
            ),

            "General visitor percentage",

            minimum=0,

            maximum=100

        )
    )

    if error:

        errors.append(
            error
        )


    elderly, error = (
        parse_number_value(

            form.get(
                "elderly",
                ""
            ),

            "Elderly visitor percentage",

            minimum=0,

            maximum=100

        )
    )

    if error:

        errors.append(
            error
        )


    pregnant, error = (
        parse_number_value(

            form.get(
                "pregnant",
                ""
            ),

            "Pregnant visitor percentage",

            minimum=0,

            maximum=100

        )
    )

    if error:

        errors.append(
            error
        )


    mobility, error = (
        parse_number_value(

            form.get(
                "mobility",
                ""
            ),

            "Mobility-limited visitor percentage",

            minimum=0,

            maximum=100

        )
    )

    if error:

        errors.append(
            error
        )


    group_values = [

        general,

        elderly,

        pregnant,

        mobility

    ]


    if all(

        value
        is not None

        for value
        in group_values

    ):

        group_total = sum(
            group_values
        )

        if (

            abs(
                group_total
                -
                100.0
            )
            >
            0.01

        ):

            errors.append(

                "Visitor percentages must total 100%. "
                f"Current total is {group_total:g}%."

            )


    if errors:

        return (
            None,
            errors
        )


    group_mix = {

        "general":
            general,

        "elderly":
            elderly,

        "pregnant":
            pregnant,

        "mobility":
            mobility

    }


    analysis_input = {

        "visitor_count":
            visitor_count,

        "session_hours":
            session_hours,

        "stages":
            stages,

        "group_mix":
            group_mix

    }


    return (
        analysis_input,
        []
    )



# =========================================================
# ANALYSIS
# =========================================================

def run_fairflow_analysis(
    analysis_input
):

    ai_result = (
        generate_ai_recommendation(

            visitor_count=
                analysis_input[
                    "visitor_count"
                ],

            session_hours=
                analysis_input[
                    "session_hours"
                ],

            stages=
                analysis_input[
                    "stages"
                ],

            group_mix=
                analysis_input[
                    "group_mix"
                ],

            verification_limit=5

        )
    )


    result = (
        ai_result[
            "baseline"
        ]
    )


    optimization = {

        "baseline":
            ai_result[
                "baseline"
            ],

        "optimized":
            ai_result[
                "recommended"
            ],

        "baseline_score":
            ai_result[
                "baseline_score"
            ],

        "optimized_score":
            ai_result[
                "recommended_score"
            ],

        "baseline_allocation":
            ai_result[
                "baseline_allocation"
            ],

        "optimized_allocation":
            ai_result[
                "recommended_allocation"
            ],

        "stage_changes":
            ai_result[
                "stage_changes"
            ],

        "configurations_evaluated":
            ai_result[
                "configurations_screened_by_ml"
            ],

        "wait_improvement_percent":
            ai_result[
                "wait_improvement_percent"
            ],

        "baseline_fairness_gap":
            ai_result[
                "baseline_fairness_gap"
            ],

        "optimized_fairness_gap":
            ai_result[
                "recommended_fairness_gap"
            ],

        "changed":
            ai_result[
                "changed"
            ]

    }


    return (

        result,

        ai_result,

        optimization

    )



# =========================================================
# SIMULATE
# =========================================================

@app.route(
    "/simulate",
    methods=[
        "GET",
        "POST"
    ]
)
def simulate():

    if (
        request.method
        ==
        "GET"
    ):

        return render_template(

            "simulate.html",

            errors=[],

            form_data=
                default_form_data(),

            min_stages=
                MIN_STAGES,

            max_stages=
                MAX_STAGES

        )


    form_data = (
        form_to_template_data(
            request.form
        )
    )


    analysis_input, errors = (
        parse_analysis_form(
            request.form
        )
    )


    if errors:

        return render_template(

            "simulate.html",

            errors=
                errors,

            form_data=
                form_data,

            min_stages=
                MIN_STAGES,

            max_stages=
                MAX_STAGES

        )


    (
        result,
        ai_result,
        optimization

    ) = run_fairflow_analysis(
        analysis_input
    )


    return render_template(

        "results.html",

        result=
            result,

        ai_result=
            ai_result,

        optimization=
            optimization,

        analysis_input=
            analysis_input

    )



# =========================================================
# PDF
# =========================================================

@app.route(
    "/download-report",
    methods=[
        "POST"
    ]
)
def download_report():

    analysis_input, errors = (
        parse_analysis_form(
            request.form
        )
    )


    if errors:

        return (

            "Unable to generate the report because "
            "the submitted analysis data is invalid.",

            400

        )


    (
        _,
        ai_result,
        _

    ) = run_fairflow_analysis(
        analysis_input
    )


    pdf_buffer = (
        build_analysis_report(

            analysis_input=
                analysis_input,

            ai_result=
                ai_result

        )
    )


    return send_file(

        pdf_buffer,

        mimetype=
            "application/pdf",

        as_attachment=
            True,

        download_name=
            "FairFlow_Analysis_Report.pdf"

    )



# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )