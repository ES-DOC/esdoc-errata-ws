# ERRATA v2 Service Testing

## Introduction

A key feature of the ES-DOC Errata service v2 is the ability of anonymous users to **propose** new errata.  All proposed errata are formally reviewed by a moderator, who can either accept or reject the proposed errata.  Communication between an anonymous user and a moderator is via email.

## Pre-Requisites

1.	Ensure that you have a GitHub account that has been registered as a member of the following team:

	https://github.com/orgs/ES-DOC-INSTITUTIONAL/teams/errata-moderation

2.	Ensure that you know how to clear your browser's session cookies for the following TEST site:

	https://test-errata-v2.es-doc.org


## Test 001: Propose new errata

0.	Apply pre-requisites.

1.  Navigate to homepage as an `anonymous` user.

2.	Press the `Propose` button in page menu bar.

	2.1.	You will be directed to the errata edit page.

3.	Enter details of the errata to be proposed.

	3.1.	The details to be entered are the same as with version 1 of the system except that you will obliged to enter an email address.

4.	When ready press the `Save` button to persist the entered details.

	4.1.	The errata details will be saved to the service's database.

	4.2.	You will receive an email informing you that a moderator will review your errata in due course.

	4.3.	Verify receipt of email and navigate to the view errata URL contained within the email.


## Test 002: Accept new errata

0.	Apply pre-requisites.

1.  Navigate to homepage as an `anonymous` user.

	1.1.	Press the `Login` button in page menu bar.

	1.2.	Authenticate via GitHub OAuth with GitHub user registered in `errata-moderation` team.

2.	Press the `Moderate` button in page menu bar.

	2.1.	You will be directed to the errata moderation search page.

	2.2.	A list of errata in various moderation states will be displayed.

	2.3.	Select an errata proposed in `Test 001`.

	2.4.	You will be directed to the edit errata page.

3.	Moderate proposed errata.

	3.1.	Click on `Moderate` button in page menu bar.

	3.2.	Select `Accept` sub-menu.

	3.3.	Verify application displays a confirmation message.

	3.4.	Verify system sends an email to anonymous user that proposed the accepted errata.

4.	Return to moderate page.

	4.1.	Verify that errata's moderation status has indeed been updated.
