
    function DeleteSubscriberConfirmation(student_id){


    $("#error").html("Do you really want to delete this subscriber?");
    $("#delete_student").attr("onclick",`DeleteSubscriber(${student_id})`)
      $('#exampleModal').modal("show");
    }


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

    function DeleteSubscriber(student_id)
    {
    var course_id = $("#course_id").val()
    $.ajax({
    url: `/plattform/course/subscriber/delete?user=${student_id}&course=${course_id}`,
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: (data) => {

       window.location.reload();
    },
    error: (data) => {
    alert("Internal  server error!");
    }
  });
    }