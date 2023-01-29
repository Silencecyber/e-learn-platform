      function DeleteQuizConfirmation()
      {
        $(document).ready(function(){

    $("#error").html("Do you really want to delete this quiz?<br>This action cannot be undone!");
      $('#myModal').modal("show");
  });
      }

      function DeleteQuiz(){

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


   $.ajax({
      url: "/plattform/remove/quiz/"+quiz_id,
      type: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
                },
      success:(data)=>{
      window.location.href="/plattform/edit/course/"+course_id
      },
      error:()=>{

      alert("Internal server error!")
      }
  })
  }


    var counter =Number($("#counter").val());
    var ans_counter=Number($("#ans_counter").val());
    var quiz_id=$("#quiz_id").val();
    var course_id=$("#course_id").val();

    console.log(counter)
    console.log(ans_counter)
    console.log(quiz_id)
    console.log(course_id)

    function Edit()
    {
        var  questions_data=[];
        var module_id=$('[name="module_id"]').val()
        var quiz_name=$('#quiz_name').val()
        $("#questions").find(".question").each(function(i,obj)
        {
            var q_text=$(obj).find('[name="question_text"]').val();
            var q_answers=[];
            $(obj).find(".answer").each(function(i,obj)
            {
                var answer_text=$(obj).find('[name="answer_text"]').val();
                var is_correct=$(obj).find('[name="is_correct"]').is(":checked")

                var data = {"answer_text":answer_text,"is_correct":is_correct}
                q_answers.push(data)

            })
            var q_data={"question_text":q_text,"answers":q_answers}

            questions_data.push(q_data)
        });
        $.ajax({
    url: "/plattform/edit/quiz/"+quiz_id,
    type: "POST",
    dataType: "json",
    data: JSON.stringify({questions:questions_data,module_id:module_id,quiz_name:quiz_name,quiz_id:quiz_id}),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: (data) => {
       if (data['error'])
       {
            alert(data['error']);
       }
      else{
            let url=data['redirect_to'];
            let redirect_url=window.location.origin+url
            window.location.href = redirect_url;
         }
    },
    error: (data) => {
    alert("Internal  server error!");
    }
  });
    }