function removeItem(id){
var item = "#" + id
$(item).remove();

}

function removeAnswer(obj)
{
$(obj).closest(".answer").remove()
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

    var counter=1;
    var ans_counter=1;

    function addAnswer(question_id)
    {



        var payload=`[data-question='${question_id}']`;
        var answer_id="answer_"+ans_counter;


        var answer_html=`

        <div class="answer" id="${answer_id}" style="margin:10px;">
        Answer
        <input  name="answer_text" class="uui-form_input-2 w-input" type="text">
         Correct? <input name="is_correct" type="checkbox" style="margin-right:50px;"><button onclick="removeItem('${answer_id}')"> <i class="icon-trash" style="font-size:2rem"></i></button>
        </div>

        `


        var answer_field=`

        <div  class="answer" id="${answer_id}" >
        <br>
        <label>Answer</label>
        <input name="answer_text" type="text">
        <label>Is correct?</label>
        <input name="is_correct" type="checkbox">
        <button onclick="removeItem('${answer_id}')" style="border:none;background:white;"><i class="fa fa-close" style="color: #d30202;"></i></button>
        <br>
        </div>

        `;
        ans_counter++;
        $(payload).find(".combine-faq1_answer-2").append(answer_html);
    }

    function addQuestion()
    {
        var id=`question_${counter}`



        var question_html=`
<div  class="combine-faq1_accordion-2 question" data-question=${counter} id="${id}">
                <div class="combine-faq1_question-2">
                  <div class="combine-faq1_expander-2">
                    <div class="combine-icon_color4-3">
                      <div class="combine-icon_small-3 w-embed" onclick="ShowHide('${id}')">
                        <svg  viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <g clip-path="url(#clip0_677_666)">
                            <path d="M8 1.77777V14.2222" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M1.77783 8H14.2223" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                          </g>
                          <defs>
                            <clipPath id="clip0_677_666">
                              <rect width="16" height="16" fill="currentColor" />
                            </clipPath>
                          </defs>
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div class="uui-form_input-2 w-input" style="border:none;background-color:#f2f3f7"><h2>Question  </h2> <input style="width:100%" name="question_text"  class="uui-form_input-2 w-input" type="text"></div>
                </div>
                <div class="combine-faq1_answer-2" >
                  <p class="combine-text-size-regular-9">

                    <button class="uui-button-4 w-button" style="display:inline-block" onclick="addAnswer(${counter})">Add answer</button>
                    <button class="uui-button-4 w-button" style="display:inline-block; border:#ba2b2b;background-color:#ba2b2b" onclick="removeItem('${id}')">  Delete question <i class="icon-trash" style="font-size:1rem"></i></button><br>


                  </p>
                  <div class="combine-space-medium-7"></div>
                </div>

        `

        var question=`
            <div class="question" data-question=${counter} id="${id}">
            <hr>
            <label for="question_${counter}">Question</label>
            <input name="question_text" type="text" >
            <button class="btn btn-warning" onclick="addAnswer(${counter})">Add answer</button>
            <button class="btn btn-danger"  onclick="removeItem('${id}')">Remove question</button>
            <br>
            </div>



        `;
        $("#questions").append(question_html);
        counter++;

    }

    function Create()
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
    url: "/plattform/create/quiz/",
    type: "POST",
    dataType: "json",
    data: JSON.stringify({questions:questions_data,module_id:module_id,quiz_name:quiz_name}),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: (data) => {
       if (data['error'])
       {
            console.log($("#error"))
            $("#error").html(data['error']);
      $('#myModal').modal("show");
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

function ShowHide(question_id){

    var  id ="#"+question_id

    if ($(id).find(".combine-faq1_answer-2").is(":visible"))
    {

      $(id).find(".combine-faq1_answer-2").css({"display":"none"})

    }
    else{
    $(id).find(".combine-faq1_answer-2").css({"display":"block"})
    }


    }
