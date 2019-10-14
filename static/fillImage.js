function readURL(input) {
    // document.getElementById("blah")[0].style="display:block";
    console.log(input)
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        $('#filenameLabel').html(input.files[0].name);
        localStorage.setItem('filename',input.files[0].name);
        reader.onload = function (e) {
            element = document.getElementById('blah').setAttribute('src',e.target.result);
            document.getElementById('blah').setAttribute('width',224);
            document.getElementById('blah').setAttribute('height',224);
        };

        reader.readAsDataURL(input.files[0]);
    }
}


function getText(){
  
}

function showLoadingBar(){
    $.busyLoadFull("show", {
        animation: "fade",
        spinner: "cube",
        text : "Predicting ...",
        textPosition : "left"
    });
}
function hideLoadingBar(){
    $.busyLoadFull("hide", {
        animation: "fade",
    });
}
$(function() {
    $('#predictImage').click(function() {
        if($("#upload_file")[0].files[0]!=null){     
            showLoadingBar();
            var form = $('#documentForm')[0];
            var form_data = new FormData(form);
            $.ajax({
                type: 'POST',
                url: '/predictImage',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $('#imageType').html(data["type"]);
                    hideLoadingBar();
                    $('#documentContent').css("visibility","visible");
                    $('#heading').css('color','green');
                    $("#type").html('Document')
                    $('#myModal').modal('show');
               },
            });
        }
        else{
            $('#imageType').html("Please upload the file before submitting");
            $('#heading').css('color','red');
            $('#myModal').modal('show');
        }

    });
});


$(function() {
    $('#getText').click(function(){
        var form = $('#documentForm')[0];
        var form_data = new FormData(form);

        if($("#upload_file")[0].files[0]!=null){     
            $.busyLoadFull("show", {});
            
        $.ajax({
            url:"/get_text", //the page containing python script
            type: "POST", //request type,
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success:function(result){
            console.log(result.text);
            $.busyLoadFull("hide", {
                animation:"fade",
                spinner :"cube",
                text : "Extracting text ..",
                textPosition : "left"
            });
            $('#myModal').modal('show');
            $('#imageType').html(result.text);
            $("#type").html('text')
                },
            error : function(error){
                $.busyLoadFull("hide", {
                    animation:"fade",
                });
               }
            });
        }
    });
});
$(function(){
    $('#predictSentimentBtn').click(function(){
    showLoadingBar();
    var form = $('#documentForm')[0];
    var form_data = new FormData(form);
    $.ajax({
        type: 'POST',
        url: '/predictSentiment',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            console.log(JSON.parse(data));
            data= JSON.parse(data);
            score = data["score"]
            $('#imageType').html(data["predictedText"]+" and    score is "+score);
            hideLoadingBar();
            $('#documentContent').css("visibility","visible");
            $('#heading').css('color','green');
            $("#type").html('Text')
            $('#myModal').modal('show');
            },
    });
})
})