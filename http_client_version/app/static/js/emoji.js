var input = document.querySelector('.emojiZone');
var messageBox = document.querySelector('.inputMessage');
var picker = new EmojiButton({
    position: 'left-start',
    style: 'twemoji'
})

picker.on('emoji', function (emoji) {
    var newEl = document.createElement('span');
    newEl.innerHTML = emoji;
    messageBox.appendChild(newEl);
    console.log(newEl)
})

input.addEventListener('click', function () {
    picker.pickerVisible ? picker.hidePicker() : picker.showPicker(input);

})