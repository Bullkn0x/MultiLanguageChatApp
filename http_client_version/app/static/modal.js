 // Get the modal
 var $modal = $("#myModal");
                            
 // Get the button that opens the modal
 var $btn = $(".addServer");
 
 // Get the <span> element that closes the modal
 var span = $("close")[0];
 
 var $options = $('.search-options');
 // When the user clicks the button, open the modal 
 $btn.on('click', function() {
   $modal.css('display', "flex");
   $('#search-heading').addClass('animated fadeIn')
   $options.addClass('animated slideInDown delay-1s');
 });
 
 // When the user clicks on <span> (x), close the modal
 $("#myModal").click( function(e) {
    if(e.target == e.currentTarget) {
        $modal.css('display', "none");
    }
});

