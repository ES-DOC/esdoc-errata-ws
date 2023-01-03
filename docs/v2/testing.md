# ERRATA v2 Service Testing

## Introduction

A key feature of the ES-DOC Errata service v2 is the ability of anonymous users to propose new errata.  All proposed errata must be reviewed by a moderator, who may either accept or reject the proposed errata.  Communication between anonymous users and moderators is via email.

## Pre-Requisites

1.	Ensure that you have a GitHub account that has been registered as a member of the following team:

	https://github.com/orgs/ES-DOC-INSTITUTIONAL/teams/errata-moderation

2.	Ensure that you know how to clear your browser's session cookies for the following TEST site:

	https://test-errata-v2.es-doc.org


### Test 001  Propose new errata

0.	Apply pre-requisites.

1.  Navigate to homepage as an `anonymous` user.

	1.1	If you have previously successfully logged into the application as an authenticated user then you will need to clear your browser's Errata application session cookies.

2.	Press the `Propose` button in page menu bar.

	2.1	You will be directed to the errata edit page.

3.	Enter details of the errata to be proposed.

	3.1 The details to be entered are the same as with version 1 of the system except that you will obliged to enter an email address.

4.	When ready press the `Save` button to persist the entered details.

	4.1	The errata details will be saved to the service's database.

	4.2	You will receive an email informing you that a moderator will review your errata in due course.

	4.3	Verify receipt of email and navigate to the view errata URL contained within the email.
 