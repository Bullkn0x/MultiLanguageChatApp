$('input#toggle--daynight').change(function(){
    if ($(this).is(':checked')) {
    document.documentElement.setAttribute('theme', 'light');
} else {
    document.documentElement.removeAttribute('theme');
}
});