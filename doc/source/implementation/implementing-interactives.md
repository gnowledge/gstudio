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
    - UGD will get stored as JSON file under `/data/gstudio_tools_logs/<tool-name>` folder in server.
        - Following is exemplar hierarchy:
        ```
            <tool-name>
            ├── 0-<tool-name>.json
            ├── 5-<tool-name>.json
            ├── 66-<tool-name>.json
            └── 98-<tool-name>.json
        ```


### II. Steps to achieve:
- Data will be collected in JSON format. **(TODO: Confirm JSON schema along with key nomenaclature/convention and value datatype)**
- Provide following JS-methods to:
    - Create a Unique Token Key (UTK).
        - Format: USERID-LANGCODE-YYMMDDHHMMSS
            - It is combination of following 3 values:
                1. USERID (e.g: *66*)
                2. LANGCODE (e.g: *hi*)
                3. YYMMDDHHMMSS (e.g: *180212163009*)
            - USERID and LANGCODE is in [cookies](../cookie.html) with key: `user_id` and `language_code` respectively. Which needs to be pick up by JS method.
        - *Note: Anonymous user will have `0` User Id, cookie will have value `0`*
    - Get JSON data at any given time.
    - Add/Update additional metadata (AMD) in same JSON data. *(TODO: Decide on AMD schema and fields)*
        - Pending: Gstudio to provide JS method giving context of current activity at any given page.
    - POST AJAX method to push UGD in gstudio server.
        - This method should take following arguments *(arguments can be taken via iframe query url or URI seperator, `#`)*:
            - Data saving end point url: `/tools/logging/`
        - POST data:
            - UGD having key-name, `"payload"`:
                - Core interactive data having key-name: `"appData"`
                - AMD having following key-name:
                    - `"createdAt"`: `"<YY-MM-DD HH:MM:SS>"`
                        - Example value, `"18-02-12 16:30:09"`
                        - e.g. `"createdAt"`: `"18-02-12 16:30:09"`
                    - `"language"`: `"<2/3 digit locale/language code>"`
                        - Pick it from cookie having key, `language_code`
                        - Example value, `"en"`
                        - e.g. `"language"`: `"en"`
                    - `"userId"`: `"<integer user Id>"`
                        - Pick it from cookie having key, `user_id`
                        - Example value, `"12345"`
                        - e.g. `"userId"`: `"1234"`
                    - `"buddyIds"`: `"<int buddy ids concatinated by &>"`
                        - Pick it from cookie having key, `buddy_ids`
                        - Example value, `"12345&1417"`
                        - e.g. `"buddyIds"`: `"12345&1417"`
                    - `"appName"`: `<"Name of app/interactive">`
                        - Example value: `"policequad"`
                        - e.g. `"appName"`: `"policequad"`
                    - (*optional*) `"appUTK"` : `"USERID-LANGCODE-YYMMDDHHMMSS"`
                        - Example value, `"66-en-180411132056"`
                        - e.g. `"appUTK"`: `"66-en-180411132056"`
            - `"csrfmiddlewaretoken"`: `"csrftoken"`
                - pick it from cookie having key, `csrftoken`
                - Example value, `"fBIqmJXByqDrWUochThtKNyE7DrVr9RB"`
                - e.g. `"csrfmiddlewaretoken"`: `"fBIqmJXByqDrWUochThtKNyE7DrVr9RB"`
            - Example:
            ```
            {
                "payload":
                {
                    "appData":
                    {
                        // this will have all data
                        // generated from interactive/app
                        // in JSON format.
                    },
                    "appName": "policequad",
                    "language": "en",
                    "createdAt": "18-02-12 16:30:09",
                    "userId": "1234",
                    "buddyIds": "12345&1417"
                },
                "csrfmiddlewaretoken": "fBIqmJXByqDrWUochThtKNyE7DrVr9RB"
            }

            ```
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