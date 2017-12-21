/**
 * MobWrite - Real-time Synchronization and Collaboration Service
 *
 * Copyright 2006 Google Inc.
 * http://code.google.com/p/google-mobwrite/
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview This client-side code interfaces with the rich-text iframe(s).
 * @author fraser@google.com (Neil Fraser)
 */


/**
 * Constructor of shared object representing an editable iframe.
 * @param {Node} doc The document node of an editable iframe
 * @param {string} id Unique file ID
 * @constructor
 */
mobwrite.shareIframeObj = function(doc, id) {
  // Call our prototype's constructor.
  mobwrite.shareObj.apply(this, [id]);

  this.doc = doc;
  // Initialise the iframe (clear any browser cache).
  if (doc) {
    this.setClientText('');
  }
  // Don't highlight incoming text on the first update.
  this.firstEdit = true;
};


// The iframe shared object's parent is a shareObj.
mobwrite.shareIframeObj.prototype = new mobwrite.shareObj('');


/**
 * When local or remote changes arrive, should the affected line(s) be recoloured?
 * @type {boolean}
 */
mobwrite.shareIframeObj.prototype.decolourChanges = true;


/**
 * Temporary icon be displayed when text is deleted.  Set to '' to disable.
 * @type {string}
 */
mobwrite.shareIframeObj.prototype.zapIcon = '/static/img/zap.gif';
if (!mobwrite.UA_msie) {
  // Base 64 encoded copy of zap.gif.  Eliminates one server-request.  Not supported by IE 5-7.
  mobwrite.shareIframeObj.prototype.zapIcon = 'data:;base64,R0lGODlhCAAIAMQAAAAAAAICAQYGAhMTCBUVCCAgDSEhDUdHHE9PIF9fJmpqKnFxLXR0Lnd3MICAM6mpRLi4Sru7S9DQU9fXVtzcWN3dWOLiWunpXfLyYfz8Zf7+Zv//Zv///////////////yH5BAkAABsALAAAAAAIAAgAAAgzADcIHLjhwcALAhdEEIjBQAUFBwY2ADAggASBFAQUAJBgIAIGFwhYEBjBgcAJAyEQHBgQAA==';
}

/**
 * How long to display the zap icon.
 * Must be less than mobwrite.minSyncInterval
 * @type {number}
 */
mobwrite.shareIframeObj.prototype.zapIconTime = 999;


/**
 * How long to display highlighting.
 * @type {number}
 */
mobwrite.shareIframeObj.prototype.highlightTime = 2000;


/**
 * Name of attribute used to keep track of character index.
 * @type {string}
 */
mobwrite.shareIframeObj.charIndexAttribute = 'mobwriteCharIndex';


/**
 * Name of attribute used to keep track of how many characters this node
 * generates before any contents.  e.g. BR, DIV and P would _usually_ be 2.
 * @type {string}
 */
mobwrite.shareIframeObj.charAddAttribute = 'mobwriteCharAdd';


/**
 * Dodge an 'Access is denied' error in IE.  Fetch the document again.
 * @private
 */
mobwrite.shareIframeObj.prototype.resetDocument_ = function() {
  if (mobwrite.UA_msie) {
    var el = window.frames[this.file];
    el = el.document;
    this.doc = el;
  }
};


/**
 * Retrieve the user's HTML.
 * @return {string} HTML content.
 */
mobwrite.shareIframeObj.prototype.getClientHtml = function() {
  return this.doc.body.innerHTML;
};


/**
 * Set the user's HTML directly.
 * @param {string} html New HTML
 */
mobwrite.shareIframeObj.prototype.setClientHtml = function(html) {
  if (this.firstEdit) {
    this.resetDocument_();
  }
  this.doc.body.innerHTML = html;
  this.firstEdit = false;
};


/**
 * Retrieve the user's text.  Converts the HTML into text.
 * @return {string} Plaintext content
 */
mobwrite.shareIframeObj.prototype.getClientText = function() {
  if (this.firstEdit) {
    this.resetDocument_();
  }
  // Convert the DOM to plaintext, and add indexing markers for future use.
  var text = mobwrite.shareIframeObj.domToText_(this.doc.body);

  // Some browsers add a trailing BR.
  if ((mobwrite.UA_gecko || mobwrite.UA_opera) &&
      text.length && text.charAt(text.length - 1) == '\n') {
    text = text.substring(0, text.length - 1);
  }
  //if (text) alert('Get: ' + escape(text));
  return text;
};


