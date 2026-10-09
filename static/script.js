/* =========================================================
   OPEN SERVICE SETUP
========================================================= */

const analyzeSetupButton =
    document.getElementById("analyzeSetupButton");


if (analyzeSetupButton) {

    analyzeSetupButton.addEventListener(
        "click",
        () => {

            window.location.href =
                "/simulate";

        }
    );

}



/* =========================================================
   PERFORMANCE BAR ANIMATION
========================================================= */

const animatedBars =
    document.querySelectorAll(
        ".bar, .fairness-fill"
    );


if (animatedBars.length > 0) {

    const barObserver =
        new IntersectionObserver(

            entries => {

                entries.forEach(entry => {

                    if (!entry.isIntersecting) {
                        return;
                    }


                    const bar =
                        entry.target;


                    const width =
                        bar.dataset.width;


                    bar.style.width =
                        width + "%";


                    barObserver.unobserve(
                        bar
                    );

                });

            },

            {
                threshold: 0.45
            }

        );


    animatedBars.forEach(bar => {

        barObserver.observe(bar);

    });

}



/* =========================================================
   BEFORE / AFTER COMPARISON
========================================================= */

const switchButtons =
    document.querySelectorAll(
        ".switch-button"
    );


const comparisonValues = {

    before: {

        label:
            "Current setup",

        headline:
            "Uneven staff utilization",

        averageWait:
            "21 min",

        priorityWait:
            "34 min",

        verificationStaff:
            "1",

        serviceStaff:
            "3",

        status:
            "Bottleneck present"

    },


    after: {

        label:
            "Suggested setup",

        headline:
            "More balanced service flow",

        averageWait:
            "13 min",

        priorityWait:
            "16 min",

        verificationStaff:
            "2",

        serviceStaff:
            "2",

        status:
            "Flow improved"

    }

};


switchButtons.forEach(button => {

    button.addEventListener(
        "click",
        () => {


            switchButtons.forEach(item => {

                item.classList.remove(
                    "active"
                );

            });


            button.classList.add(
                "active"
            );


            const selectedView =
                button.dataset.view;


            const data =
                comparisonValues[
                    selectedView
                ];


            document
                .getElementById(
                    "viewLabel"
                )
                .textContent =
                    data.label;


            document
                .getElementById(
                    "viewHeadline"
                )
                .textContent =
                    data.headline;


            document
                .getElementById(
                    "averageWait"
                )
                .textContent =
                    data.averageWait;


            document
                .getElementById(
                    "priorityWait"
                )
                .textContent =
                    data.priorityWait;


            document
                .getElementById(
                    "verificationStaff"
                )
                .textContent =
                    data.verificationStaff;


            document
                .getElementById(
                    "serviceStaff"
                )
                .textContent =
                    data.serviceStaff;


            document
                .getElementById(
                    "flowStatus"
                )
                .textContent =
                    data.status;

        }

    );

});