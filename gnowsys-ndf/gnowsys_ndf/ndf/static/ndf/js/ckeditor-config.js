/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */
	var basePath = CKEDITOR.basePath;
	basePath = basePath.substr(0, basePath.indexOf("ndf/"));
 	//function to add External plugins
	 (function() {
	   CKEDITOR.plugins.addExternal('addImage',basePath+'ndf/js/ckPlugins/addImage/','plugin.js');
	   CKEDITOR.plugins.addExternal('closebtn',basePath+'ndf/js/ckPlugins/closebtn/','plugin.js');
	   CKEDITOR.plugins.addExternal('addAudio',basePath+'ndf/js/ckPlugins/addAudio/','plugin.js');
	   CKEDITOR.plugins.addExternal('font',basePath+'ndf/bower_components/ckeditor/plugins/font/','plugin.js');

	})();

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbar_GeneralToolbar =
	[

		{ name: 'basicstyles', items : [ 'Bold','Italic','Strike','-','RemoveFormat' ] },
		{ name: 'editing', items : [ 'Find','Replace','-','SelectAll','-' ] },
		{ name: 'insert', items : [ 'Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak','Iframe','video'] },
		{ name: 'styles', items : [ 'Font' ] },
		{ name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote' ] },
		{ name: 'links', items : [ 'Link','Unlink' ] },
		{ name: 'tools', items : [ 'addImage','addAudio','Source','Maximize','-'] },

	];

	config.toolbar_BasicToolbar =
	[
		{ name: 'basicstyles', items : [ 'Bold','Italic','Strike','-','RemoveFormat' ] },
		{ name: 'paragraph', items : [ 'NumberedList','BulletedList','-' ] },
		{ name: 'links', items : [ 'Link','Unlink'] },
		{ name: 'insert', items : [ 'Flash','Iframe' ] },
		{ name: 'tools', items : [ 'addImage','addAudio','Source', 'Maximize','-','closebtn'] },
	];

	config.toolbar_GgallaryCommentsToolbar =
	[
		{ name: 'basicstyles', items : [ 'Bold','Italic' ] },
		{ name: 'links', items : [ 'Link','Unlink'] },
		{ name: 'tools', items : ['closebtn'] },
	];



	// ];
	// config.toolbarGroups = [
	// 	{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
	// 	{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
	// 	{ name: 'links' },
	// 	{ name: 'insert' },
	// 	{ name: 'forms' },
	// 	{ name: 'tools' },
	// 	{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
	// 	{ name: 'others' },
	// 	'/',
	// 	{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	// 	{ name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
	// 	{ name: 'styles' },
	// 	{ name: 'colors' },
	// 	{ name: 'addImage'}


	// ];

	// Remove some buttons provided by the standard plugins, which are
	// not needed in the Standard(s) toolbar.
	config.removeButtons = 'Underline,Subscript,Superscript';

	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';
	config.entities = false; //set false to work with  entities such as   "" & '' in source code
	config.tabSpaces = 4; // for tab spacing
	config.font_names =  'Arial/Arial, Helvetica, sans-serif;' +
            'Comic Sans MS/Comic Sans MS, cursive;' +
            'Courier New/Courier New, Courier, monospace;' +
            'Georgia/Georgia, serif;' +
            'Lucida Sans Unicode/Lucida Sans Unicode, Lucida Grande, sans-serif;' +
            'Tahoma/Tahoma, Geneva, sans-serif;' +
            'Times New Roman/Times New Roman, Times, serif;' +
            'Trebuchet MS/Trebuchet MS, Helvetica, sans-serif;' +
            'Calibri/Calibri, Verdana, Geneva, sans-serif;' + /* here is your font */
            'Verdana/Verdana, Geneva, sans-serif';

	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';
	config.extraPlugins = 'addImage,closebtn,addAudio,font';
	config.allowedContent = true;

};
