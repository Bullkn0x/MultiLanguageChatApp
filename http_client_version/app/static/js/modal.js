//CREATE MODAL
var $createSubmit = $("#createServerSubmit");
var $serverName = $("#serverName");

$createBtn.on('click', function() {
  $createModal.css('display', "flex");
});


 //As Soon as user click submit, exit the modal and submit.
$createSubmit.click( function(){
    if($serverName.val()){
        // $createModal.hide();
      // $serverName.clear();
      var room_name=$serverName.val();
      var public = $('#_checkbox').is(":not(:checked)")
      socket.emit('create server', {
        room_name:room_name,
        public:public
      });
      $createModal.hide();
    }
    
  });

$serverName.keypress(function(e){
  if (e.which==13){
    $createSubmit.click(); 
  }
});

// SEARCH MODAL
var $options = $('.search-options');

 

 // When the user clicks off the modal, close it
 $(".modal").click( function(e) {
    if(e.target == e.currentTarget) {
        $(this).hide();
    }
});

