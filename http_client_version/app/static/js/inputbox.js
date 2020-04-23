var flag = 0;

$(".toolsButton").on('click',function(){
  if(flag == 0){
    on();
    flag = 1;
  }else{
    off();
    flag = 0;
  }
});

function on(){
  $('input').addClass('rotate-input');
  $('.toolsButton').addClass('toolsButton-rotate');
  $('.tools').addClass('tools-rotate');
}

function off(){
  $('input').removeClass('rotate-input');
  $('.toolsButton').removeClass('button-rotate');
  $('.tools').removeClass('tools-rotate');
}