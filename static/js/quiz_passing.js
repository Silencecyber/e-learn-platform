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

function get_results() {
    const data = {};
    answers = $(".answer:checked");
    module_id = $("#module_id").val();
    quiz_id = $("#quiz_id").val();


    $(".answer:checked").each(function(i, obj) {
        var question = $(obj).closest('.question').attr('data-question')
        var answer = $(obj).val();
        if (data.hasOwnProperty(question)) {
            data[question].push(answer);
        } else {
            data[question] = []
            data[question].push(answer)

        }
    })

    $.ajax({
        url: "/plattform/api/check_results/",
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            answers: data,
            module_id: module_id,
            quiz_id: quiz_id
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (data) => {
            //let url=data['redirect_to'];
            //let redirect_url=window.location.origin+url
            //window.location.href = redirect_url;
            if (data['error']) {


                $("#error").html(data['error']);
                $('#myModal').modal("show");
            } else {
                var results_wrongs = [];
                $(".question").each(function() {


                    if (data['wrong_answers'].hasOwnProperty($(this).attr('data-question'))) {

                        var question = $(this).attr('data-question');
                        var wrong_answers = data['wrong_answers'][$(this).attr('data-question')]

                        results_wrongs.push({
                            'question': question,
                            'wrongs': wrong_answers
                        })

                        var answers = $(this).find('.answer');


                    }

                })

                var result = data['score'];
                var res = $(".results");
                res.css({
                    "display": "block"
                });
                $(".questions").css({
                    "display": "none"
                })

                res.html("Your score: " + "<b>" + result + "</b><br>");
                if (Object.keys(data['wrong_answers']).length !== 0) {
                    res.append("<br>This is  your wrong answers to questions<br>")
                }

                results_wrongs.forEach(function(obj, i) {

                    if (obj['wrongs'].length !== 1)

                    {
                        var wrongs = ""
                        obj['wrongs'].forEach(function(obj, i) {

                            wrongs += obj + "<br>";
                        })

                        var html = `<p> ${i+1}. ${obj['question']} <br> ${wrongs} </p>`


                    } else {

                        var html = `<p> ${i+1}. ${obj['question']} <br> ${obj['wrongs']} </p>`
                    }

                    res.append(html)


                })
                res.append('<button class="button-13 w-button" style="margin-right:20px;" onclick="window.location.reload();">Try again</button>')
                res.append('<a href="/plattform/home" class="button-13 w-button">Home</a>')
                $(".radio-qs").css({
                    "display": "none"
                })

                if ((Number(result.split("/")[0]) < Number(result.split("/")[1])) && Object.keys(data['wrong_answers']).length === 0) {
                    $("#error").html("Your score is not max, because some questions require multiple answers, but not all were provided");
                    $('#myModal').modal("show");

                }
            }

        },
        error: (data) => {
            alert("error");
        }
    });
}
var current_question_id = 1;
var questions_number = Number($("#questions_number").val());




function NextQuestion() {


    if (current_question_id === questions_number) {

        $("#next").css({
            "display": "none"
        })
        $("#results").css({
            "display": "inline"
        })
    } else {
        $(`#${current_question_id}`).css({
            "display": "none"
        });
        $(`[data-question-number='${current_question_id}']`).prop('checked', false);

        current_question_id++;

        $(`#${current_question_id}`).css({
            "display": "block"
        });

        $(`[data-question-number='${current_question_id}']`).prop('checked', true);



        if (current_question_id === questions_number) {
            $("#next").css({
                "display": "none"
            })
            $("#results").css({
                "display": "inline"
            })

        } else if (current_question_id === 1) {
            $("#prev").css({
                "display": "none"
            })
        } else {
            $("#prev").css({
                "display": "inline"
            })

        }

    }
}

function PreviousQuestion() {

    if (current_question_id === 1) {
        console.log("First")
    } else {
        if (current_question_id === questions_number) {
            $("#next").css({
                "display": "inline"
            })
            $("#results").css({
                "display": "none"
            })

        }


        $(`[data-question-number='${current_question_id}']`).prop('checked', false);
        $(`#${current_question_id}`).css({
            "display": "none"
        });
        current_question_id--;
        $(`[data-question-number='${current_question_id}']`).prop('checked', true);
        $(`#${current_question_id}`).css({
            "display": "block"
        });

        if (current_question_id === 1) {
            $("#prev").css({
                "display": "none"
            })
        }

    }
}

var questions = $(".question");
var counter = 0;
$(".current-q-radio[data-question-number='1']").prop('checked', true)
$(questions).each(function(i, obj) {

    if (i != 0) {
        $(obj).css({
            "display": "none"
        });
    }




})

$(".current-q-radio").click(function() {
    $(`#${current_question_id}`).css({
        "display": "none"
    });

    current_question_id = Number($(this).attr("data-question-number"));

    if (current_question_id === questions_number) {
        $("#next").css({
            "display": "none"
        })
        $("#results").css({
            "display": "inline"
        })

    } else if (current_question_id === 1) {

        $("#prev").css({
            "display": "none"
        })
    } else {
        $("#next").css({
            "display": "inline"
        })
        $("#prev").css({
            "display": "inline"
        })
        $("#results").css({
            "display": "none"
        })
    }

    $(`#${current_question_id}`).css({
        "display": "block"
    });

})



$(".answer").click(function() {

    var limit_ans = $(this).closest(".question").attr("data-anslimit");
    var checked = $(this).closest(".question").find(".answer:checked").length;
    var $radio = $(this);
    // if this was previously checked
    if ($radio.data('waschecked') == true) {
        $radio.prop('checked', false);
        $radio.data('waschecked', false);
    } else {
        if (checked > limit_ans) {
            $radio.prop('checked', false);
            $radio.data('waschecked', false);
            $("#error").html(`Only ${limit_ans} answer\s are avaliable for this question`);
            $('#myModal').modal("show");
        } else {
            $radio.prop('checked', true);
            $radio.data('waschecked', true);
        }
    }


    var question_id = $(this).closest(".question").attr("id")

    var answ_counter = 0


    $(`div[id='${question_id}']`).find(".answer").each(function(i, obj) {




        if ($(obj).is(':checked')) {

            answ_counter++;

        }

    })

    if (answ_counter > 0) {

        $(`span[data-question-number="${question_id}"]`).css({
            "color": "#57a16a"
        })

    } else {
        $(`span[data-question-number="${question_id}"]`).css({
            "color": "#d64545"
        })
    }



})