jQuery(document).ready(function($) {
    $(window).load(function() {
        $("button[rel]").overlay({mask: '#000', effect: 'apple'});
    });

$(document).on('click',"#loadeditor",function() {
        $("button[rel]").overlay({mask: '#000', effect: 'apple'});
});
});
