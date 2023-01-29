      function DeleteCourseConfirmation()
      {
        $(document).ready(function(){

    $("#error").html("Do you really want to delete this course?<br>After you click  the  delete button, all modules, all topics will be also deleted!");
      $('#exampleModal').modal("show");
  });
      }

      function DeleteCourse(){

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
  const course_id=$("#course_id").val();

   $.ajax({
      url: "/plattform/delete/course/"+course_id,
      type: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
                },
      success:(data)=>{
      window.location.href="/plattform/courses"
      },
      error:()=>{

      alert("Internal server error!")
      }
  })
  }