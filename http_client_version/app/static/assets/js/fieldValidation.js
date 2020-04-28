var emailInput = document.getElementById("inputEmail3");
var emailHeader = document.getElementById("emailHeader");
var usernameHeader = document.getElementById("usernameHeader");
emailInput.onkeyup = function(){
    if (emailInput.value.includes('@')) {
    emailHeader.style.fontWeight ='700';
    emailHeader.style.borderBottom ='solid';
    usernameHeader.removeAttribute("style");
    
    } else {
    usernameHeader.style.fontWeight ='700';
    usernameHeader.style.borderBottom ='solid';
    emailHeader.removeAttribute("style");
    }
}