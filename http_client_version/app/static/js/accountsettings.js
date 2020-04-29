

//The password btn on the settings page
$passwordChange = $("#password");

//The temporary modal for the password change
$passwordModal = $("#changePasswordModal");

//The submit button for changing password
$passwordChangeSubmit = $("#confirmChangePassword");

//Values for the old and new password
$oldPassword =$('#oldPassword');
$newPassword =$('#newPassword');

//If password button is press, display the modal to change password
$passwordChange.on('click', function(){
    $passwordModal.css('display','flex');
});

$passwordChangeSubmit.on('click', function(){
    
    if ($oldPassword.val() && $newPassword.val()){
        
        var oldPassword = $oldPassword.val();
        var newPassword = $newPassword.val();
        socket.emit('change password', {
            "oldPassword": oldPassword,
            "newPassword": newPassword
        });
        $passwordModal.css('display','none');
    }
});

socket.on('password confirmation', function(data){
    //Tell user if the password change is successful or not
    alert(data);
});