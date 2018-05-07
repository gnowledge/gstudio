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
	   CKEDITOR.plugins.addExternal('addVideo',basePath+'ndf/js/ckPlugins/addVideo/','plugin.js');
	   CKEDITOR.plugins.addExternal('addJhapp',basePath+'ndf/js/ckPlugins/addJhapp/','plugin.js');
	   CKEDITOR.plugins.addExternal('mathjax',basePath+'ndf/bower_components/ckeditor/plugins/mathjax/','plugin.js');
	   CKEDITOR.plugins.addExternal('font',basePath+'ndf/bower_components/ckeditor/plugins/font/','plugin.js');
	   CKEDITOR.plugins.addExternal('find',basePath+'ndf/bower_components/ckeditor/plugins/find/','plugin.js');
	   CKEDITOR.plugins.addExternal('smiley',basePath+'ndf/bower_components/ckeditor/plugins/smiley/','plugin.js');
	
	})
	();
    CKEDITOR.config.bodyId = 'scstyle';

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.

	

	config.toolbar_GeneralToolbar =
	[

		{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','-','RemoveFormat','Subscript','Superscript','Undo','Redo' ] },
		{ name: 'editing', items : [ 'Find','Replace','-','SelectAll','-','Scayt' ] },
		{ name: 'insert', items : [ 'Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak','Iframe','video'] },
		{ name: 'styles', items: [ 'Format', 'FontSize' ] },
		{ name: 'paragraph', items : [ 'NumberedList','BulletedList','Mathjax','-','Outdent','Indent','-','Blockquote','JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] },
		{ name: 'links', items : [ 'Link','Unlink' ] },
		{ name: 'tools', items : [ 'addImage','addAudio','addVideo','addJhapp','Source','Anchor','Maximize','-'] },
		{ name: 'document', items: [ '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates' ] },
		


	];
	


	config.toolbar_BasicToolbar =
	[
		{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','-','RemoveFormat','Subscript', 'Superscript','Undo','Redo','Find','Smiley' ] },
		{ name: 'paragraph', items : [ 'NumberedList','BulletedList','Mathjax','-','JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] },
		{ name: 'links', items : [ 'Link','Unlink'] },
		{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker' ]},
		{ name: 'insert', items : [ 'Flash','Iframe' ] },
		{ name: 'tools', items : [ 'addImage','addAudio','addVideo','addJhapp','Source','Anchor', 'Maximize','-','closebtn'] },
		{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'styles' },
	];

	config.toolbar_GgallaryCommentsToolbar =
	[
		{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','align','Undo','Redo','Find','Smiley' ] },
		{ name: 'links', items : [ 'Link','Unlink'] },
		{ name: 'tools', items : ['closebtn'] },
	];

	config.toolbar_LMSStudentsToolbar =
	[
		{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','align','Undo','Redo','Find','Smiley' ] },
		{ name: 'paragraph', items : [ 'NumberedList','BulletedList','Mathjax','-','JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] },
		{ name: 'links', items : [ 'Link','Unlink'] },
		{ name: 'tools', items : ['addImage','addAudio','addVideo','Anchors','closebtn'] },
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
	// config.mathJaxLib = '//cdn.mathjax.org/mathjax/2.6-latest/MathJax.js?config=TeX-AMS_HTML';
	config.mathJaxLib = '/static/ndf/bower_components/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML';
	//config.removeButtons = 'Underline';

	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';
	config.entities = false; //set false to work with  entities such as   "" & '' in source code
	config.tabSpaces = 4; // for tab spacing


	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';
	config.extraPlugins = 'addImage,closebtn,addAudio,addVideo,addJhapp,mathjax,justify,font,find,smiley';
	config.allowedContent = true;

};