/**
 * Convert the text into HTML compatible for this browser.
 * Set the resulting HTML as the user's content.
 * @param {string} value New text
 */
mobwrite.shareIframeObj.prototype.setClientText = function(value) {
  value = value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  value = mobwrite.shareIframeObj.spaceToNbsp_(value);
  if (mobwrite.UA_webkit) {
    // Safari uses DIVs to separate lines and a classed BR on blank lines.
    lines = value.split('\n');
    value = '';
    for (var x = 0; x < lines.length; x++) {
      if (lines[x]) {
        value += '<DIV CLASS="original">' + lines[x] + '</DIV>';
      } else {
        value += '<DIV><BR></DIV>';
      }
    }
  } else if (mobwrite.UA_msie || mobwrite.UA_opera) {
    // MSIE & Opera use Ps to separate lines and an &nbsp; on blank lines.
    lines = value.split('\n');
    value = '';
    for (var x = 0; x < lines.length; x++) {
      if (lines[x]) {
        value += '<P CLASS="original">' + lines[x] + '</P>';
      } else {
        value += '<P>&nbsp;</P>';
      }
    }
  } else {
    // Everyone else uses BRs to separate lines.
    if (value) {
      value = value.replace(/\n/g, '</SPAN><BR><SPAN CLASS="original">');
      value = '<SPAN CLASS="original">' + value + '</SPAN>';
    }
    if (mobwrite.UA_gecko) {  // Gecko browsers add a trailing BR.
      value += '<BR>';
    }
  }
  return this.setClientHtml(value);
};


/**
 * Modify the user's plaintext by applying a series of patches against it.
 * @param {Array<patch_obj>} patches Array of Patch objects
 */
