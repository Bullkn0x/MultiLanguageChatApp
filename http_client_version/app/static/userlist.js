$(document).ready(function() {

    var $svg = $(".sidebar"),
        $demo = $(".usersOnline"),
        $path = $(".s-path"),
        $sCont = $(".sidebar-content"),
        $chat = $(".chats"),
        demoTop = $demo.offset().top,
        demoLeft = $demo.offset().left,
        diffX = 0,
        curX = 0,
        finalX = 0,
        frame = 1000 / 60,
        animTime = 600,
        sContTrans = 200,
        animating = false;
    console.log(demoLeft);
    var easings = {
      smallElastic: function(t,b,c,d) {
        var ts = (t/=d)*t;
        var tc = ts*t;
        return b+c*(33*tc*ts + -106*ts*ts + 126*tc + -67*ts + 15*t);
      },
      inCubic: function(t,b,c,d) {
        var tc = (t/=d)*t*t;
        return b+c*(tc);
      }
    };
  
    function createD(top, ax, dir) {
      return "M0,0 "+top+",0 a"+ax+",250 0 1,"+dir+" 0,500 L0,500";
    }
  
    var startD = createD(50,0,1),
        midD = createD(125,75,0),
        finalD = createD(200,0,1),
        clickMidD = createD(300,80,0),
        clickMidDRev = createD(200,100,1),
        clickD = createD(300,0,1),
        currentPath = startD;
  
    function newD(num1, num2) {
      var d = $path.attr("d"),
          num2 = num2 || 250,
          nd = d.replace(/\ba(\d+),(\d+)\b/gi, "a" + num1 + "," + num2);
      return nd;
    }
  
    function animatePathD(path, d, time, handlers, callback, easingTop, easingX) {
      var steps = Math.floor(time / frame),
          curStep = 0,
          oldArr = currentPath.split(" "),
          newArr = d.split(" "),
          oldLen = oldArr.length,
          newLen = newArr.length,
          oldTop = +oldArr[1].split(",")[0],
          topDiff = +newArr[1].split(",")[0] - oldTop,
          nextTop,
          nextX,
          easingTop = easings[easingTop] || easings.smallElastic,
          easingX = easings[easingX] || easingTop;
  
      $(document).off("mousedown mouseup");
  
      function animate() {
        curStep++;
        nextTop = easingTop(curStep, oldTop, topDiff, steps);
        nextX = easingX(curStep, curX, finalX-curX, steps);
        oldArr[1] = nextTop + ",0";
        oldArr[2] = "a" + Math.abs(nextX) + ",250";
        oldArr[4] = (nextX >= 0) ? "1,1" : "1,0";
        $path.attr("d", oldArr.join(" "));
        if (curStep > steps) {
          curX = 0;
          diffX = 0;
          $path.attr("d", d);
          currentPath = d;
          if (callback) callback();
          return;
        }
        requestAnimationFrame(animate);
      }
      animate();
    }

  
    function closeSidebar(e) {
      if ($(e.target).closest(".sidebar-content").length ||
          $(e.target).closest(".chats").length) return;
      if (animating) return;
      animating = true;
      $sCont.removeClass("active");
      $chat.removeClass("active");
      $(".cloned").addClass("removed");
      finalX = -75;
      setTimeout(function() {
        animatePathD($path, midD, animTime/3, false, function() {
          $chat.hide();
          $(".cloned").remove();
          finalX = 0;
          curX = -75;
          animatePathD($path, startD, animTime/3*2, true);
          animating = false;
        }, "inCubic");
      }, sContTrans);
      $(document).off("click", closeSidebar);
    }
  
    function moveImage(that) {
      var $img = $(that).find(".contact__photo"),
          top = $img.offset().top - demoTop,
          left = $img.offset().left - demoLeft,
          $clone = $img.clone().addClass("cloned");
  
      $('.chats').prepend($clone);
    }
  
    function ripple(elem, e) {
      var elTop = elem.offset().top,
          elLeft = elem.offset().left,
          x = e.pageX - elLeft,
          y = e.pageY - elTop;
      var $ripple = $("<div class='ripple'></div>");
      $ripple.css({top: y, left: x});
      elem.append($ripple);
    }
  
    $(document).on("click", ".contact", function(e) {
      var that = this,
          name = $(this).find(".contact__name").text(),
          online = $(this).find(".contact__status").hasClass("online");
      $(".chats__name").text(name);
      $(".chats__online");
      if (online) $(".chats__online").addClass("active");
      ripple($(that),e);
      setTimeout(function() {
        $sCont.removeClass("active");
        finalX = -80;
        setTimeout(function() {
          $(".ripple").remove();
          animatePathD($path, clickMidD, animTime/3, false, function() {
            curX = -80;
            finalX = 0;
            animatePathD($path, clickD, animTime*2/3, true, function() {
              $chat.show();
              $chat.css("top");
              $chat.addClass("active");
              animating = false;
              if ($('div.chats.active > img').length){
                $('div.chats.active > img').remove(); 
              }
              moveImage(that);
            });
          }, "inCubic");
        }, sContTrans);
      }, sContTrans);
    });
  
    $(document).on("click", ".chats__back", function() {
      if (animating) return;
      animating = true;
      $chat.removeClass("active");
      $(".cloned").addClass("removed");
      setTimeout(function() {
        $(".cloned").remove();
        $chat.hide();
        animatePathD($path, clickMidDRev, animTime/3, false, function() {
          curX = 100;
          finalX = 0;
          animatePathD($path, finalD, animTime*2/3, true, function() {
            $sCont.addClass("active");
            $(document).on("click", closeSidebar);
            animating = false;
          });
        }, "inCubic");
      }, sContTrans);
    });
  
    $(window).on("resize", function() {
    });
  
  });