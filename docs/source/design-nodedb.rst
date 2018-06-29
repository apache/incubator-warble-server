Node Task Registry Design
=========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


****************************
Node Tasks
****************************

#####################
Basic Task Design
#####################
Warble Nodes can have one or more (or all) tasks assigned to it. Each
task consists of a target to test, as well as what to test and how to go
about that, encapsulated in a payload object. Each check you wish to
perform requires an associated task, but may be performed by multiple
nodes. Thus, testing whether your main web site works on port 80
requires a task, as does a test for https on port 443, as they are
technically two distinct targets. Specific tasks may have optional tests
built into them,for instance a SSL certificate check on a https site.

#####################
Task status
#####################
A task can be either enabled, disabled, or muted. Disabling a task
prevents it from running on nodes, whereas muting a task will still
cause nodes to perform it, but alerting will be silenced. Muting can be
used for when you still need to monitor a situation, but you don't need
to be reminded whenever the test results changes.

#####################
Task sensitivity
#####################
A task can also have a specific sensitivity set. Sensitivity denotes
how failures are treated, and when to alert about state changes:

- **low**: Alerting only happens if all currently active nodes agree that
  the test has failed, e.g. the service is down completely.

- **default**: Alerting happens if a majority of nodes agree that the test
  has failed. This is the default behavior and balances out the need for
  speedy alerting versus the need for fewer false positives.

- **high**: Alerting happens if more than one node sees failures. While
  more sensitive than the default, it still removes a fair bit of false
  positives by requiring confirmation of a reported failure by at least
  one other node.

- **twitchy**: Alerting happens if any node registers a failure.
  This may be useful for services that have guaranteed service level
  agreements, but can lead to a lot of false positives.

It should be noted that if you run a setup of Warble with only one, or
very few nodes attached, the sensitivity levels may differ very little
in terms of when alerting happens, as the definition of quorum changes
based on how many active nodes you have at any given time.

*******************
Task Categories
*******************
Each task is assigned a task category, which helps you separate tasks
into easily recognizable groups and access definitions.

Each task category has a distinct alerting and escalation path, meaning
you can assign different teams to different categories, and have alerts
go to that team, independent of other task categories. This can be
useful for having front-end issues go to a specific team, while back-end 
issues go to another team.

#####################
Task Category Access
#####################
Users can be assigned the following access levels to categories, on a
per-user basis:

1. Read-only access: The user can read and analyze test results, but
   cannot edit or remove tasks, nor see the specific payload details
   (thus, if you add a test with credentials, users with read-only
   access cannot see the credentials)

2. Read/write access: The user can read, modify, and remove existing
   tests. They can also add new tests to the category.

3. Admin access: The user can, besides permissions listed above, also
   modify or remove the category altogether or change its alerting
   options. This access level should generally be reserved for power
   users only.

It should be noted that `super users` on the system (such as the account
you create at setup) can freely access and modify any aspect of the
tasks/categories.


