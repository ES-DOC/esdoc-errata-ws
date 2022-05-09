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

    - a set of web-pages implemented in JavaScript;
    - a set of interactions with GitHub OAuth.

### Web-API

    - a set of open RESTful end-points;
    - a sub-set of end-points requiring GitHub OAuth authentication,

### Database

    - a set of PostGreSQL tables;
    - a set of dB management scripts.

## New System - User Roles

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

## Development Outline

The updated system will extend the above layers as follows:

### User-Interface:

    - New page: moderator dashboard;
    - Accept/Reject actions added to existing view page;
    - New GitHub scope: read:email.
    - Errata edit page extensions;

### Web-API:

    - New endpoint: 1/errata/moderate
    - New sub-system: notifications

### Database:

    - New Column: tbl_errata.moderation_status (accepted | not_required | rejected)
    - New Column: tbl_errata.email_of_creator
    - New table: tbl_notifications
