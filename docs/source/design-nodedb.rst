Node Task Registry Design
=========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


****************************
Node Task Registry Design
****************************

##### Basic Task Design
Warble Nodes can have one or more (or all) tasks assigned to it. Each
task consists of a target to test, as well as what to test and how to go
about that, encapsulated in a payload object. Each check you wish to
perform requires an associated task, but may be performed by multiple
nodes. Thus, testing whether your main web site works on port 80
requires a task, as does a test for https on port 443, as they are
technically two distinct targets. Specific tasks may have optional tests
built into them,for instance a SSL certificate check on a https site.

##### Task Categories
Each task is assigned a task category, which helps you separate tasks into
easily recognizable groups and access definitions.

Each task category has a distinct alerting and escalation path, meaning
you can assign different teams to different categories, and have alerts
go to that team, independent of other task categories. This can be
useful for having front-end issues go to a specific team, while back-end 
issues go to another team.

##### Task Category Access
Users can be assigned the following access levels to categories, on a
per-user basis:

1. Read-only access: The user can read and analyze test results, but
   cannot edit or remove tasks, nor see the specific payload details (thus,
   if you add a test with credentials, users with read-only access cannot
   see the credentials)

2. Read/write access: The user can read, modify, and remove existing
   tests. They can also add new tests to the category.

3. Admin access: The user can, besides permissions listed above, also modify or
   remove the category altogether or change its alerting options. This access
   level should generally be reserved for power users only.

It should be noted that _super users_ on the system (such as the account
you create at setup) can freely access and modify any aspect of the
tasks/categories.


