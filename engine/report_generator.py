from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# =========================================================
# COLORS
# =========================================================

INK = colors.HexColor("#183037")
TEXT = colors.HexColor("#53646A")
MUTED = colors.HexColor("#7C898C")

TEAL_SOFT = colors.HexColor("#E9F5F2")

MUSTARD = colors.HexColor("#B88A2D")
MUSTARD_SOFT = colors.HexColor("#FFFAF0")

LINE = colors.HexColor("#DDE3DF")
LIGHT_GREY = colors.HexColor("#FAFBF8")

WHITE = colors.white


# =========================================================
# DISCLAIMER
# =========================================================

DISCLAIMER_TEXT = (
    "FairFlow is a decision-support system. "
    "All waiting times, bottleneck estimates, fairness measures, "
    "machine-learning forecasts and staffing recommendations are "
    "generated from user-supplied assumptions, simulated visitor "
    "journeys and a model trained on simulator-generated scenarios. "
    "These outputs are illustrative estimates and should not be "
    "treated as real-world operational, clinical, safety or staffing "
    "validation. Any real-world decision should be independently "
    "reviewed and validated before implementation."
)


COPYRIGHT_TEXT = (
    "© 2026 Devyansh Nath Mathur. FairFlow AI. All rights reserved."
)


# =========================================================
# GENERIC HELPERS
# =========================================================

def _get(value, key, default=None):

    if value is None:
        return default

    if isinstance(value, dict):
        return value.get(key, default)

    return getattr(value, key, default)


def _as_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    try:
        return list(value)

    except TypeError:
        return []


def _num(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):
        return float(default)


def _fmt(value, digits=2):

    value = round(
        _num(value),
        digits
    )

    if float(value).is_integer():
        return str(
            int(value)
        )

    return (
        f"{value:.{digits}f}"
        .rstrip("0")
        .rstrip(".")
    )


def _safe(value):

    if value is None:
        value = ""

    return escape(
        str(value)
    )


def _looks_like_ai_result(value):

    return any(
        _get(
            value,
            key,
            None
        )
        is not None

        for key in (
            "headline",
            "baseline",
            "recommended",
            "stage_changes",
            "wait_improvement_percent",
            "configurations_screened_by_ml",
        )
    )


# =========================================================
# ARGUMENT NORMALIZER
# =========================================================

def _normalise_arguments(
    *args,
    **kwargs
):

    analysis_input = kwargs.get(
        "analysis_input"
    )

    ai_result = kwargs.get(
        "ai_result"
    )

    result = kwargs.get(
        "result"
    )


    if (
        analysis_input is None
        and
        len(args) >= 1
    ):
        analysis_input = args[0]


    if (
        len(args) == 2
        and
        ai_result is None
    ):
        ai_result = args[1]


    elif len(args) >= 3:

        second = args[1]
        third = args[2]

        if _looks_like_ai_result(second):

            ai_result = second

            if result is None:
                result = third

        else:

            if result is None:
                result = second

            if ai_result is None:
                ai_result = third


    if analysis_input is None:
        analysis_input = {}

    if ai_result is None:
        ai_result = {}


    return (
        analysis_input,
        ai_result,
        result
    )


# =========================================================
# STYLES
# =========================================================

