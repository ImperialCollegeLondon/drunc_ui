# Controller UI

This provides:

- An index page containing:
    - a table displaying the current state of the finite state machine (FSM) and buttons
    to run the possible transitions.
    - a collapsible tree showing the running applications and their relationship.
    - a feed showing broadcast messages from the topic `erskafka-reporting`.
- A view displaying a more detailed table with the application tree

The view functions for this UI are split into two categories:

- `pages` that load a full page.
- `partials` that load items within a page.

## Index Page

The index page contains three columns, the contents for each of them contained in a
separate template file and loaded via a partial view. Left to right, the columns contain
the finite state machine, the applications tree and the message feed.

### Finite State Machine (FSM)

The finite state machine describes the current state of the system, the possible transitions
from this state and where they lead, with all other possible transitions and states greyed out.
It represents the states and the main transitions described in the [drunc documentation], excluding the sequences.

The FSM diagram is built with `django-tables2`, with the elements for each row and columns
defined in the backend based on a **hardcoded** version of the real FSM used by `drunc`.
This is done this way since `drunc` provides no way of extracting the architecture of the
FSM machine dynamically, which also means that, potentially, they both (frontend and drunc)
might become incompatible if the actual FSM is changed but the hardcoded version in the
frontend is not updated accordingly.

When clicking on a transition, a pop-up modal dialog opens to input the arguments (required
or optional) to run the transition, and to confirm it. The code for the dialog is contained
in another partial view and template. The arguments required for each transition are pulled dynamically from
`drunc` and put together in a `django` form.

The table updates only when loading the page and when trying to execute a transition;
there is no automatic refresh via HTMX.

### Applications tree overview

The application tree overview shows the hierarchy of applications, with their children,
grandchildren, etc. It pulls this information from the controller driver `status`
recursively, and displays it using a [Shoelace tree component].

Shoelace javascript (JS) code is NOT added to the repository, like it has been done for other
more self-contained JS dependencies, meaning that **the application tree will not work**
**if internet access is not available at runtime**.

Like with the FSM, there is no automatic refresh via HTMX.

The title of the application tree card is an hyperlink that opens the dedicated [applications tree page].

### Message Feed

Similarly to the message feed in the [process manager]
this is updated periodically to display new messages received. This is implemented in
an equivalent manner with a partial function polled by HTMX. In this case, only messages
from the topic `erskafka-reporting` are displayed.

Search of messages is also implemented in an equivalent manner to the process table via
a text input which updates the feed when typed into.

## Application tree page

This page shows the same hierarchy of applications running in the system than in the
overview page but in tabular form (using `django-tables2`), fully expanded, and giving
information about the `hostname` of the application and the `detector` that each
application is linked to, if any.

The `detector` information is pulled directly from the controller driver recursively,
while the `hostname` needs to be requested via the `process manager`, which involves a
probably unwanted cross application dependency at least for now.

This page has no dynamic behaviour to care about and, contrary to the [application tree overview], it does not depend on Shoelace and therefore will work
correctly even without internet access at runtime.

[drunc documentation]: https://github.com/DUNE-DAQ/drunc/wiki/FSM
[Shoelace tree component]: https://shoelace.style/components/tree
[applications tree page]: #application-tree-page
[application tree overview]: #applications-tree-overview
[process manager]: process_manager.md#message-feed
