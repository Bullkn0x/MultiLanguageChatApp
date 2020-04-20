 //  Modals
 var $discoverModal = $("#discoverModal");
 var $createModal= $("#newServerModal");
                            
 // Side Menu Selector for modals
 var $discoverBtn = $("#discoverServer");
 var $createBtn = $("#createServer");
 

  // When the user clicks the button, open the modal 
 $discoverBtn.on('click', function() {
    $discoverModal.css('display', "flex");
    $('#search-heading').addClass('animated fadeIn')
    $options.addClass('animated slideInDown delay-1s');
  });
 
 
  $$createBtn.on('click', function() {
     $createModal.css('display', "flex");
   });
   

//CREATE MODAL
var $createSubmit = $("#createServerSubmit");
var $serverName = $("#serverName");


 //As Soon as user click submit, exit the modal.

$createSubmit.on('click' , function(){
    if($serverName.val()){
        // $createModal.hide();
      // $serverName.clear();
      var room_name=$serverName.val();
      var public = $('#_checkbox').is(":not(:checked)")
      socket.emit('create server', {
        room_name:room_name,
        public:public
      });
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

