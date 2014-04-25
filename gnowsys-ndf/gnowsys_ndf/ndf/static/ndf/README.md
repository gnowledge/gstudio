# Folder structure for static components

* scss/ - Source sass stylesheets for the app
* scss/skins - Style settings for customized skins
* css/ - Compiled css from the sass files.
* images/ - Image assets and icons
* js/ - Scripts for the app
* components/ - Frontend components managed by bower
* .bowerrc - bower configuration
* bower.json - bower dependencies
* config.rb - configuration file for compass to watch and compile sass stylesheets

## Package management using bower

Third party frontend packages can like jquery can be managed and updated using [bower](http://www.bower.io). This allows for clean installation and dependency management. Bower managed packages are in the components/ folder and currently contain the following components:

* Foundation - Responsive CSS framework
* jQuery
* d3 - Visualization library
* 

## Editing styles

Stylesheets are authored in [sass](http://sass-lang.com/) for easy management and customization with foundation. The css styles are compiled from the following sass partials:

* scss/skins/*.scss - Contains master variables for customizing the skin. This mostly includes the color pallette, typography and icon settings
* scss/_settings.scss - Contains fallback skin settings and customized settings for Foundation
* scss/_application.scss - Contains the main styles for the application
* scss/foundation-skin.scss - Is the final stylesheet compiled from the above partials. This file also contains any styles to override any default foundation rules.

* css/css.css - The only css file that is available for editing. This is to be used for making quick style fixes without the need to edit the sass stylesheets.

## Compiling styles

SCSS stylesheets need to be linked and precompiled to CSS. This is currently done using [compass](http://compass-style.org/).

* Install Ruby and [Compass gem](http://compass-style.org/install/)
* cd to the static assets folder '''cd gstudio/gnowsys-ndf/gnowsys_ndf/ndf/static/ndf'''
* run '''compass --watch'''
