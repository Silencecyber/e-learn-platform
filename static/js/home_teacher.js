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


        var categories = ["Students", "Teachers"]
        var courses_number=data['courses_number']
        var students_number = data['students_number']
        var teachers_number = data['teachers_number']
        var results = [students_number, teachers_number]


        $("#students_number").html(students_number)
        $("#teachers_number").html(teachers_number)
        $('#courses_number').html(courses_number)



        var categories = ["Students", "Teachers"]
     Highcharts.chart('chart-1', {

            chart: {
                inverted: false,
                polar: false,
                zoomType: 'xy',

            },
            title: {
                text: 'Teachers to student ratio',
                align: 'center'
            },

            xAxis: {
                categories: categories
            },
            yAxis: {
                title: {
                    text: ''
                }
            },

            series: [{
                type: 'column',
                name: 'Amount',
                colorByPoint: true,
                data: results,
                showInLegend: false
            }]
        });




        var bigger_the_course_limit = data['bigger_the_course_limit']
        var course_top_limit = data['course_top_limit']

        if (bigger_the_course_limit) {
            var chart_2_title = `Top ${course_top_limit} courses`
        } else {
            var chart_2_title = "Courses popularity"
        }

        Highcharts.chart('chart-2', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: chart_2_title,
                align: 'center'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.0f}%</b>'
            },
            accessibility: {
                point: {
                    valueSuffix: '%'
                }
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b> {point.percentage:.1f} %'
                    }
                }
            },

            tooltip: {
                pointFormat: '{point.name}<br>{point.y} subscriber\\s'
            },
            series: [{
                name: 'Subscribers',
                colorByPoint: true,
                data: data['courses_popularity']
            }]
        });

        var bigger_the_topic_limit = data['bigger_the_topic_limit']
        var topics_top_limit = data['topics_top_limit']

        if (bigger_the_topic_limit) {
            var chart_3_title = `Top ${topics_top_limit} topics amount`
        } else {
            var chart_3_title = "Topics amount"
        }

        Highcharts.chart('chart-3', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: chart_3_title,
                align: 'center'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.0f}%</b>'
            },
            accessibility: {
                point: {
                    valueSuffix: '%'
                }
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b> {point.percentage:.1f} %'
                    }
                }
            },

            tooltip: {
                pointFormat: '{point.name}<br>{point.y} topic\\s'
            },
            series: [{
                name: 'Subscribers',
                colorByPoint: true,
                data: data['topics_amount']
            }]
        });


        var bigger_the_quiz_limit = data['bigger_the_quiz_limit']
        var quiz_top_limit = data['quiz_top_limit']


        if (bigger_the_quiz_limit) {

            var chart_4_title = `Top ${quiz_top_limit} quizes amount`
        } else {
            var chart_4_title = "Quizes amount"
        }

        Highcharts.chart('chart-4', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: chart_4_title,
                align: 'center'
            },
            tooltip: {
                pointFormat: '{series.name} <b>{point.percentage:.0f}%</b>'
            },
            accessibility: {
                point: {
                    valueSuffix: '%'
                }
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b> {point.percentage:.1f} %'
                    }
                }
            },

            tooltip: {
                pointFormat: '{point.name}<br>{point.y} quiz\\es'
            },
            series: [{
                name: 'Subscribers',
                colorByPoint: true,
                data: data["quizes_amount"]
            }]
        });
    },
    error: (data) => {
        alert("Internal server error");
    }
});