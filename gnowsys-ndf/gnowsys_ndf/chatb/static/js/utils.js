function logError() {
    console.log('ERROR', arguments);
}

function addTurnServers() {
    // Dont fail if browser is not supported
    if (!createIceServer) {
        return;
    }
    // Skipping TURN Http request for Firefox version <=22.
    // Firefox does not support TURN for version <=22.
    if (webrtcDetectedBrowser === 'firefox' && webrtcDetectedVersion <=22) {
        return;
    }
    if (config.turnServer) {
        for (i = 0; i < config.turnServer.uris.length; i++) {
            // Create a turnUri using the polyfill (adapter.js).
            var iceServer = createIceServer(config.turnServer.uris[i],
                                            config.turnServer.username,
                                            config.turnServer.password);
            if (iceServer !== null) {
                pc_config.iceServers.push(iceServer);
            }
        }
    }
}

// Set Opus as the default audio codec if it's present.
function preferOpus(sdp) {
    var sdpLines = sdp.split('\r\n');

    // Search for m line.
    for (var i = 0; i < sdpLines.length; i++) {
        if (sdpLines[i].search('m=audio') !== -1) {
          var mLineIndex = i;
          break;
        }
    }
    if (mLineIndex === null)
      return sdp;

    // If Opus is available, set it as the default in m line.
    for (var i = 0; i < sdpLines.length; i++) {
      if (sdpLines[i].search('opus/48000') !== -1) {
        var opusPayload = extractSdp(sdpLines[i], /:(\d+) opus\/48000/i);
        if (opusPayload)
          sdpLines[mLineIndex] = setDefaultCodec(sdpLines[mLineIndex], opusPayload);
        break;
      }
    }

    // Remove CN in m line and sdp.
    sdpLines = removeCN(sdpLines, mLineIndex);

    sdp = sdpLines.join('\r\n');
    return sdp;
}

// Set Opus in stereo if stereo is enabled.
function addStereo(sdp) {
    var sdpLines = sdp.split('\r\n');

    // Find opus payload.
    for (var i = 0; i < sdpLines.length; i++) {
      if (sdpLines[i].search('opus/48000') !== -1) {
        var opusPayload = extractSdp(sdpLines[i], /:(\d+) opus\/48000/i);
        break;
      }
    }

    // Find the payload in fmtp line.
    for (var i = 0; i < sdpLines.length; i++) {
      if (sdpLines[i].search('a=fmtp') !== -1) {
        var payload = extractSdp(sdpLines[i], /a=fmtp:(\d+)/ );
        if (payload === opusPayload) {
          var fmtpLineIndex = i;
          break;
        }
      }
    }
    // No fmtp line found.
    if (fmtpLineIndex === null)
      return sdp;

    // append stereo=1 to fmtp line.
    sdpLines[fmtpLineIndex] = sdpLines[fmtpLineIndex].concat(' stereo=1');

    sdp = sdpLines.join('\r\n');
    return sdp;
}

function extractSdp(sdpLine, pattern) {
    var result = sdpLine.match(pattern);
    return (result && result.length == 2)? result[1]: null;
}

  // Set the selected codec to the first in m line.
function setDefaultCodec(mLine, payload) {
    var elements = mLine.split(' ');
    var newLine = new Array();
    var index = 0;
    for (var i = 0; i < elements.length; i++) {
      if (index === 3) // Format of media starts from the fourth.
        newLine[index++] = payload; // Put target payload to the first.
      if (elements[i] !== payload)
        newLine[index++] = elements[i];
    }
    return newLine.join(' ');
}

  // Strip CN from sdp before CN constraints is ready.
function removeCN(sdpLines, mLineIndex) {
    var mLineElements = sdpLines[mLineIndex].split(' ');
    // Scan from end for the convenience of removing an item.
    for (var i = sdpLines.length-1; i >= 0; i--) {
      var payload = extractSdp(sdpLines[i], /a=rtpmap:(\d+) CN\/\d+/i);
      if (payload) {
        var cnPos = mLineElements.indexOf(payload);
        if (cnPos !== -1) {
          // Remove CN payload from m line.
          mLineElements.splice(cnPos, 1);
        }
        // Remove CN line in sdp
        sdpLines.splice(i, 1);
      }
    }

    sdpLines[mLineIndex] = mLineElements.join(' ');
    return sdpLines;
}

function sdpRate(sdp, rate) {
    rate = rate || 1638400;
    return sdp.replace(/b=AS:\d+\r/g, 'b=AS:' + rate + '\r');
}

function mergeConstraints(cons1, cons2) {
    var merged = cons1;
    for (var name in cons2.mandatory) {
        merged.mandatory[name] = cons2.mandatory[name];
    }
    merged.optional.concat(cons2.optional);
    return merged;
}

function formatMessage(text) {
    //return Ox.sanitizeHTML(message.replace(/\n/g, '<br>'));
    var html = $('<div>').text(text).html();
    return addLinks(html).replace(/\n/g, '<br>\n');

    function addLinks(string) {
        return string
            .replace(
                /\b((https?:\/\/|www\.).+?)([.,:;!?)\]]*?(\s|$))/gi,
                function(match, url, prefix, end) {
                    prefix = prefix.toLowerCase() == 'www.' ? 'http://' : '';
                    return formatString(
                        '<a href="{prefix}{url}">{url}</a>{end}',
                        {end: end, prefix: prefix, url: url}
                    );
                }
            )
            .replace(
                /\b([0-9A-Z.+\-_]+@(?:[0-9A-Z\-]+\.)+[A-Z]{2,6})\b/gi,
                '<a href="mailto:$1">$1</a>'
            );
    }
    function formatString(string, collection, keepUnmatched) {
        return string.replace(/\{([^}]+)\}/g, function(string, match) {
            // make sure to not split at escaped dots ('\.')
            var key,
                keys = match.replace(/\\\./g, '\n').split('.').map(function(key) {
                    return key.replace(/\n/g, '.');
                }),
                value = collection || {};
            while (keys.length) {
                key = keys.shift();
                if (value[key]) {
                    value = value[key];
                } else {
                    value = null;
                    break;
                }
            }
            return value !== null ? value : keepUnmatched ? '{' + match + '}' : '';
        });
    };
}
