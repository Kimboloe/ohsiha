
function test(song, artist) {
  console.log(song);
  var content = {'Song': song, 'Artist': artist};
  var doc = document.getElementById("lyrics-"+song.toString());
  var val = doc.innerText.toString();
  //var val = doc.options[doc.selectedIndex].text;
  console.log(val);

  if(val.includes("No lyrics loaded")){
    $.ajax({
      type: "GET",
      data: content,
      success: function(data){
        doc.innerText = "";
        doc.append(data);
      }
    });
  }
}


$(document).ready(() => {
    console.log("Ready?");

    $('#changeCountry').click(function(){
      var elem = document.getElementById("selected_country");
      var code = elem.options[elem.selectedIndex].value;
      var url = window.location.toString()
      var path_name = window.location.pathname.toString();
      var new_path = "/home/" + code.toString();
      var newUrl = url.replace(path_name, new_path);
      console.log(code," : ",path_name," : ", url, " : ", newUrl);
      window.location.assign(newUrl);
    });

    $('#charts').click(function() {
      var doc = document.getElementById("selected_country");
      var country_code = doc.options[doc.selectedIndex].value;
      console.log(country_code);
      var old_url = window.location.toString();
      var new_url = old_url.replace(window.location.pathname.toString(), "/charts/" + country_code.toString());
      window.location.assign(new_url);

    });

    $("#comment-form").submit(function(event) {

       /* stop form from submitting normally */
       event.preventDefault();

      var $inputs = $('#comment-form :input');

      var values = {};
      $inputs.each(function() {
        values[this.name] = $(this).val();
      });
       console.log(values);
       console.log(username);
       var name = username;
       var text = values["comment"];
       console.log(text)
       if(name == ""){
         name = "anonymous";
       }

       var message = {"messageType": "comment", "user": name, "comment": text};

       $.ajaxSetup({
          beforeSend: function(xhr, settings) {
             function getCookie(name) {
                 var cookieValue = null;
                 if (document.cookie && document.cookie != '') {
                     var cookies = document.cookie.split(';');
                     for (var i = 0; i < cookies.length; i++) {
                         var cookie = jQuery.trim(cookies[i]);
                         // Does this cookie string begin with the name we want?
                         if (cookie.substring(0, name.length + 1) == (name + '=')) {
                             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                             break;
                         }
                     }
                 }
                 return cookieValue;
             }
             if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                 // Only send the token to relative URLs i.e. locally.
                 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
             }
          }
        });
        $.ajax({
          url: window.location.pathname,
          type: "POST",
          data: JSON.stringify(message),
          contentType: 'application/json',
          success: function(data) {
            console.log(data);
            var doc = document.getElementById("comments");
            var h5 = document.createElement('h5');
            h5.appendChild(document.createTextNode(data));
            doc.append(h5);
          }
        });

     });

});