def _styles():

    base = getSampleStyleSheet()


    return {

        "title":
            ParagraphStyle(
                "FairFlowTitle",
                parent=base["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=INK,
                alignment=TA_LEFT,
                spaceAfter=3 * mm,
            ),


        "subtitle":
            ParagraphStyle(
                "FairFlowSubtitle",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                textColor=TEXT,
                spaceAfter=4 * mm,
            ),


        "section":
            ParagraphStyle(
                "FairFlowSection",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=16,
                textColor=INK,
                spaceBefore=3 * mm,
                spaceAfter=3 * mm,
            ),


        "body":
            ParagraphStyle(
                "FairFlowBody",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=8.4,
                leading=12,
                textColor=TEXT,
                spaceAfter=2.5 * mm,
            ),


        "small":
            ParagraphStyle(
                "FairFlowSmall",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=7.3,
                leading=10,
                textColor=MUTED,
            ),


        "strong":
            ParagraphStyle(
                "FairFlowStrong",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=INK,
            ),


        "th":
            ParagraphStyle(
                "TableHeader",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=6.6,
                leading=8,
                textColor=MUTED,
            ),


        "td":
            ParagraphStyle(
                "TableBody",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=7.1,
                leading=9,
                textColor=TEXT,
            ),


        "tdb":
            ParagraphStyle(
                "TableBodyStrong",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=7.1,
                leading=9,
                textColor=INK,
            ),


        "disc_title":
            ParagraphStyle(
                "DisclaimerTitle",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=INK,
                spaceAfter=1.5 * mm,
            ),


        "disc_body":
            ParagraphStyle(
                "DisclaimerBody",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=7.4,
                leading=10.5,
                textColor=colors.HexColor("#5E625E"),
            ),

    }


# =========================================================
# PARAGRAPH / TABLE HELPERS
# =========================================================

def _p(
    value,
    style
):

    return Paragraph(
        _safe(value),
        style
    )


def _table(
    rows,
    widths,
    header=True
):

    table = Table(
        rows,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT",
    )


    commands = [

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            LINE
        ),

        (
            "BACKGROUND",
            (0, 0),
            (-1, -1),
            WHITE
        ),

    ]


    if header:

        commands += [

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT_GREY
            ),

            (
                "LINEBELOW",
                (0, 0),
                (-1, 0),
                0.7,
                LINE
            ),

        ]


    table.setStyle(
        TableStyle(
            commands
        )
    )


    return table


def _metrics(
    items,
    styles
):

    labels = [
        _p(
            label,
            styles["th"]
        )
        for label, _ in items
    ]


    values = [
        _p(
            value,
            styles["tdb"]
        )
        for _, value in items
    ]


    count = max(
        len(items),
        1
    )


    width = (
        180 * mm
    ) / count


    table = Table(
        [
            labels,
            values
        ],
        colWidths=[
            width
        ] * count,
        hAlign="LEFT",
    )


    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                WHITE
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.45,
                LINE
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.35,
                LINE
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
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
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT_GREY
            ),

        ])

    )


    return table


# =========================================================
# PAGE HEADER / FOOTER
# =========================================================

def _draw_page_frame(
    canvas,
    document
):

    canvas.saveState()


    page_width, page_height = A4


    canvas.setFont(
        "Helvetica-Bold",
        8
    )

    canvas.setFillColor(
        INK
    )

    canvas.drawString(
        document.leftMargin,
        page_height - 10 * mm,
        "FairFlow"
    )


    canvas.setFont(
        "Helvetica",
        7
    )

    canvas.setFillColor(
        MUTED
    )

    canvas.drawRightString(
        page_width - document.rightMargin,
        page_height - 10 * mm,
        "Service Flow Analysis Report"
    )


    canvas.setStrokeColor(
        LINE
    )

    canvas.setLineWidth(
        0.45
    )


    canvas.line(
        document.leftMargin,
        page_height - 12.5 * mm,
        page_width - document.rightMargin,
        page_height - 12.5 * mm,
    )


    canvas.line(
        document.leftMargin,
        13 * mm,
        page_width - document.rightMargin,
        13 * mm,
    )


    canvas.setFont(
        "Helvetica",
        6.3
    )

    canvas.setFillColor(
        MUTED
    )


    canvas.drawString(
        document.leftMargin,
        8.8 * mm,
        "FairFlow - decision-support system"
    )


    canvas.drawCentredString(
        page_width / 2,
        8.8 * mm,
        COPYRIGHT_TEXT
    )


    canvas.drawRightString(
        page_width - document.rightMargin,
        8.8 * mm,
        f"Page {canvas.getPageNumber()}"
    )


    canvas.restoreState()


