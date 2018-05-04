# Interactives
> Interactives are JS/HTML apps intended to integrate with gStudio. Data generated will get saved under defined folder hierarchy as JSON file.


### Implementation Objectives:
- It should be easy to embed in multiple activity pages.
- It should play as like other interactives within activities.
- While students playing the interactive, it should track each and every step and log those detailed data along with inputs and each iterations.
- User Generated Data (UGD) should get persists to server.
    - Data persistance should happen at following events:
        1. On click of `Finish` button.
        2. Before user leaving page.
        3. After fixed configured period (e.g: 2 min).
- UGD is **CREATE only** for research purpose, which is not intended to get Read/Update/Delete within/via platform UI.
    - UGD will get stored as JSON file under `/data/gstudio_tools_logs/<tool-name>` folder in server.
        - Following is exemplar hierarchy:
        ```
            <tool-name>
            ├── 5-180212162952.json
            ├── 5-180212163000.json
            ├── 65-180212163022.json
            ├── 65-180212163023.json
            ├── 98-180212163009.json
            └── 98-180212163025.json
        ```


### Steps to achieve:
- Data should be collected in JSON format. **(TODO: Confirm JSON schema along with key nomenaclature/convention and value datatype)**
- Provide following JS methods to:
    - Create a Unique Token Key (UTK).
        - Format: USERID-YYMMDDHHMMSS
        - User id is in cookies with key: `user_id` which needs to be pick up by JS method.
    - Get JSON data at any given time.
    - Add/Update additional metadata (AMD) in same JSON data. *(TODO: Decide on AMD schema and fields)*
        - Gstudio to provide JS method giving context of current activity at any given page.
    - POST AJAX method to push UGD in gstudio server.
        - This method should take following arguments *(arguments can be taken via iframe query url or URI seperator, `#`)*:
            1. Data saving end point url
            2. Time in minutes, after which periodic writing should happen to gstudio end-point/server. 
        - POST data:
            1. UGD
            2. AMD
            3. UTK
    - An event listner method which will listen to any of above specified (3) events and trigger POST AJAX method.


### Interactive features requests:
#### **PHASE - I**
- Taking input from user and rendering result.
- Tracking each and every user actions and persisting data in JSON form.

#### **PHASE - II**
- **Responsiveness**
    > Any action like a button click, should result in some visible change somewhere - the users should not have to wait and press more buttons to see the effect.
    - Can we use soft CSS/JS volatile popups to explicit user actions?

- **Permissiveness**
    > Should not gray out all buttons and at any time give control to the user. We should expect the user to do reasonable things at all times. No taking away control.
    - Can we have *play/edit* and *view-only* behavior? Which can be configured by passing URI parameter. 

- **Consistency** 
    > Should give a similar look and feel across interactives, nothing more nothing less. We cannot expect the user to learn to map a new set of actions to some existing button types with which he/she had earlier associated something else. Also about the placement of buttons...
    - Making a provision to override CSS. Enabling custom CSS skin to interactive.


### Pending/TODO:
- AMD schema
- gstudio: end point for UGD saving (via POST AJAX).
    + After JSON data file creation, subsequent writting may happen multiple times 
    + Check for UTK in POST data. If present override existing JOSN file or create a new one.
- Create template to render interactives like `node_ajax_content.html`, which will have necessary styles, JS methods.
    + All the interactives will render with `index.html` as default. If this is not the case, custom template name should be provided to key `index` while including this template.
<!-- - Interactive tool name -->


### Glossary:
- UTK: Unique Token Key
- UGD: User Generated Data 
- AMD: Additional MetaData 