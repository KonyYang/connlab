# Project Library

The page queries the current **Materials library folder** and **Project default save location**.
Entering the page, submitting a search, and Refresh start a cancellable background scan. Typing
and changing filters use the existing lightweight index. Each request checks the active Settings
paths. An unavailable root produces a path-specific warning while the other root remains usable.

Each direct child directory appears once, independently of project registration or duplicate LTR
numbers. A folder named `DL-YYYY-MM-NNN Description` supplies its own description. For a bare
number, the browser uses the unique description from a direct child with the same number.
Unmatched and ambiguous descriptions display as a dash. Folders without an LTR show their
folder name as the description. The outer folder remains the browse root, including its siblings
of the described child. Search covers these labels and filenames, without opening documents.

The path and two-column list identify the selected folder. Double-click or Enter opens a file.
The folder icon on a file row opens its containing directory. Folder access revalidates paths,
excludes internal storage, and rejects links and traversal. Browsing requires no current project
or copy session. Receive materials still archives a selected external folder at the configured
materials location through the existing confirmation and recovery workflow.

Directory index records use separately namespaced identities in the existing derived index.
They confer no project or receipt ownership. Former registrations, receipts and recovery history
are retained. Old navigation links may resolve only to an outer folder within the current roots.