mobwrite.shareIframeObj.prototype.patchClientText = function(patches) {
  // Apply a series of patches to the user's text.
  if (this.firstEdit) {
    this.resetDocument_();
    // In general this would be destructive of cursor location.  But it's the first edit.
    var result = this.dmp.patch_apply(patches, this.getClientText());
    this.setClientText(result[0]);
    this.firstEdit = false;
    return;
  }
  this.dmp.patch_splitMax(patches);
  var body = this.doc.body;
  var text = this.getClientText();
  var delta = 0;
  // IE counts an image as a single character, so keep track of how many zap
  // icons are added in order to generate the correct character offset.
  var zapIcons = 0;
  for (var x = 0; x < patches.length; x++) {
    var expectedLoc = patches[x].start2 + delta;
    var text1 = this.dmp.diff_text1(patches[x].diffs);
    var startLoc = this.dmp.match_main(text, text1, expectedLoc);
    if (startLoc === null) {
      continue;  // No match found.  :(
    }
    delta = startLoc - expectedLoc;
    var text2 = text.substring(startLoc, startLoc + text1.length);
    // Run a diff to get a framework of equivalent indicies.
    var diff = this.dmp.diff_main(text1, text2, false);
    var index1 = 0;
    for (var y = 0; y < patches[x].diffs.length; y++) {
      var mod = patches[x].diffs[y];
      var index2;
      if (mod[0] != DIFF_EQUAL) {
        index2 = this.dmp.diff_xIndex(diff, index1);
      }
      var startDom, endDom;

      if (mod[0] == DIFF_INSERT) {  // Insertion
        // Insert text into the mock servertext.
        text = text.substring(0, startLoc + index2) + mod[1] + text.substring(startLoc + index2);
        // And do the same to the HTML.
        if (this.doc.createRange) {  // W3
          startDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + index2);
          if (this.decolourChanges) {
            // Drop any original styles.
            mobwrite.shareIframeObj.scrubBack_(startDom[0]);
            mobwrite.shareIframeObj.scrubForward_(startDom[0]);
          }
          var range = this.doc.createRange();
          try {
            if (startDom[1] == 0 && startDom[0].tagName != 'BODY') {
              range.setStartBefore(startDom[0]);
            } else {
              range.setStart(startDom[0], startDom[1]);
            }
          } catch (e) {
            if (mobwrite.debug) {
              window.console.warn('Error on setStart during insert:\n' + startDom + '\n' + e);
            }
            continue;
          }
          range.collapse(true);
          // Location is known, now add the text.
          var span = this.doc.createElement('span');
          span.id = mobwrite.uniqueId();
          span.className = 'highlight';
          mod[1] = mobwrite.shareIframeObj.spaceToNbsp_(mod[1]);
          var lines = mod[1].split('\n');
          for (z = 0; z < lines.length; z++) {
            if (lines[z]) {
              span.appendChild(this.doc.createTextNode(lines[z]));
            }
            if (z != lines.length - 1) {
              // Convert all CR+LF into <BR>.
              span.appendChild(this.doc.createElement('br'));
            }
          }
          range.insertNode(span);
          setTimeout('mobwrite.shareIframeObj.cropNode("' + this.file + '", "' + span.id + '")', this.highlightTime);
          range.detach();
        } else if (body.createTextRange) {  // MSIE
          if (this.decolourChanges) {
            // Drop any original styles.
            startDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + index2);
            mobwrite.shareIframeObj.scrubBack_(startDom[0]);
            mobwrite.shareIframeObj.scrubForward_(startDom[0]);
          }
          var range = body.createTextRange();
          startDom = startLoc + index2;
          range.move('character', startDom);
          // range.text = mod[1];  // Plaintext version without highlighting
          var span = mod[1];
          span = span.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          span = mobwrite.shareIframeObj.spaceToNbsp_(span);
          span = span.replace(/\n/g, '<BR>');
          var spanId = mobwrite.uniqueId();
          span = '<SPAN CLASS="highlight" ID="' + spanId + '">' + span + '</SPAN>'
          range.pasteHTML(span);
          setTimeout('mobwrite.shareIframeObj.cropNode("' + this.file + '", "' + spanId + '")', this.highlightTime);
        } else {
          // Uh oh.  Unsupported browser.
        }

      } else if (mod[0] == DIFF_DELETE) {  // Deletion
        // Delete text from the mock serverText.
        text = text.substring(0, startLoc + index2) + text.substring(startLoc + this.dmp.diff_xIndex(diff, index1 + mod[1].length));
        // And do the same to the HTML.
        if (this.doc.createRange) {  // W3
          startDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + index2);
          endDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + this.dmp.diff_xIndex(diff, index1 + mod[1].length));
          if (this.decolourChanges) {
            // Drop any original styles.
            mobwrite.shareIframeObj.scrubBack_(startDom[0]);
            mobwrite.shareIframeObj.scrubForward_(startDom[0], endDom[0]);
          }
          var range = this.doc.createRange();
          try {
            if (startDom[1] == 0) {
              range.setStartBefore(startDom[0]);
            } else {
              range.setStart(startDom[0], startDom[1]);
            }
          } catch (e) {
            if (mobwrite.debug) {
              window.console.warn('Error on setStart during delete:\n' + startDom + '\n' + e);
            }
            continue;
          }
          try {
            if (endDom[1] == 0) {
              range.setEndBefore(endDom[0]);
            } else {
              range.setEnd(endDom[0], endDom[1]);
            }
          } catch (e) {
            if (mobwrite.debug) {
              window.console.warn('Error on setEnd during delete:\n' + endDom + '\n' + e);
            }
            continue;
          }
          range.deleteContents();
          // Add a zap icon if this delete is not followed by an insert.
          if (this.zapIcon && patches[x].diffs[y + 1] && patches[x].diffs[y + 1][0] != DIFF_INSERT) {
            var span = this.doc.createElement('img');
            span.src = this.zapIcon;
            span.id = mobwrite.uniqueId();
            span.className = 'highlight';
            range.insertNode(span);
            setTimeout('mobwrite.shareIframeObj.nukeZap("' + this.file + '", "' + span.id + '")', this.zapIconTime);
          }
          range.detach();
        } else if (body.createTextRange) {  // MSIE
          if (this.decolourChanges) {
            // Drop any original styles.
            startDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + index2);
            endDom = mobwrite.shareIframeObj.findNodeOffset_(body, startLoc + this.dmp.diff_xIndex(diff, index1 + mod[1].length));
            mobwrite.shareIframeObj.scrubBack_(startDom[0]);
            mobwrite.shareIframeObj.scrubForward_(startDom[0], endDom[0]);
          }
          var range = body.createTextRange();
          startDom = startLoc + index2 + zapIcons;
          endDom = mod[1].length;
          range.move('character', startDom);
          range.moveEnd('character', endDom);
          // Add a zap icon if this delete is not followed by an insert.
          if (this.zapIcon && patches[x].diffs[y + 1] && patches[x].diffs[y + 1][0] != DIFF_INSERT) {
            var spanId = mobwrite.uniqueId();
            var span = '<IMG SRC="' + this.zapIcon + '" CLASS="highlight" ID="' + spanId + '">';
            range.pasteHTML(span);
            zapIcons++;
            setTimeout('mobwrite.shareIframeObj.nukeZap("' + this.file + '", "' + spanId + '")', this.zapIconTime);
          } else {
            // Just delete the text, don't add a highlighted zap.
            range.text = '';
          }
        } else {
          // Uh oh.  Unsupported browser.
        }
      }

      if (mod[0] != DIFF_DELETE) {
        index1 += mod[1].length;
      }
    }
  }
};


