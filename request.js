var disp;
var dispCtx;
var im;
var ws;

function doLoad() {
    disp = document.getElementById("display");
    dispCtx = disp.getContext("2d");
    im = new Image();
    im.onload = function() {
    disp.setAttribute("width", im.width);
    disp.setAttribute("height", im.height);
    dispCtx.drawImage(this, 0, 0);
  };
    im.src = "img/img_not_found.png";
    ws = new WebSocket("ws://127.0.0.1:50007");
    ws.onmessage = function (evt) {
        im.src = "data:image/png;base64," + evt.data;
    }
}