This list consists of all the changes made to the FBI Cyber's fork of Iris.

## Features 
- Users can now toggle between showing and hiding columns on the Timeline. 
- Users can now add multiple internal and external IPs to an Asset. 
- New Local Timezone dropdown on Timeline page to allow user to select the appropriate local time and calculate the UTC and Local timestamps more accurately. 
- Assets and IOCs are now additional sheets when using the Timeline Excel export. 
- If user does not add timezone in their Event timestamp, it defaults to UTC and warns the user. 
- Timeline has Excel import and export available. 
- IOCs are now added to the graph view.

## Bug Fixes 
- Iris can now display Event descriptions with HTML Tags properly. 
- Fixed a bug that prevented users from deleting Timeline Events. 
- Fixed a bug that made the Timeline table stretch off screen when having longer event titles. 
- Using the Filter on the Events Timeline no longer switches the active case. 
- Upon hitting Enter on the empty search box, users are no longer routed back to case #1. 


## Changes 
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