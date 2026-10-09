from datetime import datetime

from html import escape

from io import BytesIO


from reportlab.lib import colors

from reportlab.lib.enums import (
    TA_LEFT,
    TA_RIGHT
)

from reportlab.lib.pagesizes import (
    A4
)

from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)

from reportlab.lib.units import cm

from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)


COPYRIGHT_TEXT = (

    "© 2026 Devyansh Nath Mathur. "
    "FairFlow AI. All rights reserved."

)


PAGE_WIDTH, PAGE_HEIGHT = A4


INK = colors.HexColor(
    "#183037"
)

TEXT = colors.HexColor(
    "#53646A"
)

MUTED = colors.HexColor(
    "#7C898C"
)

TEAL = colors.HexColor(
    "#087E78"
)

TEAL_SOFT = colors.HexColor(
    "#E9F5F2"
)

CORAL = colors.HexColor(
    "#D76B4F"
)

CORAL_SOFT = colors.HexColor(
    "#FFF0EB"
)

LINE = colors.HexColor(
    "#DDE3DF"
)

PAPER_SOFT = colors.HexColor(
    "#FBFAF6"
)



def _fmt(
    value,
    decimals=2
):

    try:

        number = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return str(
            value
        )

    if number.is_integer():

        return str(
            int(
                number
            )
        )

    return (

        f"{number:.{decimals}f}"
        .rstrip(
            "0"
        )
        .rstrip(
            "."
        )

    )



def _safe(
    value
):

    return escape(
        str(
            value
        )
    )



def _footer(
    canvas,
    doc
):

    canvas.saveState()

    canvas.setStrokeColor(
        LINE
    )

    canvas.setLineWidth(
        0.5
    )

    canvas.line(

        1.6 * cm,

        1.0 * cm,

        PAGE_WIDTH
        -
        1.6 * cm,

        1.0 * cm

    )

    canvas.setFont(
        "Helvetica",
        7.2
    )

    canvas.setFillColor(
        MUTED
    )

    canvas.drawString(

        1.6 * cm,

        0.68 * cm,

        COPYRIGHT_TEXT

    )

    canvas.setFillColor(
        INK
    )

    canvas.drawRightString(

        PAGE_WIDTH
        -
        1.6 * cm,

        0.68 * cm,

        f"Page {doc.page}"

    )

    canvas.restoreState()



def _metric_table(
    items,
    styles
):

    cells = []

    for (
        label,
        value,
        suffix
    ) in items:

        value_text = (
            _safe(
                value
            )
        )

        suffix_text = (

            (
                " <font size='7' color='#7C898C'>"
                f"{_safe(suffix)}"
                "</font>"
            )

            if suffix

            else ""

        )

        cells.append(

            [

                Paragraph(

                    _safe(
                        label
                    )
                    .upper(),

                    styles[
                        "metric_label"
                    ]

                ),

                Paragraph(

                    value_text
                    +
                    suffix_text,

                    styles[
                        "metric_value"
                    ]

                )

            ]

        )

    table = Table(

        [
            cells
        ],

        colWidths=[

            (
                PAGE_WIDTH
                -
                3.2 * cm
            )
            /
            len(
                cells
            )

        ]
        *
        len(
            cells
        )

    )

    table.setStyle(

        TableStyle(

            [

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    LINE
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    LINE
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                )

            ]

        )

    )

    return table



def _styled_table(
    data,
    col_widths,
    header_background=
        PAPER_SOFT
):

    table = Table(

        data,

        colWidths=
            col_widths,

        repeatRows=1,

        hAlign=
            "LEFT"

    )

    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    header_background
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    MUTED
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    7.5
                ),

                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    0.7,
                    LINE
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    8.4
                ),

                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, -1),
                    TEXT
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "LINEBELOW",
                    (0, 1),
                    (-1, -2),
                    0.45,
                    LINE
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )

            ]

        )

    )

    return table



