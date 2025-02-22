# Process Manager UI

This provides:

- An index page containing:
    - a table displaying the currently running processes.
    - a feed showing broadcast messages from the topics `control.*.process_manager`.
    - action buttons that allow calling the `restart`, `kill` and `flush` functions of
      the process manager.
- A view displaying the logs of an individual process.
- A view providing a form collecting data for use with the process manager `dummy_boot`
  function (for use in development).

The view functions for this UI are split into three categories:

- `pages` that load a full page.
- `partials` that load items within a page.
- `actions` that proxy requests to the process manager.

## Index Page

As the most complex part, some more information is provided here about the index page.

The page is composed primarily of two columns with the message feed on the right. The
left contains a row of buttons for performing actions on processes, a search bar for the
process table and the process table itself.

### Process Table

To keep the process table in sync with the system state the table is updated
periodically. The table is rendered via a partial view function that is polled on an
interval via HTMX.

Search of the table is also implemented via HTMX. Typing into the text input triggers a
call to the process table partial view function which includes the search query. A new
version of the table is returned containing only those entries that match the search
query.

A small amount of client side behaviour is implemented via Hyperscript to:

1. make the table checkboxes behave as a group with the header checkbox accurately
   reflecting the state of the row checkboxes.
1. disable/enable the action buttons based on whether any checkboxes are selected or
   not.

### Message Feed

Similarly to the process table, the message feed is updated periodically to display new
messages received. This is implemented in an equivalent manner with a partial function
polled by HTMX.

Search of messages is also implemented in an equivalent manner to the process table via
a text input which updates the feed when typed into.

The message feed can be hidden by the user by clicking an 'X'. This behaviour is
implemented on the client side by using Hyperscript to toggle the visibility of the feed
element.