/**
 * After a locally-created diff is sent, strip the style tags from the affected
 * line(s).
 * @param {Array.<Array.<*>>} diffs Array of diff tuples
 */
mobwrite.shareIframeObj.prototype.onSentDiff = function(diffs) {
  if (!this.decolourChanges) {
    return;
  }
  // Determine the node locations of the start of each diff.
  var nodes = [];
  var i = 0;
  for (var x = 0; x < diffs.length; x++) {
    nodes[x] = mobwrite.shareIframeObj.followMapDom_(this.doc.body, i);
    if (diffs[x][0] != DIFF_DELETE) {
      i += diffs[x][1].length;
    }
  }

  // We now have two lists: diffs[x][0] (diff modes)
  // and nodes[x] (the document objects associated with each diff)
  for (var x = 0; x < diffs.length; x++) {
    if (diffs[x][0] != DIFF_EQUAL) {
      mobwrite.shareIframeObj.scrubBack_(nodes[x]);
      if (diffs[x][0] == DIFF_INSERT && x + 1 == diffs.length) {
        // Final insertion
        mobwrite.shareIframeObj.scrubForward_(nodes[x], this.doc.body);
      } else if (diffs[x][0] == DIFF_INSERT) {
        // Insertion
        mobwrite.shareIframeObj.scrubForward_(nodes[x], nodes[x + 1]);
      } else {
        // Deletion
        mobwrite.shareIframeObj.scrubForward_(nodes[x], null);
      }
    }
  }
};


// Remove the class of this node.
// Used to remove highlighting, while preserving the text.
// Ideally the node's children would be moved, but this can cause cursor jumps.
mobwrite.shareIframeObj.cropNode = function(shareId, nodeId) {
  // 'this' is undefined since this method is being called with setTimeout.
  // Thus we need to find the shareIframeObj based on the shareId.
  var shareIframeObj = mobwrite.shared[shareId];
  if (!shareIframeObj) {
    // The iframe must have been unshared while the highlighting was onscreen.
    return;
  }

  var node = shareIframeObj.doc.getElementById(nodeId);
  if (node) {
    node.className = '';
  }
};


// Delete a zap symbol.
mobwrite.shareIframeObj.nukeZap = function(shareId, nodeId) {
  // 'this' is undefined since this method is being called with setTimeout.
  // Thus we need to find the shareIframeObj based on the shareId.
  var shareIframeObj = mobwrite.shared[shareId];
  if (shareIframeObj) {
    // Find the zap in the DOM and delete it.
    var node = shareIframeObj.doc.getElementById(nodeId);
    if (node) {
      node.parentNode.removeChild(node);
    }
  }
};


/**
 * Walk back through the DOM nuking class names until we hit a line break.
 * @param {Node} node Current node.
 * @private
 */
mobwrite.shareIframeObj.scrubBack_ = function(node) {
  var backTrack = false;
  var firstTime = true; // Skip the very first node (it will be caught by scrubForward_).
  while (node.tagName != 'BODY') {
    if (node.nodeType != 3 && !firstTime) {
      if (node.className && node.className != 'highlight') {
        node.className = '';
      }
      if (node.tagName == 'BR' || node.tagName == 'P' || node.tagName == 'DIV') {
        return;
      }
    }
    firstTime = false;
    if (!backTrack && node.lastChild != null) {
      node = node.lastChild;
    } else if (node.previousSibling) {
      node = node.previousSibling;
      backTrack = false;
    } else {
      node = node.parentNode;
      backTrack = true;
    }
  }
};


/**
 * Walk forward through the DOM nuking class names until we pass 'finalnode' and hit a line break.
 * @param {Node} node Current node.
 * @param {Node} finalNode Current node.
 * @private
 */
