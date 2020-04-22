 //  Modals
 var $discoverModal = $("#discoverModal");
 var $createModal= $("#newServerModal");
 var $leaveModal = $("#leaveConfirmModal"); 
 var $serverOptionModal = $("serverOptionModal");

 // Side Menu Selector for modals
 var $discoverBtn = $("#discoverServer");
 var $createBtn = $("#createServer");

  //temporary help button'
 var $helpBtn = $("#help");


// When the user clicks the button, open the modal 
$discoverBtn.on('click', function() {
  $discoverModal.css('display', "flex");
  $('#search-heading').addClass('animated fadeIn')
  $options.addClass('animated slideInDown delay-1s');
});


//Leave Server Modal AREA ------------
//Temp button to bring up the modal
$helpBtn.on('click', function(){
  $leaveModal.css('display', 'flex');
});
//Gets the cancel button and hide the modal if cancel is pressed.
var $leaveServerCancel = $('cancelLeave');
//Function is not working for some reason....
$leaveServerCancel.on('click', function(){
  // $leaveModal.css('display', 'none');
  $leaveModal.hide();
  // $('.modal').css('display', 'none');
});




//When right click on all the servers on the serverList... Do something HERE...
//Currently Returns the text and room_id of which ever you click on
//(Think of a way to use the information and pass the arguments)
$(document).on("contextmenu", ".your-server", function(e){
    alert($(this).text());
    alert($(this).attr('room_id'));
    $(this).on()
    $serverOptionModal.css('display', "flex");

    return false;
 });

 
//CREATE MODAL
var $createSubmit = $("#createServerSubmit");
var $serverName = $("#serverName");

$createBtn.on('click', function() {
  $createModal.css('display', "flex");
});
 //As Soon as user click submit, exit the modal.

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

