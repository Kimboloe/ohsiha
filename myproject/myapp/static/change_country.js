
var event = new Event('lyrics');

window.addEventListener('lyrics', e => handleEvent(e));

function test(song, artist) {
  console.log(song);
  var content = {'Song': song, 'Artist': artist};
  $.ajax({
    type: "GET",
    data: content,
    success: function(data){
      document.getElementById(song).append(data);
    }
  });
}

const handleEvent = e => {
  data = e.data;
  $.ajax({
    type: "GET",
    data: data,
    success: function(data){
      console.log(data);
    }
  });

}

$(document).ready(() => {
    console.log("Ready?");
    $('#changeCountry').click(function() {
      var doc = document.getElementById("selected_country");
      var country_code = doc.options[doc.selectedIndex].value;
      console.log(country_code);
      $.ajax({
        type: "GET",
        data: country_code,
        success: function(data){
          console.log(data);
        }
      });
    }
    );
});
