/*
For annotation based discussions:
*/

// var annotations = "{{ annotations | safe}}";
var currentUser = null;
var  existingComments = [];
var SideComments = require('side-comments');
var sideComments;
var flag = false; 
var pos=-1;
var st = null;
var initialText;
var toggleValue = 1;
var moving_divInitialX;
var moving_divInitialY;

if(!window.win){
  win = {};
}
win.Selector = {};
win.Selector.getSelected = function()
{
    var t = '';
    if(window.getSelection)             //For firefox
    {
      t = window.getSelection();
    }
    else if(document.getSelection)
    {
      t = document.getSelection();
    }
    else if(document.selection)         //For IE
    {
      t = document.selection.createRange().text;
    }
    return t;
}

win.Selector.mouseup = function(e)
{
  /*
   * Called on a mouseup event. 
   * Tweaks selection to include entire words automatically.
   * Further, if the selection is not null, 
   *                      if the annotate mode is enabled, one can add annotations.
   *                      if annotate mode is disabled, the anotate icon appears, by clicking on which one may switch to the annotate mode. 
  */
  var obj = win.Selector.getSelected();
  st = String(obj);
  prevSel = "";
  var selectionRange = obj.getRangeAt(0);
  var startVal = selectionRange.startOffset; 
  expand(selectionRange);
  var selection = selectionRange.toString();
  if(selection && (selection = new String(selection).replace(/^\s+|\s+$/g,''))) 
  {
      st = selection;
      st = st.trim();
  } 
  
  //console.log("stout: " + st)
  st = st.trim();
  if (st)
  {
     //if selection is not empty
      if (toggleValue == 1)
      {
             //if discussion mode is already enabled, create a new side-comments object 
             highlightSearchTerms(st);
             existingComments = [];
             sideComments = new SideComments('#commentable-area', currentUser, existingComments);
             $('.marker').trigger('click');   
      }
      
      else if (toggleValue == -1)
      {
            //if discussion mode is not enabled, show annotate icon. 
            if (st != prevSel) 
            {
                //console.log("show menu");
                $('#moving_div').css({
                   left:  e.pageX - 320,
                   top:   e.pageY - 60,
                   display: "block"
                }).delay(5000).fadeOut(4000);
            }
            else 
            {
                //console.log("hide menu");
                $('#moving_div').css({
                     display: "none"
                });
            }
            prevSel = st;
      }
  }
  else
  {
            //console.log("hide menu");
            $('#moving_div').css({
                 display: "none"
            });
  }
}


function switchMode()
{
    /*To switch to annotate mode when some text is selected*/
    toggle(document.getElementById("toggleContainer"));
    //console.log("st inside switchMode: " + st);
    highlightSearchTerms(st);
    existingComments = [];
    sideComments = new SideComments('#commentable-area', currentUser, existingComments);
    $('.marker').trigger('click');   
    $('.marker').trigger('click');   
}

function expand(range) 
{
    /*helper function to expand the selection range to incude whole words */
    if (range.collapsed) {
        return;
    }

    while (range.toString()[0].match(/\w/)) {
        range.setStart(range.startContainer, range.startOffset - 1);   
    }

    while (range.toString()[range.toString().length - 1].match(/\w/)) {
        range.setEnd(range.endContainer, range.endOffset + 1);
    }
}

// $(document).ready(function(){
//   initialText = $("#content").html();
//   $("#content").bind("mouseup", win.Selector.mouseup);

//   // For topic node landing page concept svg graph
//   svgdata = $('#chart-concept svg');
//   alert(svgdata)
//   $('#view-graph').append(svgdata);
// });

{% if user.is_authenticated %}
  currentUser=
  {
      id: {{ user.id }},
      avatarUrl: "/static/ndf/images/user.png",
      name: '{{ user.username }}'
  };
{% endif %}

