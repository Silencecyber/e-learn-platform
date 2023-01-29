
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

    function AddSubscriber(student_id,course_id)
    {

    $.ajax({
    url: `/plattform/course/subscribers/${course_id}/add`,
    type: "POST",
    data: jQuery.param({user:student_id}),
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