# =========================================================
# PDF GENERATOR
# =========================================================

def _generate_pdf(
    analysis_input,
    ai_result,
    result=None
):

    output = BytesIO()

    styles = _styles()


    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=19 * mm,
        title="FairFlow Service Flow Analysis Report",
        author="Devyansh Nath Mathur",
        subject="FairFlow AI Service Flow Analysis",
    )


    story = []


    # =====================================================
    # DATA
    # =====================================================

    baseline = _get(
        ai_result,
        "baseline",
        {}
    )


    recommended = _get(
        ai_result,
        "recommended",
        {}
    )


    baseline_summary = _get(
        baseline,
        "summary",
        {}
    )


    recommended_summary = _get(
        recommended,
        "summary",
        {}
    )


    if (
        result is not None
        and
        not baseline_summary
    ):

        baseline = result

        baseline_summary = _get(
            result,
            "summary",
            {}
        )


    stages_in = _as_list(
        _get(
            analysis_input,
            "stages",
            []
        )
    )


    stages_now = _as_list(
        _get(
            baseline,
            "stages",
            []
        )
    )


    groups_now = _as_list(
        _get(
            baseline,
            "groups",
            []
        )
    )


    group_mix = _get(
        analysis_input,
        "group_mix",
        {}
    )


    changes = _as_list(
        _get(
            ai_result,
            "stage_changes",
            []
        )
    )


    model_metrics = _get(
        ai_result,
        "model_metrics",
        {}
    )


    visitors = _get(
        analysis_input,
        "visitor_count",
        _get(
            baseline_summary,
            "visitors",
            0
        )
    )


    hours = _get(
        analysis_input,
        "session_hours",
        0
    )


    current_wait = _get(
        baseline_summary,
        "average_wait",
        0
    )


    recommended_wait = _get(
        recommended_summary,
        "average_wait",
        0
    )


    current_gap = _get(
        ai_result,
        "baseline_fairness_gap",
        _get(
            baseline_summary,
            "fairness_gap",
            0
        )
    )


    recommended_gap = _get(
        ai_result,
        "recommended_fairness_gap",
        _get(
            recommended_summary,
            "fairness_gap",
            0
        )
    )


    bottleneck = _get(
        baseline_summary,
        "bottleneck",
        ""
    )


    improvement = _get(
        ai_result,
        "wait_improvement_percent",
        0
    )


    headline = _get(
        ai_result,
        "headline",
        "FairFlow recommendation"
    )


    explanation = _get(
        ai_result,
        "explanation",
        ""
    )


    fairness_insight = _get(
        ai_result,
        "fairness_insight",
        ""
    )


    # =====================================================
    # TITLE
    # =====================================================

    story += [

        Paragraph(
            "FAIRFLOW",
            styles["small"]
        ),

        Paragraph(
            "Service Flow Analysis Report",
            styles["title"]
        ),

        Paragraph(
            (
                "A decision-support analysis combining "
                "service-flow simulation, machine-learning "
                "screening and fairness-aware staffing "
                "recommendation."
            ),
            styles["subtitle"],
        ),

        Paragraph(
            (
                "<b>Report generated:</b> "
                f"{_safe(datetime.now().strftime('%d %B %Y, %I:%M %p'))}"
            ),
            styles["small"],
        ),

        Spacer(
            1,
            5 * mm
        ),

    ]


    # =====================================================
    # 1. EXECUTIVE SUMMARY
    # =====================================================

    story += [

        Paragraph(
            "1. Executive summary",
            styles["section"]
        ),

        _metrics(
            [
                (
                    "VISITORS",
                    _fmt(
                        visitors,
                        0
                    )
                ),

                (
                    "CURRENT AVG. WAIT",
                    f"{_fmt(current_wait)} min"
                ),

                (
                    "RECOMMENDED AVG. WAIT",
                    f"{_fmt(recommended_wait)} min"
                ),

                (
                    "ESTIMATED REDUCTION",
                    f"{_fmt(improvement, 1)}%"
                ),
            ],
            styles,
        ),

        Spacer(
            1,
            4 * mm
        ),

        Paragraph(
            f"<b>{_safe(headline)}</b>",
            styles["strong"]
        ),

    ]


    if explanation:

        story.append(
            Paragraph(
                _safe(explanation),
                styles["body"]
            )
        )


    if fairness_insight:

        story.append(
            Paragraph(
                _safe(fairness_insight),
                styles["body"]
            )
        )


    # =====================================================
    # 2. SUBMITTED SERVICE SETUP
    # =====================================================

    setup_rows = [

        [
            _p(
                "STAGE",
                styles["th"]
            ),

            _p(
                "COUNTERS",
                styles["th"]
            ),

            _p(
                "AVG. SERVICE TIME",
                styles["th"]
            ),
        ]

    ]


    for stage in stages_in:

        setup_rows.append([

            _p(
                _get(
                    stage,
                    "name",
                    ""
                ),
                styles["tdb"]
            ),

            _p(
                _fmt(
                    _get(
                        stage,
                        "counters",
                        0
                    ),
                    0
                ),
                styles["td"]
            ),

            _p(
                (
                    f"{_fmt(_get(stage, 'service_time', 0))} "
                    "min"
                ),
                styles["td"]
            ),

        ])


    story += [

        Paragraph(
            "2. Submitted service setup",
            styles["section"]
        ),

        _table(
            setup_rows,
            [
                85 * mm,
                40 * mm,
                55 * mm
            ]
        ),

        Spacer(
            1,
            3.5 * mm
        ),

        _metrics(
            [
                (
                    "EXPECTED VISITORS",
                    _fmt(
                        visitors,
                        0
                    )
                ),

                (
                    "SESSION DURATION",
                    f"{_fmt(hours)} hours"
                ),
            ],
            styles,
        ),

    ]


    # =====================================================
    # 3. VISITOR MIX
    # =====================================================

    visitor_rows = [

        [
            _p(
                "VISITOR GROUP",
                styles["th"]
            ),

            _p(
                "SHARE",
                styles["th"]
            ),
        ],


        [
            _p(
                "General",
                styles["tdb"]
            ),

            _p(
                f"{_fmt(_get(group_mix, 'general', 0), 1)}%",
                styles["td"]
            ),
        ],


        [
            _p(
                "Elderly",
                styles["tdb"]
            ),

            _p(
                f"{_fmt(_get(group_mix, 'elderly', 0), 1)}%",
                styles["td"]
            ),
        ],


        [
            _p(
                "Pregnant",
                styles["tdb"]
            ),

            _p(
                f"{_fmt(_get(group_mix, 'pregnant', 0), 1)}%",
                styles["td"]
            ),
        ],


        [
            _p(
                "Mobility-limited",
                styles["tdb"]
            ),

            _p(
                f"{_fmt(_get(group_mix, 'mobility', 0), 1)}%",
                styles["td"]
            ),
        ],

    ]


    story += [

        Paragraph(
            "3. Visitor mix",
            styles["section"]
        ),

        _table(
            visitor_rows,
            [
                135 * mm,
                45 * mm
            ]
        ),

    ]


    # =====================================================
    # 4. CURRENT SERVICE PERFORMANCE
    # =====================================================

    performance_rows = [

        [
            _p(
                "STAGE",
                styles["th"]
            ),

            _p(
                "COUNTERS",
                styles["th"]
            ),

            _p(
                "AVG. WAIT",
                styles["th"]
            ),

            _p(
                "MAX WAIT",
                styles["th"]
            ),

            _p(
                "MAX QUEUE",
                styles["th"]
            ),

            _p(
                "UTILIZATION",
                styles["th"]
            ),
        ]

    ]


    for stage in stages_now:

        performance_rows.append([

            _p(
                _get(
                    stage,
                    "name",
                    ""
                ),
                styles["tdb"]
            ),

            _p(
                _fmt(
                    _get(
                        stage,
                        "counters",
                        0
                    ),
                    0
                ),
                styles["td"]
            ),

            _p(
                f"{_fmt(_get(stage, 'average_wait', 0))} min",
                styles["td"]
            ),

            _p(
                f"{_fmt(_get(stage, 'maximum_wait', 0))} min",
                styles["td"]
            ),

            _p(
                _fmt(
                    _get(
                        stage,
                        "max_queue",
                        0
                    ),
                    0
                ),
                styles["td"]
            ),

            _p(
                f"{_fmt(_get(stage, 'utilization', 0), 1)}%",
                styles["td"]
            ),

        ])


    story += [

        Paragraph(
            "4. Current service performance",
            styles["section"]
        ),

        Paragraph(
            (
                "The current simulation identifies "
                f"<b>{_safe(bottleneck)}</b> "
                "as the primary bottleneck."
            ),
            styles["body"],
        ),

        _table(
            performance_rows,
            [
                42 * mm,
                22 * mm,
                31 * mm,
                31 * mm,
                26 * mm,
                28 * mm,
            ]
        ),

    ]


    # =====================================================
    # 5. VISITOR-GROUP EXPERIENCE
    # =====================================================

    names = [
        "General",
        "Elderly",
        "Pregnant",
        "Mobility-limited",
    ]


    shares = [

        _get(
            group_mix,
            "general",
            0
        ),

        _get(
            group_mix,
            "elderly",
            0
        ),

        _get(
            group_mix,
            "pregnant",
            0
        ),

        _get(
            group_mix,
            "mobility",
            0
        ),

    ]


    group_rows = [

        [
            _p(
                "VISITOR GROUP",
                styles["th"]
            ),

            _p(
                "SHARE",
                styles["th"]
            ),

            _p(
                "AVG. WAIT",
                styles["th"]
            ),
        ]

    ]


    for index, group in enumerate(
        groups_now
    ):

        name = (
            names[index]
            if index < len(names)
            else _get(
                group,
                "name",
                f"Group {index + 1}"
            )
        )


        share = (
            shares[index]
            if index < len(shares)
            else 0
        )


        group_rows.append([

            _p(
                name,
                styles["tdb"]
            ),

            _p(
                f"{_fmt(share, 1)}%",
                styles["td"]
            ),

            _p(
                f"{_fmt(_get(group, 'average_wait', 0))} min",
                styles["td"]
            ),

        ])


    story += [

        Paragraph(
            "5. Visitor-group experience",
            styles["section"]
        ),

        _table(
            group_rows,
            [
                90 * mm,
                40 * mm,
                50 * mm
            ]
        ),

        Spacer(
            1,
            3 * mm
        ),

        _metrics(
            [
                (
                    "CURRENT FAIRNESS GAP",
                    f"{_fmt(current_gap)} min"
                ),

                (
                    "RECOMMENDED FAIRNESS GAP",
                    f"{_fmt(recommended_gap)} min"
                ),
            ],
            styles,
        ),

    ]


    # =====================================================
    # 6. MACHINE-LEARNING ANALYSIS
    # =====================================================

    story += [

        Paragraph(
            "6. Machine-learning analysis",
            styles["section"]
        ),

        _metrics(
            [
                (
                    "CONFIGURATIONS SCREENED",
                    _fmt(
                        _get(
                            ai_result,
                            "configurations_screened_by_ml",
                            0
                        ),
                        0
                    )
                ),

                (
                    "CONFIGURATIONS VERIFIED",
                    _fmt(
                        _get(
                            ai_result,
                            "configurations_verified_by_simulation",
                            0
                        ),
                        0
                    )
                ),

                (
                    "TEST-SET R²",
                    _fmt(
                        _get(
                            model_metrics,
                            "wait_r2",
                            0
                        ),
                        3
                    )
                ),

                (
                    "MEDIAN ABS. ERROR",
                    (
                        f"{_fmt(_get(model_metrics, 'wait_median_ae', 0))} "
                        "min"
                    )
                ),
            ],
            styles,
        ),

        Spacer(
            1,
            3 * mm
        ),

        _metrics(
            [
                (
                    "CURRENT SETUP ML FORECAST",
                    (
                        f"{_fmt(_get(ai_result, 'baseline_ml_predicted_wait', 0))} "
                        "min"
                    )
                ),

                (
                    "RECOMMENDED SETUP ML FORECAST",
                    (
                        f"{_fmt(_get(ai_result, 'recommended_ml_predicted_wait', 0))} "
                        "min"
                    )
                ),
            ],
            styles,
        ),

        Spacer(
            1,
            2 * mm
        ),

        Paragraph(
            (
                "Model performance is measured on held-out "
                "scenarios generated by FairFlow's simulation "
                "engine. These metrics should not be interpreted "
                "as real-world operational validation."
            ),
            styles["small"],
        ),

    ]


    # =====================================================
    # 7. RECOMMENDED ACTION
    # =====================================================

    recommendation_content = [

        Paragraph(
            f"<b>{_safe(headline)}</b>",
            styles["strong"]
        )

    ]


    if explanation:

        recommendation_content.append(
            Paragraph(
                _safe(explanation),
                styles["body"]
            )
        )


    if fairness_insight:

        recommendation_content.append(
            Paragraph(
                _safe(fairness_insight),
                styles["body"]
            )
        )


    recommendation_box = Table(
        [
            [
                recommendation_content
            ]
        ],
        colWidths=[
            180 * mm
        ],
        hAlign="LEFT",
    )


    recommendation_box.setStyle(

        TableStyle([

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
                0.6,
                colors.HexColor("#C8DCD8")
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
            ),

        ])

    )


    story += [

        Paragraph(
            "7. Recommended action",
            styles["section"]
        ),

        recommendation_box,

    ]


    # =====================================================
    # 8. RECOMMENDED STAFFING
    # =====================================================

    staffing_rows = [

        [
            _p(
                "STAGE",
                styles["th"]
            ),

            _p(
                "CURRENT",
                styles["th"]
            ),

            _p(
                "RECOMMENDED",
                styles["th"]
            ),

            _p(
                "CHANGE",
                styles["th"]
            ),
        ]

    ]


    for change in changes:

        difference = int(
            round(
                _num(
                    _get(
                        change,
                        "difference",
                        0
                    )
                )
            )
        )


        change_text = (
            f"+{difference}"
            if difference > 0
            else str(difference)
            if difference < 0
            else "No change"
        )


        staffing_rows.append([

            _p(
                _get(
                    change,
                    "name",
                    ""
                ),
                styles["tdb"]
            ),

            _p(
                _fmt(
                    _get(
                        change,
                        "before",
                        0
                    ),
                    0
                ),
                styles["td"]
            ),

            _p(
                _fmt(
                    _get(
                        change,
                        "after",
                        0
                    ),
                    0
                ),
                styles["td"]
            ),

            _p(
                change_text,
                styles["td"]
            ),

        ])


    story += [

        Paragraph(
            "8. Recommended staffing",
            styles["section"]
        ),

        _table(
            staffing_rows,
            [
                75 * mm,
                35 * mm,
                40 * mm,
                30 * mm
            ]
        ),

        Spacer(
            1,
            3 * mm
        ),

        _metrics(
            [
                (
                    "CURRENT AVG. WAIT",
                    f"{_fmt(current_wait)} min"
                ),

                (
                    "RECOMMENDED AVG. WAIT",
                    f"{_fmt(recommended_wait)} min"
                ),

                (
                    "WAIT REDUCTION",
                    f"{_fmt(improvement, 1)}%"
                ),
            ],
            styles,
        ),

    ]


    # =====================================================
    # 9. METHODOLOGY
    # =====================================================

    methodology = [

        (
            "1",
            "Simulate current service flow",
            (
                "Virtual visitors move through the configured "
                "service stages to estimate waiting times, "
                "queues and utilization."
            )
        ),

        (
            "2",
            "Generate alternative allocations",
            (
                "Feasible staffing configurations are generated "
                "while keeping the total number of counters "
                "unchanged."
            )
        ),

        (
            "3",
            "Rank using machine learning",
            (
                "The trained wait-time model rapidly estimates "
                "congestion behaviour and ranks candidate "
                "configurations."
            )
        ),

        (
            "4",
            "Verify shortlisted configurations",
            (
                "Leading ML-ranked configurations are tested "
                "again using detailed service-flow simulation."
            )
        ),

        (
            "5",
            "Select the final recommendation",
            (
                "Waiting time, bottleneck severity, utilization "
                "and fairness are evaluated together before "
                "the final staffing recommendation is selected."
            )
        ),

    ]


    method_rows = []


    for (
        number,
        title,
        description
    ) in methodology:

        method_rows.append([

            _p(
                number,
                styles["tdb"]
            ),

            [
                Paragraph(
                    f"<b>{_safe(title)}</b>",
                    styles["tdb"]
                ),

                Paragraph(
                    _safe(description),
                    styles["td"]
                ),
            ],

        ])


    method_table = Table(
        method_rows,
        colWidths=[
            12 * mm,
            168 * mm
        ],
        hAlign="LEFT",
    )


    method_table.setStyle(

        TableStyle([

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LINEBELOW",
                (0, 0),
                (-1, -2),
                0.35,
                LINE
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

        ])

    )


    story += [

        Paragraph(
            "9. Methodology",
            styles["section"]
        ),

        method_table,

        Spacer(
            1,
            5 * mm
        ),

    ]


    # =====================================================
    # 10. SIMULATION & USE DISCLAIMER
    # =====================================================

    disclaimer_box = Table(
        [
            [
                [
                    Paragraph(
                        "Simulation &amp; Use Disclaimer",
                        styles["disc_title"]
                    ),

                    Paragraph(
                        _safe(
                            DISCLAIMER_TEXT
                        ),
                        styles["disc_body"]
                    ),
                ]
            ]
        ],
        colWidths=[
            180 * mm
        ],
        hAlign="LEFT",
    )


    disclaimer_box.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                MUSTARD_SOFT
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                MUSTARD
            ),

            (
                "LINEBEFORE",
                (0, 0),
                (0, -1),
                3,
                MUSTARD
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
            ),

        ])

    )


    story.append(

        KeepTogether([

            Paragraph(
                "10. Simulation &amp; Use Disclaimer",
                styles["section"]
            ),

            disclaimer_box,

        ])

    )


    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(
        story,
        onFirstPage=_draw_page_frame,
        onLaterPages=_draw_page_frame,
    )


    output.seek(
        0
    )


    return output


# =========================================================
# PUBLIC REPORT FUNCTIONS
# =========================================================

def generate_fairflow_report(
    *args,
    **kwargs
):

    (
        analysis_input,
        ai_result,
        result
    ) = _normalise_arguments(
        *args,
        **kwargs
    )


    return _generate_pdf(
        analysis_input,
        ai_result,
        result
    )


def generate_analysis_report(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )


def generate_pdf_report(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )


def generate_report(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )


def generate_report_pdf(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )


def build_pdf_report(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )


def build_analysis_report(
    *args,
    **kwargs
):

    return generate_fairflow_report(
        *args,
        **kwargs
    )