// Create a new SideComments instance, passing in the wrapper element and the optional the current user and any existing comments.
sideComments = new SideComments('#commentable-area', currentUser, existingComments);
//Listen to 'commentPosted'
sideComments.on('commentPosted', function( comment ) 
{
    if(st)
    {
     $.ajax({
            url: "{% url 'annotationlibInSelText' groupid %}",
            type: 'POST',
            datatype : "JSON",
            data: 
            {
                comment      : JSON.stringify(comment),
                selectedText : st,
                node_id      : '{{ node }}', 
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function( updatedAnnotationsField ) 
            {
              // Once the comment is saved, insert the comment into the comment stream with "insertComment(comment)".
              //highlight this selection
              //update the local annotations variable
              //console.log("Inside success: Comment added!");
              sideComments.insertComment(comment);
              highlightSearchTerms(st);
              annotations = jQuery.parseJSON(updatedAnnotationsField);
            }
          });
    }
    else
    {
      //Alert user to select text
      $("#alertSelText").foundation('reveal', 'open');
    }
}); 
  
sideComments.on('addCommentAttempted', function() 
{  
    //Alert user to sign in to add comments!
    $("#alertSignIn").foundation('reveal', 'open');
});

//Listen to "commentDeleted" and send a request to backend to delete the comment.
/*sideComments.on('commentDeleted', function( commentId ) 
{
    //console.log("entered del func")
    $.ajax({
            url: "{% url 'delComment' groupid %}",
            success: function( success ) {
            alert(commentId);
            }
           });
});*/

toggle(document.getElementById("toggleContainer"));

function showThread(elem)
{
  /*Parses the local copy of annotations field to load comments about the annotated text that was clicked on */
  text = $(elem).text();
  existingComments = [];
  st = String(text);
  //console.log("You clicked on: " + st);
  for (i = 0; i < annotations.length; i++)
  {
      if(String(text).toLowerCase() == annotations[i].selectedText.toLowerCase())
      {
        existingComments.push(annotations[i]);
        //console.log("existingComments" + existingComments[0]['comments'][0]['comment']);
        sideComments = new SideComments('#commentable-area', currentUser, existingComments); 
        break;
      }
  }
  //trigger clicks so that discussions are visible as soon as an annotated text is clicked on
  $('.marker').trigger('click');   
  $('.marker').trigger('click');       

}


/*
 * This is the function that highlights a text string by adding HTML tags before and after all occurrences of the search term. 
 * Cant use a regular expression search, because we want to filter out matches that occur within HTML tags and script blocks. 
 * so we do a little extra validation.
 * Moreover, it optimises the searching in the sense that it ensures whole words are highlighted by checking the characters before after the serach term's occurrence in the body text by a regular expression match. 
 * So if the search term is 'comment', it wont highlight 'comments'
 */
function high(bodyText, searchText)
{
  highlightStartTag = "<span class = 'annotatedElement' onclick = 'if(event.stopPropagation){event.stopPropagation();}else if(window.event){event.cancelBubble=true;} showThread(this);  '>";
  highlightEndTag = "</span>";
  var newText = "";
  i = -1;
  var charCheck = /[a-z]/;
  var lcSearchTerm = searchText.toLowerCase();
  var lcBodyText = bodyText.toLowerCase();
  var cur;
  var next;
  var inter;
  lcBodyTextLength = lcBodyText.length;
  oneWord = false;
  //console.log("lcSearchTerm: " + lcSearchTerm);
  // console.log("lcBodyText: " + lcBodyText);
  arr = lcSearchTerm.split(" ");
  noOfWords = arr.length;

  if (noOfWords == 1)
  {
    oneWord = true;
  }

  while (bodyText.length > 0) 
  {
    
            if (oneWord)
            {
                i = lcBodyText.indexOf(arr[0], i+1);
            }
            else
            {
                i = lcBodyText.indexOf(arr[0] + " ", i+1);
            }
            
            //validation for i
            if(i>0 && charCheck.test(lcBodyText.charAt(i-1)))
            {
                continue;
            }

            if(i>=0 && (!oneWord || (i+arr[0].length < lcBodyTextLength)) && charCheck.test(lcBodyText.charAt(i+arr[0].length)))
            {
                continue;
            }

  
    start = i;
    //console.log("start value:   " + start);
    if (i < 0) 
    {
      newText += bodyText;
      bodyText = "";
    } 
    else 
    { 
          if(bodyText.lastIndexOf(">", i) >= bodyText.lastIndexOf("<", i))
          {
            //exclude everything inside HTML tags
                  if(lcBodyText.lastIndexOf("/script>", i) >= lcBodyText.lastIndexOf("<script", i) )
                  {
                        //exclude everything inside script tags
                        next = i;
                        cur = next;
                        for (k = 0; k < noOfWords -1; k++)
                        {
                          next = lcBodyText.indexOf(arr[k+1], cur+1);
                          //validation for next
                          if (next+arr[k+1].length < lcBodyTextLength &&  charCheck.test(lcBodyText.charAt(next+arr[k+1].length)))
                          {
                            break;
                          }
                          inter = lcBodyText.substring(cur+arr[k].length, next);
                          inter = inter.trim();
                          if(inter == "" || (inter[0] == '<' && inter[inter.length-1] == '>'))
                          {
                            cur = next;
                            continue;
                          }
                          break;
                        }

                        if (k == noOfWords -1)
                        {
                          //all words matched
                          newText += bodyText.substring(0, start) + highlightStartTag + bodyText.substring(start, next+arr[noOfWords-1].length ) + highlightEndTag;
                          bodyText = bodyText.substr( next+arr[noOfWords-1].length );
                          lcBodyText = bodyText.toLowerCase();
                          i = -1;
                        }
                   }
           }
    }
  }

  return newText;
}


/*
 * This is a wrapper function to the high function.
 * It takes the searchText that you pass and transforms the text on the current web page.
 * The "searchText" parameter is required
 */
function highlightSearchTerms(searchText)
{
  // search string so that each word is searched for and highlighted individually
  var bodyText = $("#content").html();
  //alert("inside highlightSearchTerms" + searchText);
  bodyText = high(bodyText, searchText);
  $("#content").html(bodyText);
  return true;
}

/*
script for marking up the annotated text
*/
function highlightAll()
{

  for (p = 0; p < annotations.length; p++)
  {
     t = annotations[p].selectedText;
     highlightSearchTerms(t);
     //alert("inside highlightAll: " + t);
  }

}


/*
*Function to switch between the enable and disable discussion modes. 
*Takes the toggleContainer icon as a parameter to toggle it's contents.
*Uses a flag 'toggleValue (1 or -1)' to keep track of present mode and multiply by -1 each time the function is called.
*If annotate mode is enabled, it hides the side-comments, loads the initial text that had no highlights and toggles the icon.
*If annotate mode is disabled, it shows the side-comments, highlights all annotated text, hides the menu and toggles the icon.
*/
function toggle(el)
{
  // console.log("toggleClass at beginning: " + toggleValue);
  if (toggleValue == 1)
   {
         //Disable annotations
         $(".side-comment").hide();
         $("#content").html(initialText);
         el.innerHTML = '<i class="fi-comments annotateIcon"></i> Annotate';
   }  
  
  else if (toggleValue == -1)
  {     
        //enable annotations
        $(".side-comment").show();
        highlightAll(); 
        el.innerHTML = '<i class="fi-clipboard-pencil annotateIcon"></i> Annotate';
        // console.log("hide menu");
        $('#moving_div').css({
             display: "none"
        });
  }

  toggleValue *= -1;
  // console.log("toggleClass at end: " + toggleValue);
}

function getPosition(element) {
    var xPosition = 0;
    var yPosition = 0;
  
    while(element) {
        xPosition += (element.offsetLeft - element.scrollLeft + element.clientLeft);
        yPosition += (element.offsetTop - element.scrollTop + element.clientTop);
        element = element.offsetParent;
    }
    return { x: xPosition, y: yPosition };
}
