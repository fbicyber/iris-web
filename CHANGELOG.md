This list consists of all the changes made to the FBI Cyber's fork of Iris.

## v2.5.3 - October 6, 2026

### Changes
- Fixed 39 CISA Vulnerabilities
- Added spatial 3D view for the graph tab as an option
- Hide create date by default on the Timeline table
- Allow searching on all fieds on the Timeline table
- Added nginx timestamp to approved event date validator

## v2.5.2 - September 1, 2026

### Features
- Added 508 Compliance to the UI.
- Added right click modal update for multiple items selected.

### Bug Fixes
- Fixed when creating IOCs, some fields are ignored.
- Fixed when case notes only shows collaborator changes after refresh

### Changes
- Save state for toggling columns in case module grids.
- Update the title and button names in notes for renaming/creating folders.
- Added a warning status to IOC duplicate issue

## v2.5.1 - June 22, 2026

### Features
- Added manual way to add alerts.
- Added create date to Timeline table.
- Added ability to add screenshots to IOC and Timeline items.
- Added UI msg why saving case failed if not customer data supplied.
- Deployed vulnerability scanning to code releases.
- Deployed code quality scanning to code releases.
- Removed unnecessary Case ID field when creating a new case.
- Added paging selection at the top of the Timeline table.
- Added nanoseconds to auto parser in Timeline modal.
- Added more options to Show Entries on Timeline page.

### Bug Fixes
- Fixed case access column that was not filterable/sortable in manage case access modal.
- Fixed status column in Tasks list that was not sortable if you sorted by a different column first.
- Fixed notes from unfolding when renaming folders.
- Fixed invalid date issue when using date selector during event creation

### Changes
- Made events now have a single line per pair of nodes in graph.
- When leaving notes with an edit, it will now auto save.
- Host has been added as field in register evidence modal.
- Added "VM Image - Windows Workstation" as new evidence type in register evidence modal.
- Added "Unknown" and "Other" as new asset types

## v2.5.0 - May 5, 2026

### Features
- Extend the report generate timeout for long running tasks.
- When generating a report, it now uploads the document to an object storage.
- View Reports button now added that holds all generated reports.
- Indicate status for report generation in progress.
- Adding event to timeline now allows the UTMP dump unique timestamp.
- Add ability to drag and change the timeline table's columns width.
- Add a no color option to events on timeline.
- Add more colors to the timeline colors options.
- Display if an event currently has "add to summary" toggle on.
- Add ability to duplicate an event from the right click menu.
- Introduce start-end times for events.
- Add Light/Dark mode button at the top of the app.
- Add "Are you sure" to the delete button for all modals in the Case Section.
- Add Right-click menu/option to edit nodes/edges in graph.
- Toggle show in graph for assets and IOCs.
- Add Release Notes to Iris.

### Bug Fixes
- Fix bug on selecting the first color for an event in the timeline table.
- Fix Bug that has disappearing filter in Assets, IOC and Evidence.
- Missing event ID in timeline right-click menu.
- Fix bug in timeline that scrolls to top after taking update actions.

### Changes
- Timestamps in Timeline View line break more user-friendly.
- Apply bulleted list to existing description in editor instead of clearing out the highlighted content in all description editors (Asset, IOC, Timeline, Task, ...).
- Fix alembic migration hanging for new revisions by adding factory pattern.
- Create a pipeline to automate all the manual deployment tasks into the GitLab CI/CD pipeline.
- Investigate how to implement Cytoscape instead of vis to display graph.
- Make event line colors in graph match colors in timeline.

## v2.4.20 - October 21, 2025

### Features 
- Users can now toggle between showing and hiding columns on the Timeline. 
- Users can now add multiple internal and external IPs to an Asset. 
- New Local Timezone dropdown on Timeline page to allow user to select the appropriate local time and calculate the UTC and Local timestamps more accurately. 
- Assets and IOCs are now additional sheets when using the Timeline Excel export. 
- If user does not add timezone in their Event timestamp, it defaults to UTC and warns the user. 
- Timeline has Excel import and export available. 
- IOCs are now added to the graph view.
- Users can create IOCs and Assets when creating/updating an event from the event modal.
- Users can import/export an Excel sheet of Evidence items into the Evidence table.

### Bug Fixes 
- Iris can now display Event descriptions with HTML Tags properly. 
- Fixed a bug that prevented users from deleting Timeline Events. 
- Fixed a bug that made the Timeline table stretch off screen when having longer event titles. 
- Using the Filter on the Events Timeline no longer switches the active case. 
- Upon hitting Enter on the empty search box, users are no longer routed back to case #1. 
- Fixed a bug where event description with JSON caused an error for the entire timeline table.
- Fixed UTC timestamps bugs when updating, but making no changes to the timestamps modified the event’s timestamp to local time.

### Changes 
- Iris updated to v2.4.20. 
- Default time input for Events is now the string input auto parser, and the calendar style input is now secondary option. 
- Simpler search bar in the Timeline that automatically displays rows containing searched keywords, alleviating the burden to have to learn additional filtering syntax. 
- Local browser cache of graph nodes to enable graph persistence between sessions. Graph nodes stay in the same position that user places them in, after refreshing page or switching tabs.
- Comments for an event in Timeline are now bigger/more visible. 
- Multiselect in the Events timeline was changed to avoid accidentally selecting multiple items. The following is how to multiselect now: 
  - Shift + Click highlights all the rows in between the 1st and 2nd row click (select a range of items).  
  - CTRL + Click highlights the exact rows you click (select/deselect individual items). 
  - Right click highlights the exact rows you click (like CTRL + Click). 
  - Left click selects a single item. If you left click with multiple items selected, it will unselect all of them and just select the one left clicked on. 
- Timestamps in Events Timeline table no longer display milliseconds. 
- Added the search bar to the Evidence page for consistency. 
- Event categories are now displayed in alphabetical order. 
- The Host column of the Timeline table now only includes the asset name (asset type was removed). 
- Timeline table padding was decreased in multiple spots to increase the amount of data visible on the screen. 
- Errors that occur when uploading an excel sheet of Events are now displayed on the UI.
- 24 hour time is now the default view when adding an Event.