mobwrite.shareIframeObj.scrubForward_ = function(node, finalNode) {
  var backTrack = false;
  while (node.tagName != 'BODY') {
    if (node == finalNode) {
      finalNode = null;
    }
    if (node.nodeType != 3) {
      if (finalNode == null && node.tagName == 'BR' || node.tagName == 'P' || node.tagName == 'DIV') {
        return;
      }
      if (node.className && node.className != 'highlight') {
        node.className = '';
      }
    }
    if (!backTrack && node.firstChild != null) {
      node = node.firstChild;
    } else if (node.nextSibling) {
      node = node.nextSibling;
      backtrack = false;
    } else {
      node = node.parentNode;
      backTrack = true;
    }
  }
};


/**
 * Add &nbsp; so that whitespace doesn't collapse.
 * Add the minimum number required, so as not to interfere with line wrapping.
 * @param {string} text Text possibly including runs of whitespace.
 * @return {string} Text with &nbsp; characters added.
 * @private
 */
mobwrite.shareIframeObj.spaceToNbsp_ = function(text) {
  text = text.replace(/\u00A0/g, ' '); // Remove any existing ones.
  text = text.replace(/  /g, '\u00A0 ').replace(/  /g, '\u00A0 ');
  text = text.replace(/^ /, '\u00A0').replace(/ $/, '\u00A0');
  text = text.replace(/\n /g, '\n\u00A0').replace(/ \n/g, '\u00A0\n');
  return text;
};


/**
 * Obtain a plaintext version of a DOM.
 * As a side-effect, adds character indexing properties to every node.
 * @param {Node} startNode Top of the DOM tree.
 * @return {string} Plaintext content.
 * @private
 */
mobwrite.shareIframeObj.domToText_ = function(startNode) {
  // IE could sort of use this:
  // return document.body.createTextRange().moveToElementText(startNode).text;
  // But it puts an extra \r\n in this: '<P>one<BR></P><P>two</P>'
  var text = '';
  // crlf records the node requesting a linebreak.
  // '<DIV></DIV><DIV></DIV>' is only one linebreak.
  var crlf = null;
  // br records if the last entry was a <BR>.
  var br = false;
  var node = startNode.firstChild;
  if (!node) {
    return '';
  }
  var backTrack = false;

  while (node != startNode) {
    if (!backTrack) {
      // We haven't been to this node before.
      if (node.nodeType == 3) {
        // Text node.
        if (node.data) {
          if (text && crlf) {
            // Add previously requested linefeed.
            crlf[mobwrite.shareIframeObj.charAddAttribute] = 1;
            text += '\n';
          }
          crlf = null;
          br = false;
          text += node.data.replace(/[ \t\r\n]+/g, ' ');
        }
      } else if (node.nodeType == 1) {
        // Start tag.
        node[mobwrite.shareIframeObj.charIndexAttribute] = text.length;
        if (node.tagName == 'DIV' || node.tagName == 'P') {
          if (mobwrite.UA_opera && node.tagName == 'P' &&
              node.childNodes.length == 1 && node.firstChild.data == '') {
            // This is Opera's placeholder: <P></P> with a null textnode.
            text += '\n';
            node[mobwrite.shareIframeObj.charAddAttribute] = 1;
          } else if (mobwrite.UA_msie && node.tagName == 'P' && !node.firstChild) {
            // This is IE's placeholder: <P>&nbsp;</P>
            // The &nbsp; doesn't exist when viewed at this level in IE.
            text += '\n';
            node[mobwrite.shareIframeObj.charAddAttribute] = 1;
          }
          if (!br) {
            crlf = node;
          }
        } else if (node.tagName == 'BR') {
          if (text && crlf) {
            // Add previously requested linefeed.
            text += '\n';
            crlf[mobwrite.shareIframeObj.charAddAttribute] = 1;
            node[mobwrite.shareIframeObj.charIndexAttribute] += 1;
          }
          crlf = null;
          br = true;
          text += '\n';
          node[mobwrite.shareIframeObj.charAddAttribute] = 1;
        }
      }
    } else {
      // Closing tag.
      if (node.tagName == 'DIV' || node.tagName == 'P') {
        if (!br) {
          crlf = node;
        }
      }
    }

    if (!backTrack && node.firstChild) {
      node = node.firstChild;
    } else if (node.nextSibling) {
      node = node.nextSibling;
      backTrack = false;
    } else {
      node = node.parentNode;
      backTrack = true;
    }
  }

  // Normalize whitespace.
  text = text.replace(/\u00A0/g, ' ');
  // Safari has issues with regex replacements of Unicode.
  while (text.indexOf('\u00A0') != -1) {
    text = text.replace('\u00A0', ' ');
  }

  return text;
};


