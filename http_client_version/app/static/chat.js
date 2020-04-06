$(function() {
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];


  
  // Initialize varibles
  var $window = $(window);
  var $usernameInput = $('.usernameInput'); // Input for username
  var $messages = $('.messages'); // Messages area
  var $inputMessage = $('.inputMessage'); // Input message input box
  
  var $loginPage = $('.login.page'); // The login page
  var $chatPage = $('.chat.page'); // The chatroom page
  var $navBar = $('.navcontainer');
  var $onlineNumber = $('.online span');
  var $languagePref = $('#language');
  var $serverList = $('.serverList');
  var currentRoom; 
  var sideBarActive = false;
  // Prompt for setting a username
  var username;
  var connected = false;
  var typing = false;
  var lastTypingTime;
  var $currentInput = $usernameInput.focus();
  
  var socket = io.connect(null,  {
    port: 5000, 
    rememberTransport: false,
  });
  
  $('.online').click(function(){
    if (sideBarActive){
    $('.chatArea').animate({width:"100%"},350);
    $('.userList').animate({width:"0%"},350);

    sideBarActive =false
    }
    else {
      $('.chatArea').animate({width:"90%"},350);
      $('.userList').animate({width:"10%"},350);
      sideBarActive = true
    }
    
  })


  
  function updateOnline (data) {
    $('#onlineUsers').append('<li>'+data.username+'</li>');
    $onlineNumber.text(data.numUsers);
  }
  

  
  // DROPDOWN TOGGLE
    $('.dropdown-menu a').on('click', function(){    
      $('.dropdown-toggle').html($(this).html());
      changeLanguage();
  })  
  function changeLanguage () {
    var language = $languagePref.text().toLowerCase().trim();
    socket.emit('change language',language);
  }
  

// Handle ServerList Clicks
    $(".serverList").on('click', 'a', function(){
      joinRoom = $(this).text();
      joinRoomID = $(this).attr('roomid');
      console.log("You are Joining Room: " + joinRoom);
      socket.emit('join server',{
        "username": username,
        "roomID" : joinRoomID,
        "room" : joinRoom
      });

      log("You are chatting in "+ joinRoom, {
        prepend: true
      });

    });
  // Sends a chat message
  function sendMessage () {
    var message = $inputMessage.val();
    // Prevent markup from being injected into the message
    message = cleanInput(message);
    // if there is a non-empty message and a socket connection
    if (message && connected) {
      $inputMessage.val('');
      addChatMessage({
        username: username,
        message: message
      });
      // tell server to execute 'new message' and send along one parameter
      socket.emit('new message', message);
    }
  }

  // Log a message
  function log (message, options) {
    var $el = $('<li>').addClass('log').text(message);
    addMessageElement($el, options);
    
  }

  // Adds the visual chat message to the message list
  function addChatMessage (data, options) {
    // Don't fade the message in if there is an 'X was typing'
    var $typingMessages = getTypingMessages(data);
    options = options || {};
    if ($typingMessages.length !== 0) {
      options.fade = false;
      $typingMessages.remove();
    }
    var $usernameDiv = $('<span class="username"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));
    var $messageBodyDiv = $('<span class="messageBody">')
      .html(linkify(data.message));

    var typingClass = data.typing ? 'typing' : '';
    var $messageDiv = $('<li class="message"/>')
      .data('username', data.username)
      .addClass(typingClass)
      .append($usernameDiv, $messageBodyDiv);

    addMessageElement($messageDiv, options);
  }
  function linkify(inputText) {
    var replacedText, replacePattern1, replacePattern2, replacePattern3;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a id="link" href="http://$2" target="_blank">$2</a>');

    //Change email addresses to mailto:: links.
    replacePattern3 = /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
    replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

    return replacedText;
  }
  // Adds the visual chat typing message
  function addChatTyping (data) {
    data.typing = true;
    data.message = 'is typing';
    addChatMessage(data);
  }

  // Removes the visual chat typing message
  function removeChatTyping (data) {
    getTypingMessages(data).fadeOut(function () {
      $(this).remove();
    });
  }

  // Adds a message element to the messages and scrolls to the bottom
  // el - The element to add as a message
  // options.fade - If the element should fade-in (default = true)
  // options.prepend - If the element should prepend
  //   all other messages (default = false)
  function addMessageElement (el, options) {
    var $el = $(el);

    // Setup default options
    if (!options) {
      options = {};
    }
    if (typeof options.fade === 'undefined') {
      options.fade = true;
    }
    if (typeof options.prepend === 'undefined') {
      options.prepend = false;
    }

    // Apply options
    if (options.fade) {
      $el.hide().fadeIn(FADE_TIME);
    }
    if (options.prepend) {
      if ($messages.children('.log').length > 0) {
       $messages.children('.log').html($el);
    } else {
      $messages.prepend($el);
    } 
    } 
  
    else {
      $messages.append($el);
    }
    $messages[0].scrollTop = $messages[0].scrollHeight;
  }

  // Prevents input from having injected markup
  function cleanInput (input) {
    return $('<div/>').text(input).text();
  }

  // Updates the typing event
  function updateTyping () {
    if (connected) {
      if (!typing) {
        typing = true;
        socket.emit('typing');
      }
      lastTypingTime = (new Date()).getTime();

      setTimeout(function () {
        var typingTimer = (new Date()).getTime();
        var timeDiff = typingTimer - lastTypingTime;
        if (timeDiff >= TYPING_TIMER_LENGTH && typing) {
          socket.emit('stop typing');
          typing = false;
        }
      }, TYPING_TIMER_LENGTH);
    }
  }

  // Gets the 'X is typing' messages of a user
  function getTypingMessages (data) {
    return $('.typing.message').filter(function (i) {
      return $(this).data('username') === data.username;
    });
  }

  // Gets the color of a username through our hash function
  function getUsernameColor (username) {
    // Compute hash code
    var hash = 7;
    for (var i = 0; i < username.length; i++) {
       hash = username.charCodeAt(i) + (hash << 5) - hash;
    }
    // Calculate color
    var index = Math.abs(hash % COLORS.length);
    return COLORS[index];
  }

  // Keyboard events

  $window.keydown(function (event) {
    // Auto-focus the current input when a key is typed
    if (!(event.ctrlKey || event.metaKey || event.altKey)) {
      $currentInput.focus();
    }
    // When the client hits ENTER on their keyboard
    if (event.which === 13) {
      if (username) {
        sendMessage();
        socket.emit('stop typing');
        typing = false;
      } 
    }
  });

  $inputMessage.on('input', function() {
    updateTyping();
  });

//  FILE TRANSFER 
const chunk_size = 64 * 1024;
var files = [];
var dropzone = document.getElementById('dropzone');
dropzone.ondragover = function(e) {
  e.preventDefault();
}

document.addEventListener("dragenter", function( event ) {
  // highlight potential drop target when the draggable element enters it
  if ( event.target.id == "dropzone" ) {
      event.target.style.background = "red";
  }

}, false);
document.addEventListener("dragleave", function( event ) {
  // reset background of potential drop target when the draggable element leaves it
  if ( event.target.id == "dropzone" ) {
      event.target.style.background = "";
  }

}, false);
dropzone.ondrop = function(e) {
  e.preventDefault();
  for(var i = 0; i < e.dataTransfer.files.length; i++) {
      filediv = document.createElement('div');
      filename = document.createElement('div');
      filename.classList.add('filename');
      filename.innerHTML = e.dataTransfer.files[i].name;
      progress = document.createElement('div');
      progress.classList.add('file-progress');
      progress.classList.add('in-progress');
      filediv.appendChild(filename);
      filediv.appendChild(progress);
      document.getElementById('filelist').appendChild(filediv);
      files.push({
          file: e.dataTransfer.files[i],
          progress: progress,
          done: false
      });
  }
}
function readFileChunk(file, offset, length, success, error) {
  end_offset = offset + length;
  if (end_offset > file.size)
      end_offset = file.size;
  var r = new FileReader();
  r.onload = function(file, offset, length, e) {
      if (e.target.error != null)
          error(file, offset, length, e.target.error);
      else
          success(file, offset, length, e.target.result);
  }.bind(r, file, offset, length);
  r.readAsArrayBuffer(file.slice(offset, end_offset));
}

// read success callback
function onReadSuccess(file, offset, length, data) {
  if (this.done)
      return;
  if (!socket.connected) {
      // the WebSocket connection was lost, wait until it comes back
      setTimeout(onReadSuccess.bind(this, file, offset, length, data), 5000);
      return;
  }
  socket.emit('write-chunk', this.server_filename, offset, data, function(offset, ack) {
      if (!ack)
          onReadError(this.file, offset, 0, 'Transfer aborted by server')
  }.bind(this, offset));
  end_offset = offset + length;
  this.progress.style.width = parseInt(300 * end_offset / file.size) + "px";
  if (end_offset < file.size)
      readFileChunk(file, end_offset, chunk_size,
          onReadSuccess.bind(this),
          onReadError.bind(this));
  else {                        
      this.progress.classList.add('complete');
      this.progress.classList.remove('in-progress');
      this.done = true;
  }
}

// read error callback
function onReadError(file, offset, length, error) {
  console.log('Upload error for ' + file.name + ': ' + error);
  this.progress.classList.add('error');
  this.progress.classList.remove('in-progress');    
  this.done = true;
}

// upload button
var upload = document.getElementById('upload');
upload.onclick = function() {
  if (files.length == 0)
      alert('Drop some files above first!');
  for (var i = 0; i < files.length; i++) {
      socket.emit('start-transfer', files[i].file.name, files[i].file.size, function(filename) {
          if (!filename) {
              // the server rejected the transfer
              onReadError.call(this, this.file, 0, 0, 'Upload rejected by server')
          }
          else {
              // the server allowed the transfer with the given filename
              this.server_filename = filename;
              readFileChunk(this.file, 0, chunk_size,
                  onReadSuccess.bind(this),
                  onReadError.bind(this));
          }
      }.bind(files[i]));
  }
  files = [];
}



















  // Click events


  // Focus input when clicking on the message input's border
  $inputMessage.click(function () {
    $inputMessage.focus();
  });

  // Socket events
  function setUser(data) {
    username = data.username;
  }
  
  // Whenever the server emits 'connect', log the connect message
  socket.on('login', function (data) {
    connected = true;
    username = data.username
    // Display the welcome message
    var message = "Welcome to AnyChat :) ";
    log(message, {
      prepend: true
    });
    updateOnline(data);
  });

  // Whenever the server emits 'new message', update the chat body
  socket.on('new message', function (data) {
    console.log(data);
    addChatMessage(data);
  });

  // Whenever the server emits 'user joined', log it in the chat body
  socket.on('user joined', function (data) {
    log(data.username + ' joined');
    updateOnline(data);
  });

  // Whenever the server emits 'chat log' Append chat log to message box
  socket.on('chat log', function (messages) {
    $messages.html('');
    messages.forEach(function(data) {
      
      addChatMessage(data)
    });
    var message = "You have joined " + messages[0].room_name ;
    log(message, {
      prepend: true
    });
  });

  // Whenever the server emits 'stop typing', kill the typing message
  socket.on('server list', function (serverList) {
    // console.log(serverList)
    $serverList.html('')
    serverList.forEach(function(server) {
      var $imgDiv = $('<img />').attr("src", server.img_url).css({
        "max-height": "133%",
        "border-radius": "16%",
        "margin-right": "10px",
      })

      var $serverNameDiv = $('<span class="menu-collapsed"/>')
        .text(server.room_name);
      var $tableCellDiv =$('<a href="#" class="list-group-item list-group-item-action bg-dark text-white">').append($imgDiv).append($serverNameDiv);
      $serverList.append($tableCellDiv.attr('roomID',server.room_id));
    });
  });
  
  // Whenever the server emits 'user left', log it in the chat body
  socket.on('user left', function (data) {
    console.log(data);
    log(data.username + ' left');
    updateOnline(data);
    removeChatTyping(data);
  });

  // Whenever the server emits 'typing', show the typing message
  socket.on('typing', function (data) {
    addChatTyping(data);
  });

  // Whenever the server emits 'stop typing', kill the typing message
  socket.on('stop typing', function (data) {
    removeChatTyping(data);
  });
});




