
/* get the Modal */
function openModal(thisid){
  var modal = document.getElementById('myModal');
  //get the images
  var img1= document.getElementById(thisid.id);
  var modalImg = document.getElementById("img01"); //get modal image x
  var captionText = document.getElementById("caption");

  modal.style.display = "block";
  modalImg.src = thisid.src;
  captionText.innerHTML = thisid.alt;
  fg = document.getElementsByTagName("figcaption")
  for (var i=0; i< fg.length; i++){
    fg[i].style.display = "none";
  }
}



// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
console.log(span)

// When the user clicks on <span> (x), close the modal
function closemodal(thisid) { 
    var modal = document.getElementById('myModal');
    modal.style.display = "none";
    $('#myModal').trigger('reveal:close');
    fg = document.getElementsByTagName("figcaption")
    for (var i=0; i< fg.length; i++){
      fg[i].style.display = "block";
    }
}

