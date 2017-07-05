//http://stackoverflow.com/questions/18956257/how-to-add-an-ajax-save-button-with-loading-gif-to-ckeditor-4-2-1-working-samp

CKEDITOR.plugins.add( 'closebtn', {
    icons: 'closebtn',
    init: function( editor ) {
        editor.addCommand( 'closetoolbar', {
        	exec : function(editor){
                var id = "cke_"+editor.name;
                var elem;
                if( document.getElementById ){
                    elem = document.getElementById(id);
                }else if( document.all ){
                    elem = document.all[id];
                }else if( document.layers ){
                    elem = document.layers[id];
                }
                
                $("#create-discussion").show();
                setCurrNodeEdit("");    
                CKEDITOR.instances.ckeditor_textarea.destroy();
                $( "div" ).remove( ".ckeditor-content-reply" );
                $( "div" ).remove( ".ckeditor-content-comment" );
                $('.reply-button').remove();
                $(".btn-group").remove();
                $("#audios-container").remove();
                
    	}
    });


//add the save button to the toolbar

        editor.ui.addButton( 'closebtn', {
            label: 'Close',
            command: 'closetoolbar'
           // toolbar: 'insert'
        });


    }
});
