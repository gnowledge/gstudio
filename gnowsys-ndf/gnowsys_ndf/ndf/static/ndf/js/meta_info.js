    var header_logo_dataURL;
    function toDataUrl(url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function() {
            var reader = new FileReader();
            reader.onloadend = function() {
                callback(reader.result);
            }
            reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.send();
    }

    toDataUrl('/static/ndf/images/Clix-logo.png', function(myBase64) {
        header_logo_dataURL = myBase64; // myBase64 is the base64 string
    });
 

var date = new Date();
var datetime_val = date.toDateString() + date.toLocaleTimeString()