def build_analysis_report(
    analysis_input,
    ai_result
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        pagesize=
            A4,

        rightMargin=
            1.6 * cm,

        leftMargin=
            1.6 * cm,

        topMargin=
            1.35 * cm,

        bottomMargin=
            1.35 * cm,

        title=
            "FairFlow AI - Service Flow Analysis Report",

        author=
            "Devyansh Nath Mathur",

        subject=
            "FairFlow AI service-flow decision-support analysis"

    )

    base_styles = (
        getSampleStyleSheet()
    )

    styles = {

        "eyebrow":
            ParagraphStyle(

                "eyebrow",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    7.5,

                leading=
                    10,

                textColor=
                    TEAL,

                spaceAfter=
                    5

            ),

        "title":
            ParagraphStyle(

                "title",

                parent=
                    base_styles[
                        "Title"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    22,

                leading=
                    26,

                textColor=
                    INK,

                alignment=
                    TA_LEFT,

                spaceAfter=
                    7

            ),

        "subtitle":
            ParagraphStyle(

                "subtitle",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica",

                fontSize=
                    9,

                leading=
                    14,

                textColor=
                    TEXT,

                spaceAfter=
                    12

            ),

        "section":
            ParagraphStyle(

                "section",

                parent=
                    base_styles[
                        "Heading2"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    13,

                leading=
                    16,

                textColor=
                    INK,

                spaceBefore=
                    8,

                spaceAfter=
                    8

            ),

        "body":
            ParagraphStyle(

                "body",

                parent=
                    base_styles[
                        "BodyText"
                    ],

                fontName=
                    "Helvetica",

                fontSize=
                    8.5,

                leading=
                    13,

                textColor=
                    TEXT,

                spaceAfter=
                    6

            ),

        "body_bold":
            ParagraphStyle(

                "body_bold",

                parent=
                    base_styles[
                        "BodyText"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    9,

                leading=
                    13,

                textColor=
                    INK,

                spaceAfter=
                    5

            ),

        "metric_label":
            ParagraphStyle(

                "metric_label",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    6.7,

                leading=
                    8,

                textColor=
                    MUTED,

                spaceAfter=
                    5

            ),

        "metric_value":
            ParagraphStyle(

                "metric_value",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    14,

                leading=
                    17,

                textColor=
                    INK

            ),

        "table_cell":
            ParagraphStyle(

                "table_cell",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica",

                fontSize=
                    8.4,

                leading=
                    11,

                textColor=
                    TEXT

            ),

        "table_cell_bold":
            ParagraphStyle(

                "table_cell_bold",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica-Bold",

                fontSize=
                    8.4,

                leading=
                    11,

                textColor=
                    INK

            ),

        "note":
            ParagraphStyle(

                "note",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica",

                fontSize=
                    7.7,

                leading=
                    11.5,

                textColor=
                    TEXT,

                leftIndent=
                    8,

                rightIndent=
                    8

            ),

        "right":
            ParagraphStyle(

                "right",

                parent=
                    base_styles[
                        "Normal"
                    ],

                fontName=
                    "Helvetica",

                fontSize=
                    7.5,

                leading=
                    10,

                textColor=
                    MUTED,

                alignment=
                    TA_RIGHT

            )

    }

    story = []

    generated = (
        datetime.now()
        .strftime(
            "%d %B %Y, %I:%M %p"
        )
    )

    story.extend(

        [

            Paragraph(
                "FAIRFLOW AI",
                styles[
                    "eyebrow"
                ]
            ),

            Paragraph(
                "Service Flow Analysis Report",
                styles[
                    "title"
                ]
            ),

            Paragraph(

                "A decision-support analysis combining "
                "service-flow simulation, machine-learning "
                "screening and fairness-aware staffing "
                "recommendation.",

                styles[
                    "subtitle"
                ]

            ),

            Paragraph(

                "Report generated: "
                f"{_safe(generated)}",

                styles[
                    "right"
                ]

            ),

            Spacer(
                1,
                9
            )

        ]

    )

    baseline = (
        ai_result[
            "baseline"
        ]
    )

    recommended = (
        ai_result[
            "recommended"
        ]
    )

    story.append(

        Paragraph(
            "1. Executive summary",
            styles[
                "section"
            ]
        )

    )

    story.append(

        _metric_table(

            [

                (
                    "Visitors",
                    baseline[
                        "summary"
                    ][
                        "visitors"
                    ],
                    ""
                ),

                (
                    "Current avg. wait",
                    baseline[
                        "summary"
                    ][
                        "average_wait"
                    ],
                    "min"
                ),

                (
                    "Recommended avg. wait",
                    recommended[
                        "summary"
                    ][
                        "average_wait"
                    ],
                    "min"
                ),

                (
                    "Estimated reduction",
                    ai_result[
                        "wait_improvement_percent"
                    ],
                    "%"
                )

            ],

            styles

        )

    )

    story.extend(

        [

            Spacer(
                1,
                9
            ),

            Paragraph(

                _safe(
                    ai_result[
                        "headline"
                    ]
                ),

                styles[
                    "body_bold"
                ]

            ),

            Paragraph(

                _safe(
                    ai_result[
                        "explanation"
                    ]
                ),

                styles[
                    "body"
                ]

            ),

            Paragraph(

                _safe(
                    ai_result[
                        "fairness_insight"
                    ]
                ),

                styles[
                    "body"
                ]

            ),

            Spacer(
                1,
                5
            )

        ]

    )

    story.append(

        Paragraph(

            "2. Submitted service setup",

            styles[
                "section"
            ]

        )

    )

    stage_data = [

        [
            "STAGE",
            "COUNTERS",
            "AVG. SERVICE TIME"
        ]

    ]

    for stage in analysis_input[
        "stages"
    ]:

        stage_data.append(

            [

                Paragraph(

                    _safe(
                        stage[
                            "name"
                        ]
                    ),

                    styles[
                        "table_cell_bold"
                    ]

                ),

                _fmt(
                    stage[
                        "counters"
                    ]
                ),

                (
                    f"{_fmt(stage['service_time'])} min"
                )

            ]

        )

    story.append(

        _styled_table(

            stage_data,

            [
                8.5 * cm,
                3.0 * cm,
                4.5 * cm
            ]

        )

    )

    story.extend(

        [

            Spacer(
                1,
                8
            ),

            _metric_table(

                [

                    (
                        "Expected visitors",
                        analysis_input[
                            "visitor_count"
                        ],
                        ""
                    ),

                    (
                        "Session duration",
                        analysis_input[
                            "session_hours"
                        ],
                        "hours"
                    ),

                    (
                        "Configured stages",
                        len(
                            analysis_input[
                                "stages"
                            ]
                        ),
                        ""
                    )

                ],

                styles

            ),

            Spacer(
                1,
                8
            )

        ]

    )

    mix = (
        analysis_input[
            "group_mix"
        ]
    )

    mix_data = [

        [
            "VISITOR GROUP",
            "SHARE"
        ]

    ]

    mix_labels = [

        (
            "General",
            mix[
                "general"
            ]
        ),

        (
            "Elderly",
            mix[
                "elderly"
            ]
        ),

        (
            "Pregnant",
            mix[
                "pregnant"
            ]
        ),

        (
            "Mobility-limited",
            mix[
                "mobility"
            ]
        )

    ]

    for (
        label,
        value
    ) in mix_labels:

        mix_data.append(

            [

                label,

                f"{_fmt(value)}%"

            ]

        )

    story.append(

        KeepTogether(

            [

                Paragraph(

                    "3. Visitor mix",

                    styles[
                        "section"
                    ]

                ),

                _styled_table(

                    mix_data,

                    [
                        11.5 * cm,
                        4.5 * cm
                    ]

                )

            ]

        )

    )

    story.append(
        Spacer(
            1,
            7
        )
    )

    performance_data = [

        [

            "STAGE",

            "COUNTERS",

            "AVG. WAIT",

            "MAX WAIT",

            "MAX QUEUE",

            "UTILIZATION"

        ]

    ]

    for stage in baseline[
        "stages"
    ]:

        performance_data.append(

            [

                Paragraph(

                    _safe(
                        stage[
                            "name"
                        ]
                    ),

                    styles[
                        "table_cell_bold"
                    ]

                ),

                str(
                    stage[
                        "counters"
                    ]
                ),

                (
                    f"{_fmt(stage['average_wait'])} min"
                ),

                (
                    f"{_fmt(stage['maximum_wait'])} min"
                ),

                str(
                    stage[
                        "max_queue"
                    ]
                ),

                (
                    f"{_fmt(stage['utilization'], 1)}%"
                )

            ]

        )

    performance_table = (
        _styled_table(

            performance_data,

            [

                4.2 * cm,

                2.0 * cm,

                2.5 * cm,

                2.5 * cm,

                2.1 * cm,

                2.7 * cm

            ]

        )
    )

    story.append(

        KeepTogether(

            [

                Paragraph(

                    "4. Current service performance",

                    styles[
                        "section"
                    ]

                ),

                Paragraph(

                    "The current simulation identifies "
                    f"<b>{_safe(baseline['summary']['bottleneck'])}</b> "
                    "as the primary bottleneck.",

                    styles[
                        "body"
                    ]

                ),

                performance_table

            ]

        )

    )

    story.append(
        Spacer(
            1,
            8
        )
    )

    story.append(

        Paragraph(

            "5. Visitor-group experience",

            styles[
                "section"
            ]

        )

    )

    group_data = [

        [

            "VISITOR GROUP",

            "VISITORS",

            "AVG. WAIT"

        ]

    ]

    display_names = {

        "general":
            "General",

        "elderly":
            "Elderly",

        "pregnant":
            "Pregnant",

        "mobility":
            "Mobility-limited"

    }

    for group in baseline[
        "groups"
    ]:

        group_data.append(

            [

                display_names.get(

                    group[
                        "group"
                    ],

                    group[
                        "group"
                    ]

                ),

                str(
                    group[
                        "visitors"
                    ]
                ),

                (
                    f"{_fmt(group['average_wait'])} min"
                )

            ]

        )

    story.append(

        _styled_table(

            group_data,

            [

                8.0 * cm,

                3.0 * cm,

                5.0 * cm

            ]

        )

    )

    story.extend(

        [

            Spacer(
                1,
                8
            ),

            _metric_table(

                [

                    (
                        "Current fairness gap",
                        ai_result[
                            "baseline_fairness_gap"
                        ],
                        "min"
                    ),

                    (
                        "Recommended fairness gap",
                        ai_result[
                            "recommended_fairness_gap"
                        ],
                        "min"
                    )

                ],

                styles

            ),

            Spacer(
                1,
                8
            )

        ]

    )

    story.append(

        Paragraph(

            "6. Machine-learning analysis",

            styles[
                "section"
            ]

        )

    )

    metrics = (
        ai_result[
            "model_metrics"
        ]
    )

    story.append(

        _metric_table(

            [

                (
                    "Configurations screened",
                    ai_result[
                        "configurations_screened_by_ml"
                    ],
                    ""
                ),

                (
                    "Configurations verified",
                    ai_result[
                        "configurations_verified_by_simulation"
                    ],
                    ""
                ),

                (
                    "Test-set R²",
                    metrics[
                        "wait_r2"
                    ],
                    ""
                ),

                (
                    "Median abs. error",
                    metrics[
                        "wait_median_ae"
                    ],
                    "min"
                )

            ],

            styles

        )

    )

    story.extend(

        [

            Spacer(
                1,
                8
            ),

            _metric_table(

                [

                    (
                        "Current setup ML forecast",
                        ai_result[
                            "baseline_ml_predicted_wait"
                        ],
                        "min"
                    ),

                    (
                        "Recommended setup ML forecast",
                        ai_result[
                            "recommended_ml_predicted_wait"
                        ],
                        "min"
                    )

                ],

                styles

            ),

            Spacer(
                1,
                6
            ),

            Paragraph(

                "Model performance is measured on held-out "
                "scenarios generated by FairFlow's simulation "
                "engine. These metrics should not be interpreted "
                "as real-world operational validation.",

                styles[
                    "note"
                ]

            ),

            Spacer(
                1,
                7
            )

        ]

    )

    story.append(

        KeepTogether(

            [

                Paragraph(

                    "7. Recommended action",

                    styles[
                        "section"
                    ]

                ),

                Table(

                    [

                        [

                            Paragraph(

                                _safe(
                                    ai_result[
                                        "headline"
                                    ]
                                ),

                                styles[
                                    "body_bold"
                                ]

                            )

                        ],

                        [

                            Paragraph(

                                _safe(
                                    ai_result[
                                        "explanation"
                                    ]
                                ),

                                styles[
                                    "body"
                                ]

                            )

                        ],

                        [

                            Paragraph(

                                _safe(
                                    ai_result[
                                        "fairness_insight"
                                    ]
                                ),

                                styles[
                                    "body"
                                ]

                            )

                        ]

                    ],

                    colWidths=[
                        16.0 * cm
                    ],

                    style=
                        TableStyle(

                            [

                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, -1),
                                    TEAL_SOFT
                                ),

                                (
                                    "BOX",
                                    (0, 0),
                                    (-1, -1),
                                    0.7,
                                    colors.HexColor(
                                        "#C8DCD8"
                                    )
                                ),

                                (
                                    "LEFTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    12
                                ),

                                (
                                    "RIGHTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    12
                                ),

                                (
                                    "TOPPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    8
                                ),

                                (
                                    "BOTTOMPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    8
                                )

                            ]

                        )

                )

            ]

        )

    )

    story.append(
        Spacer(
            1,
            8
        )
    )

    staffing_data = [

        [

            "STAGE",

            "CURRENT",

            "RECOMMENDED",

            "CHANGE"

        ]

    ]

    for change in ai_result[
        "stage_changes"
    ]:

        difference = int(
            change[
                "difference"
            ]
        )

        if difference > 0:

            change_text = (
                f"+{difference}"
            )

        elif difference < 0:

            change_text = str(
                difference
            )

        else:

            change_text = (
                "No change"
            )

        staffing_data.append(

            [

                Paragraph(

                    _safe(
                        change[
                            "name"
                        ]
                    ),

                    styles[
                        "table_cell_bold"
                    ]

                ),

                str(
                    change[
                        "before"
                    ]
                ),

                str(
                    change[
                        "after"
                    ]
                ),

                change_text

            ]

        )

    staffing_table = (
        _styled_table(

            staffing_data,

            [

                7.0 * cm,

                2.8 * cm,

                3.3 * cm,

                2.9 * cm

            ]

        )
    )

    story.append(

        KeepTogether(

            [

                Paragraph(

                    "8. Recommended staffing",

                    styles[
                        "section"
                    ]

                ),

                staffing_table

            ]

        )

    )

    story.extend(

        [

            Spacer(
                1,
                8
            ),

            _metric_table(

                [

                    (
                        "Current avg. wait",
                        baseline[
                            "summary"
                        ][
                            "average_wait"
                        ],
                        "min"
                    ),

                    (
                        "Recommended avg. wait",
                        recommended[
                            "summary"
                        ][
                            "average_wait"
                        ],
                        "min"
                    ),

                    (
                        "Wait reduction",
                        ai_result[
                            "wait_improvement_percent"
                        ],
                        "%"
                    )

                ],

                styles

            ),

            Spacer(
                1,
                8
            )

        ]

    )

    methodology_rows = [

        (

            "1",

            "Simulate current service flow",

            "Virtual visitors move through the configured "
            "service stages to estimate waiting times, "
            "queues and utilization."

        ),

        (

            "2",

            "Generate alternative allocations",

            "Feasible staffing configurations are generated "
            "while keeping the total number of counters "
            "unchanged."

        ),

        (

            "3",

            "Rank using machine learning",

            "The trained wait-time model rapidly estimates "
            "congestion and ranks candidate staffing "
            "configurations."

        ),

        (

            "4",

            "Verify shortlisted configurations",

            "Leading ML-ranked configurations are tested "
            "again using detailed service-flow simulation."

        ),

        (

            "5",

            "Select the final recommendation",

            "Waiting time, bottleneck severity, utilization "
            "and fairness are evaluated together before the "
            "final staffing recommendation is selected."

        )

    ]

    methodology_data = [

        [
            "STEP",
            "METHOD"
        ]

    ]

    for (
        number,
        title,
        description
    ) in methodology_rows:

        methodology_data.append(

            [

                number,

                Paragraph(

                    "<b>"
                    f"{_safe(title)}"
                    "</b><br/>"
                    f"{_safe(description)}",

                    styles[
                        "table_cell"
                    ]

                )

            ]

        )

    story.append(

        Paragraph(

            "9. Methodology",

            styles[
                "section"
            ]

        )

    )

    story.append(

        _styled_table(

            methodology_data,

            [

                1.5 * cm,

                14.5 * cm

            ]

        )

    )

    story.extend(

        [

            Spacer(
                1,
                10
            ),

            KeepTogether(

                [

                    Paragraph(

                        "Important note",

                        styles[
                            "body_bold"
                        ]

                    ),

                    Table(

                        [

                            [

                                Paragraph(

                                    "FairFlow provides analytical decision "
                                    "support using estimates derived from "
                                    "user-supplied service assumptions, "
                                    "simulated visitor journeys and a "
                                    "machine-learning model trained on "
                                    "simulator-generated scenarios. The "
                                    "report should not be interpreted as "
                                    "real-world operational, clinical or "
                                    "safety validation.",

                                    styles[
                                        "note"
                                    ]

                                )

                            ]

                        ],

                        colWidths=[
                            16.0 * cm
                        ],

                        style=
                            TableStyle(

                                [

                                    (
                                        "BACKGROUND",
                                        (0, 0),
                                        (-1, -1),
                                        CORAL_SOFT
                                    ),

                                    (
                                        "BOX",
                                        (0, 0),
                                        (-1, -1),
                                        0.7,
                                        colors.HexColor(
                                            "#EFD8CF"
                                        )
                                    ),

                                    (
                                        "LEFTPADDING",
                                        (0, 0),
                                        (-1, -1),
                                        10
                                    ),

                                    (
                                        "RIGHTPADDING",
                                        (0, 0),
                                        (-1, -1),
                                        10
                                    ),

                                    (
                                        "TOPPADDING",
                                        (0, 0),
                                        (-1, -1),
                                        9
                                    ),

                                    (
                                        "BOTTOMPADDING",
                                        (0, 0),
                                        (-1, -1),
                                        9
                                    )

                                ]

                            )

                    )

                ]

            )

        ]

    )

    doc.build(

        story,

        onFirstPage=
            _footer,

        onLaterPages=
            _footer

    )

    buffer.seek(
        0
    )

    return buffer