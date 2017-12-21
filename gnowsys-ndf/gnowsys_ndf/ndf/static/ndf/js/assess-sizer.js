'use strict';

$(document).ready(function() {

  window.addEventListener("message", function(event){
    var iframeCt = document.getElementsByTagName('iframe');
    var player = [];
    var iframeTrgt = [];
    var payload = JSON.parse(event.data);
    for (var i=0; i < iframeCt.length; i++) {
      iframeTrgt[i] = iframeCt[i].id;
      player = document.getElementById(iframeTrgt[i]);
      // var innerHT = document.getElementsByClassName('no-js');
      if(payload.height) {
        player.style.height = payload.height + 'px';
      }
    }
  }, false);

});

