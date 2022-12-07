# ES-DOC Errata v2.0 Design Document

## Introduction

The ES-DOC Dataset Errata service has been in service since 2019.  At it's inception the intent was to permit authenticated & authorised authors (typically data-node administrators) to create errata & upload associated PID information.  Whilst unauthenticated users had search & view rights, it was never intended that they would be able to create errata.  The system has worked quite well, particularly within the context of CMIP6.

In order to further promote usage of the errata system, it is proposed to extend errata creation rights to unauthenticated users.  The assumption is that by extending such rights, more errata will be reported to the benefit of the community as a whole.  In order to defend the system against spam and quality issues, it will be necessary to introduce a formal review mechanism into the errata creation process.

The review process will be driven by a new type of user, a moderator.  Once an unauthenticated user has created an Errata, a moderator will need to perform a review within a reasonable (but extendable) timeframe.  It is assumed that creator & moderator will communicate via email, i.e. a creator must specify their email at the point of errata creation.  The review outcome is binary, i.e. acceptance or rejection.  Only accepted errata will be available to unauthenticated users for search & view.  

The majority of the new work will involve the introduction of a notification sub-system plus several extensions to the existing user-interface.  A new test environment will be established within the existing ES-DOC web-hosting environment.  Testing will be progressive and will leverage the wider ES-DOC community when & where appropriate.

## Existing System

At a high level the existing system can be summarised as follows: 

### User Roles

- Author
  - Authenticated
  - Typically a data-node administrator
  - GitHub account is white-listed

- Public
  - Anonymous
  - Typically a researcher

### User-Interface

- A set of web-pages implemented in JavaScript;
- A set of interactions with GitHub OAuth.

### Web-API

- A set of open RESTful end-points;
- A sub-set of end-points requiring GitHub OAuth authentication,

### Database

- A set of PostGreSQL tables;
- A set of dB management scripts.

## New System - User Roles

In the new system the set of supported user roles will be extended.  A new **moderator** role will join the existing **public** and **author** roles.

### Author

An **authenticated** user authorised to perform the following actions:

- Errata - Create
- Errata - Edit
- Errata - Search
- Errata - View
- PID - Search

### Moderator

An **authenticated** user authorised to perform the following actions:

- Errata - Accept
- Errata - Edit
- Errata - Extend Moderation Window
- Errata - Reject
- Errata - Search
- Errata - View
- PID - Search

### Public

An **anonymous** user authorised to perform the following actions:

- Errata - Create
- Errata - Search
- Errata - View
- PID - Search

## New System - User-Interface

In the new system the user interface will be extended to support the moderation process.

- New Page
  - Moderator Dashboard
  - Allows moderator to see all errata requiring moderation

- New GitHub Scope
  - Scope name: read:email
  - Applies to moderators only
  - Allows system to auto-email moderators

- Update Page
  - Edit Errata
  - New action: Accept Errata

- Update Page
  - Edit Errata
  - New action: Reject Errata

- Update Page
  - Edit Errata
  - If user role is public then prompt for email address;

## New System - Web-API

- New endpoint
  - BASE_ADDRESS/1/errata/moderation/accept
  - Set errata status -> Accepted
  - Send email notification -> Author

- New endpoint
  - BASE_ADDRESS/1/errata/moderation/extend
  - Set errata moderation time window
  - Send email notification -> Author

- New endpoint
  - BASE_ADDRESS/1/errata/moderation/reject
  - Set errata status -> Rejected
  - Send email notification -> Author

- New sub-system: notifications
  - Support automated email of moderation decisions
  - Email 1: Errata Accepted
  - Email 2: Errata Extended
  - Email 3: Errata Rejected

## New System - Database

- New Column
  - Table: tbl_errata
  - Name: moderation_status
  - Constraint: allowed values = accepted | in_review | not_required | rejected

- New Column
  - Table: tbl_errata
  - Name: moderation_window
  - Constraint - valid timestamp

- New Column
  - Table: tbl_errata
  - Name: email_of_creator
  - Constraint - valid email address

- New Table
  - Table: tbl_notification
  - Description: Stores details injected into email templates

- New Table
  - Table: tbl_notification_template
  - Description: Stores email templates as text blobs

- New Cron Job
  - Delete rejected errata N days after rejected
