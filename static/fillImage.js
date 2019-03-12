function readURL(input) {
    // document.getElementById("blah")[0].style="display:block";
    console.log(input)
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        $('#filenameLabel').html(input.files[0].name);
        localStorage.setItem('filename',input.files[0].name)
        reader.onload = function (e) {
            element = document.getElementById('blah').setAttribute('src',e.target.result);
            document.getElementById('blah').setAttribute('width',224);
            document.getElementById('blah').setAttribute('height',224);
            localStorage.setItem('previousImage',e.target.result)
        };

        reader.readAsDataURL(input.files[0]);
    }
}
window.onload=function(){
    previousImage = localStorage.getItem("previousImage")
    if(previousImage!=null){
        document.getElementById('blah').setAttribute('src',previousImage)
        document.getElementById('blah').setAttribute('width',224);
        document.getElementById('blah').setAttribute('height',224);
    }
}


function getText(){
    $.ajax({
        url:"get_text", //the page containing python script
        type: "post", //request type,
        dataType: 'json',
        data: {'filename' :localStorage.getItem('filename').toString()},
        success:function(result){
        console.log(result.text);
        $('#invoice').html(result.text);
              }
            });
}