/**
 * Walk up from the given node to the previous node.
 * @param {Node} node The node to start from
 * @return {Node?} The previous node in the DOM (or null if none)
 * @private
 */
mobwrite.shareIframeObj.walkUp_ = function(node) {
  // Return null if one runs off the top.
  if (node.tagName == 'BODY') {
    return null;
  }
  if (node.previousSibling) {
    node = node.previousSibling;
    while (node.hasChildNodes()) {
      node = node.lastChild;
    }
    return node;
  }
  if (node.parentNode) {
    return node.parentNode;
  }
  // Ran off top of page.
  return null;
};


/**
 * Walk down from the given node to the next node.
 * @param {Node} node The node to start from
 * @return {Node?} The next node in the DOM (or null if none)
 * @private
 */
mobwrite.shareIframeObj.walkDown_ = function(node) {
  if (node.hasChildNodes()) {
    return node.firstChild;
  }
  while (node && node.tagName != 'BODY') {
    if (node.nextSibling) {
      return node.nextSibling;
    }
    node = node.parentNode;
  }
  // Ran off the page.
  return null;
};


/**
 * Look up how many characters preceeded the given node.
 * DOM must have been preindexed by domToText_().
 * @param {Node} node The node to look up.
 * @return {Number} The number of characters preceeding this node.
 *     Returns 0 if node is not indexed.
 * @private
 */
mobwrite.shareIframeObj.getCharIndex_ = function(node) {
  var first = true;
  var delta = 0;
  while (node) {
    // First check if there is a charIndex tag.
    if (mobwrite.shareIframeObj.charIndexAttribute in node) {
      return node[mobwrite.shareIframeObj.charIndexAttribute] + delta;
    }
    // This must be a text node (IE can't store tags on text nodes).
    if (first) {
      first = false;
    } else if (node.data) {
      delta += node.data.length;
    }
    // Walk to previous nodes until we hit a non-text node.
    node = mobwrite.shareIframeObj.walkUp_(node);
    // DIV, BR and P tags sometimes involve linefeeds.
    if (node && mobwrite.shareIframeObj.charAddAttribute in node) {
      delta += node[mobwrite.shareIframeObj.charAddAttribute];
    }
  }
  return 0;
};


/**
 * Step down the DOM looking for the first node with the largest charIndex
 * property that is smaller or equal to target.  Recursive, extremely fast.
 * DOM must have been preindexed by domToText_().
 * @param {Node} node The DOM fragment to search.
 * @param {Number} target The charIndex value not to exceed.
 * @return {Object} The node with the best charIndex property.
 * @private
 */
mobwrite.shareIframeObj.followMapDom_ = function(node, target) {
  // First pass: use a rough tree-search to find the first node that's ok or
  // too large.
  node = mobwrite.shareIframeObj.followMapDomRecursive_(node, target);
  
  // Second pass: walk up to the last qualifying node.
  var nodeIndex = mobwrite.shareIframeObj.getCharIndex_(node);
  while (nodeIndex >= target) {
    var prevNode = mobwrite.shareIframeObj.walkUp_(node);
    if (!prevNode) {
      // Ran off the document top.
      break;
    }
    node = prevNode;
    nodeIndex = mobwrite.shareIframeObj.getCharIndex_(node);
  }

  // Special case for BR: it creates one character and does not contain nodes.
  // 'a<BR>b': 0->a, 1->a, 2->b, 3->b
  // 'a<P>b</P>': 0->a, 1->a, 2-><P> 3->b
  if (node.tagName == 'BR' && mobwrite.shareIframeObj.charAddAttribute in node &&
      nodeIndex + node[mobwrite.shareIframeObj.charAddAttribute] == target) {
    return mobwrite.shareIframeObj.walkDown_(node) || node;
  }

  // Third pass: keep walking up if previous nodes have the same index.
  // e.g. <P></P><P></P><P></P>
  if (node.nodeType == 1) {
    var prevNode = node;
    do {
      node = prevNode;
      prevNode = mobwrite.shareIframeObj.walkUp_(node);
      prevNodeIndex = mobwrite.shareIframeObj.getCharIndex_(prevNode);
    } while (prevNode && nodeIndex == prevNodeIndex);
  }

  // Special case: don't return [BODY, 0], step into first node.
  // Inserting something before the first node can cause an unexpected
  // linefeed if that first node is a P or DIV.
  if (node.tagName == 'BODY' && target == 0) {
    node = mobwrite.shareIframeObj.walkDown_(node) || node;
  }

  return node;
};


