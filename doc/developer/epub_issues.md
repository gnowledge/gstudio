# Bugs found, but yet to be fixed, in the epub generated
We, the Xchange group from BITS Pilani interns 2018, used http://validator.idpf.org/ (which uses EpubCheck library) to validate epubs generated using our export_to_unit.py script and found the following issues/bugs in the epub.
Bugs in **content.opf** :
1. `<html>, <body>` tags are to be removed from the generated epub, as they are no longer part of the standard.
2. Since we are not storing date and description of the epub, we need to remove `<dc:date> and <dc:description>` tags.
3. Format of date inside dcterms:modified should be like 2018-06-07T14:42:18Z (YYYY-MM-DDThh:mm::ssZ), and 2 extra copies of the date after dcterms:modified should be removed.
4. In meta properties ranging from ibooks:version to ibooks:scroll-axis, the property should be contained inside the meta tag, e.g. `<meta property="ibooks:scroll-axis"> vertical </meta>`
5. In manifest, IDs of items must not have any space like `<item href="Images/Express Parcel" id="Express Parcel" media-type="image/png">`. Such spaces ought to be replaced by an underscore ( _ ). Hrefs of the items need not be changed.
6. In manifest, media-type of all xhtml items should be application/xhtml+xml. e.g. `<item href="Text/le_spab-ms.xhtml" id="le_spab-ms.xhtml" media-type="application/xhtml+xml">`
7. In manifest, Certain items have names starting with a digit like '1-gender.xhtml', but their IDs should not start with a digit. Those need to be prefixed with an underscore. like '_1-gender.xhtml'. (Href should not be changed.)
8. In spine (table of contents), idref of itemref should not start with a digit like point 7 above.
9. In manifest, id of styles.css should be clix-activity-styles.css like  `<item href="Styles/clix-activity-styles.css" id="clix-activity-styles.css" media-type="text/css">`
10. Since many xhtml files have scripts inside them, their declaration should have "properties scripted" like so: `<item href="Text/postal-charges.xhtml" id="postal-charges.xhtml" media-type="application/xhtml+xml" properties="scripted">`
11. In OEBPS/Text/assessment.xhtml, for allowing remote resource access, property 'remote-resources' should be declared in content.opf
12. sgc-toc.css, opensans-font.css etc should be declared in content.opf
13. All the included fonts should be declared in content.opf
14. To have ibooks support, package tag of content.opf should have prefix attribute as follows: `<package unique-identifier="BookId" version="3.0" xmlns="http://www.idpf.org/2007/opf" prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/">`

[//]: # (list end)
Bugs in other files:
- Spaces should be removed from all file-names (esp. images).
- In file videojs-skin-colour.css, last line should not have word "io" as it currently has.
- In clix-activity-styles.css, CSS variables, which are a very recent feature, are causing trouble.
- In OEBPS/Text/*.xhtml, alt text of images having spaces in names should be properly kept. e.g. it should be `<img alt="Express Parcel" />` instead of current `<img alt="Express" parcel="" />`
- In OEBPS/Text/*.xhtml, `<font>` tag has been used, which is not supported in HTML5, and should be replaced with proper CSS.
- In OEBPS/Text/nav.xhtml, sgc-nav.css is needed, but is not included in CSS Styles folder. 