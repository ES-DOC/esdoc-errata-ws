--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)

-- Started on 2022-12-08 12:47:06 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3528 (class 0 OID 46760)
-- Dependencies: 211
-- Data for Name: tbl_issue; Type: TABLE DATA; Schema: errata; Owner: errata_dbuser_admin
--

COPY errata.tbl_issue (id, row_create_date, row_update_date, project, institute, uid, title, description, severity, status, moderation_status, moderation_window, created_by, created_by_email, created_date, updated_by, updated_date, closed_by, closed_date) FROM stdin;
\.


--
-- TOC entry 3534 (class 0 OID 46802)
-- Dependencies: 217
-- Data for Name: tbl_issue_facet; Type: TABLE DATA; Schema: errata; Owner: errata_dbuser_admin
--

COPY errata.tbl_issue_facet (id, row_create_date, row_update_date, project, issue_uid, facet_type, facet_value) FROM stdin;
\.


--
-- TOC entry 3532 (class 0 OID 46786)
-- Dependencies: 215
-- Data for Name: tbl_issue_resource; Type: TABLE DATA; Schema: errata; Owner: errata_dbuser_admin
--

COPY errata.tbl_issue_resource (id, row_create_date, row_update_date, issue_uid, resource_type, resource_location) FROM stdin;
\.


--
-- TOC entry 3530 (class 0 OID 46772)
-- Dependencies: 213
-- Data for Name: tbl_pid_service_task; Type: TABLE DATA; Schema: errata; Owner: errata_dbuser_admin
--

COPY errata.tbl_pid_service_task (id, row_create_date, row_update_date, action, status, issue_uid, dataset_id, error, try_count, "timestamp") FROM stdin;
\.


--
-- TOC entry 3545 (class 0 OID 0)
-- Dependencies: 216
-- Name: tbl_issue_facet_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: errata_dbuser_admin
--

SELECT pg_catalog.setval('errata.tbl_issue_facet_id_seq', 1, false);


--
-- TOC entry 3546 (class 0 OID 0)
-- Dependencies: 210
-- Name: tbl_issue_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: errata_dbuser_admin
--

SELECT pg_catalog.setval('errata.tbl_issue_id_seq', 1, false);


--
-- TOC entry 3547 (class 0 OID 0)
-- Dependencies: 214
-- Name: tbl_issue_resource_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: errata_dbuser_admin
--

SELECT pg_catalog.setval('errata.tbl_issue_resource_id_seq', 1, false);


--
-- TOC entry 3548 (class 0 OID 0)
-- Dependencies: 212
-- Name: tbl_pid_service_task_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: errata_dbuser_admin
--

SELECT pg_catalog.setval('errata.tbl_pid_service_task_id_seq', 1, false);


-- Completed on 2022-12-08 12:47:06 CET

--
-- PostgreSQL database dump complete
--