/**
 * Step down the DOM looking for the first node with the largest charIndex
 * property that is smaller or equal to target.  Recursive, extremely fast.
 * Not guaranteed to find the very first matching node.  See folowMapDom_
 * DOM must have been preindexed by domToText_().
 * @param {Node} node The DOM fragment to search.
 * @param {Number} target The charIndex value not to exceed.
 * @return {Object} The node with the best charIndex property.
 * @private
 */
mobwrite.shareIframeObj.followMapDomRecursive_ = function(node, target) {
  var nodeIndex = mobwrite.shareIframeObj.getCharIndex_(node);
  if (nodeIndex >= target) {
    return node;
  } else if (node.nodeType == 3) {
    return node;
  } else if (!node.hasChildNodes()) {
    // Non-container tags like <HR>
    return node;
  }
  for (var x = 0; x < node.childNodes.length - 1; x++) {
    var childIndex = mobwrite.shareIframeObj.getCharIndex_(node.childNodes[x + 1]);
    if (childIndex >= target) {
      return mobwrite.shareIframeObj.followMapDomRecursive_(node.childNodes[x], target);
    }
  }
  // It's either the last child or this node's closing tag
  // or a parent node's closing tag.
  var childResult = mobwrite.shareIframeObj.followMapDomRecursive_(node.lastChild, target);
  if (typeof childResult == 'object') {
    return childResult;
  } else if (childResult + 1 == target) {
    return node;
  } else {
    return childResult + 1;
  }
};


/**
 * Find the node and offset which corresponds to the requested target
 * position. e.g. 'a<P></P><P></P>b' -> first <P> for 2
 * DOM must have been preindexed by domToText_().
 * @param {Node} startNode The DOM fragment to search.
 * @param {Number} target The charIndex value to seek.
 * @return {Array} A tuple containing a node and an offset within that node.
 * @private
 */
mobwrite.shareIframeObj.findNodeOffset_ = function(startNode, target) {
  var node = mobwrite.shareIframeObj.followMapDom_(startNode, target);
  var offset;
  if (node.nodeType == 3) {
    offset = target - mobwrite.shareIframeObj.getCharIndex_(node);
    if (offset > node.data.length) {
      // This should never happen.
      offset = node.data.length;
    }
  } else {
    if (!node.hasChildNodes()) {
      offset = 0;
    } else if (mobwrite.shareIframeObj.getCharIndex_(node) +
        (mobwrite.shareIframeObj.charAddAttribute in node ?
        node[mobwrite.shareIframeObj.charAddAttribute] : 0) >= target) {
      offset = 0;
    } else {
      offset = node.childNodes.length;
    }
  }

  return [node, offset];
};


/**
 * Handler to accept iframes as elements that can be shared.
 * If the element is an iframe, create a new sharing object.
 * Makes editable.
 * @param {*} node Object or ID of object to share
 * @return {Object?} A sharing object or null
 */
mobwrite.shareIframeObj.shareHandler = function(node) {
  if (typeof node == 'string') {
    node = document.getElementById(node);
  }

  if (!node || typeof node != 'object') {
    return;
  }
  var id = node.id;
  if (!node.contentWindow.document) {
    // Can't find document for the iframe.  Maybe it's not an iframe.
    return;
  }
  var doc = node.contentWindow.document;
  if ('contentEditable' in doc.body) {
    doc.body.contentEditable = true;
  } else {
    // Firefox 2 and below.
    doc.designMode = 'on';
  }
  return new mobwrite.shareIframeObj(doc, id);
};


// Register this shareHandler with MobWrite.
mobwrite.shareHandlers.push(mobwrite.shareIframeObj.shareHandler);


// Convert a node into a human-readable string.
// Very helpful debugging function.
function node2str(node) {
  if (node.nodeType == 3) {
    return '"' + node.data + '"';
  } else if (node.nodeType == 1) {
    return '<'+node.nodeName+'>' + node.innerHTML + '</'+node.nodeName+'>';
  } else {
    return '' + node;
  }
}
