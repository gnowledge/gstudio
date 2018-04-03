# Interactives
> Interactives are JS/HTML apps intended to integrate with gStudio. Data generated will get saved under defined folder hierarchy as JSON file.


### I. Implementation Objectives:
- Should be easy to embed and play in multiple activity pages.
- While students playing the interactive, it should track each and every step and log those detailed data along with inputs of each iterations(if applicable).
- User Generated Data (UGD) should get saved to server.
    - Data persistance should happen at any of following events:
        1. On interactive completion / click-of-button (e.g: `Finish` , `Done` etc.)
        2. Before user leaving page.
        3. After fixed configured period (e.g: 2 min).
- UGD is **CREATE only** for research purpose, which is not intended to get Read/Update/Delete within/via platform UI.
    - UGD will get stored as JSON file under `/data/gstudio-tool-logs/<tool-name>` folder in server.
        - Following is exemplar hierarchy:
        ```
            <tool-name>
            ├── 0-en-180212162912.json
            ├── 0-en-180212162807.json
            ├── 0-hi-180212162948.json
            ├── 5-hi-180212162952.json
            ├── 5-hi-180212163000.json
            ├── 66-en-180212163022.json
            ├── 66-hi-180212163023.json
            ├── 98-en-180212163009.json
            └── 98-en-180212163025.json
        ```
        - File naming convention:
            - It is combination of following 3 values:
                1. User ID (e.g: *66*)
                2. Language Code (e.g: *hi*)
                3. Timestamp: YYMMDDHHMMSS (e.g: *180212163009*)
            - Final file name will be: `66-hi-180212163023.json`


### II. Steps to achieve:
- Data will be collected in JSON format. **(TODO: Confirm JSON schema along with key nomenaclature/convention and value datatype)**
- Provide following JS-methods to:
    - Create a Unique Token Key (UTK).
        - Format: USERID-LANGCODE-YYMMDDHHMMSS
            - USERID and LANGCODE is in [cookies](../cookie.html) with key: `user_id` and `language_code` respectively. Which needs to be pick up by JS method.
        - *Note: Anonymous user will have `0` User Id, cookie will have value `None`*
    - Get JSON data at any given time.
    - Add/Update additional metadata (AMD) in same JSON data. *(TODO: Decide on AMD schema and fields)*
        - Pending: Gstudio to provide JS method giving context of current activity at any given page.
    - POST AJAX method to push UGD in gstudio server.
        - This method should take following arguments *(arguments can be taken via iframe query url or URI seperator, `#`)*:
            1. Data saving end point url: `/tools/logging/`
        - POST data:
            1. UGD (json):
                - Core interactive data.  
                - AMD
                    - `timestamp` (e.g: `YYMMDDHHMMSS`)
                    - `locale` (e.g: `en` or `hi`)
                    - `user_id` (e.g: `12345`)
                    - `user_and_buddy_ids` (pick from cookie, e.g: `12345&1417`)
                    - `app_name` (i.e: Name of app/interactive)
                - UTK
                    - USERID-LANGCODE-YYMMDDHHMMSS
                    - e.g: `66-hi-180212163023`
            2. `csrfmiddlewaretoken`:
                - `csrftoken`
                - Can be taken from cookie named - `csrftoken`
    - An event listner method which will listen to any of above specified (3) events and trigger POST AJAX method.


### III. Interactive features requests:
#### **PHASE - 1**
- Taking input from user and rendering result.
- Tracking each and every user actions and persisting data in JSON form.

#### **PHASE - 2**
- **Responsiveness**
    > Any action like a button click, should result in some visible change somewhere - the users should not have to wait and press more buttons to see the effect.
    - Can we use soft CSS/JS volatile popups to explicit user actions?

- **Permissiveness**
    > Should not gray out all buttons and at any time give control to the user. We should expect the user to do reasonable things at all times. No taking away control.
    - Can we have *play/edit* and *view-only* behavior? Which can be configured by passing URI parameter. 

- **Consistency** 
    > Should give a similar look and feel across interactives, nothing more nothing less. We cannot expect the user to learn to map a new set of actions to some existing button types with which he/she had earlier associated something else. Also about the placement of buttons...
    - Making a provision to override CSS. Enabling custom CSS skin to interactive.


### IV. Pending/TODO:
- AMD schema
- gstudio: end point for UGD saving (via POST AJAX).
    + After JSON data file creation, subsequent writting may happen multiple times 
    + Check for UTK in POST data. If present override existing JOSN file or create a new one.
- Create template to render interactives like `node_ajax_content.html`, which will have necessary styles, JS methods.
    + All the interactives will render with `index.html` as default. If this is not the case, custom template name should be provided to key `index` while including this template.
<!-- - Interactive tool name -->


### V. Glossary:
- UTK: Unique Token Key
- UGD: User Generated Data 
- AMD: Additional MetaData 