function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



const csrftoken = getCookie('csrftoken');

const url = window.location.pathname


$.ajax({
    url: url,
    type: "POST",
    dataType: "json",
    headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
    },
    success: (data) => {
        var students = data['students_names']
        var results = data['students_results']
        const chart = Highcharts.chart('container', {

            chart: {
                inverted: true,
                zoomType: 'xy',
                events: {
                    load() {
                        this.yAxis[0].setExtremes(0, 100)
                    }
                }
            },
            title: {
                text: 'Gradebook',
                align: 'center'
            },

            xAxis: {
                categories: students
            },
            yAxis: {
                title: {
                    text: 'Percent'
                }
            },

            series: [{

                type: 'column',
                name: 'Progress',
                colorByPoint: true,
                data: results,
                showInLegend: false
            }]
        });

        document.getElementById('plain').addEventListener('click', () => {
            chart.update({
                chart: {
                    inverted: false,
                    polar: false
                }
            });
        });

        document.getElementById('inverted').addEventListener('click', () => {
            chart.update({
                chart: {
                    inverted: true,
                    polar: false
                }

            });
        });

        document.getElementById('polar').addEventListener('click', () => {
            chart.update({
                chart: {
                    inverted: false,
                    polar: true
                }
            });
        });




        // tell the embed parent frame the height of the content
        if (window.parent && window.parent.parent) {
            window.parent.parent.postMessage(["resultsFrame", {
                height: document.body.getBoundingClientRect().height,
                slug: ""
            }], "*")
        }

        // always overwrite window.name, in case users try to set it manually
        window.name = "result"

        let allLines = []

        window.addEventListener("message", (message) => {
            if (message.data.console) {
                let insert = document.querySelector("#insert")
                allLines.push(message.data.console.payload)
                insert.innerHTML = allLines.join(";\r")

                let result = eval.call(null, message.data.console.payload)
                if (result !== undefined) {
                    console.log(result)
                }
            }
        })
    },
    error: (data) => {
        alert("Internal server error");
    }
});