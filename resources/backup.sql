--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)

-- Started on 2023-01-03 20:12:36 CET

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
-- TOC entry 5 (class 2615 OID 47049)
-- Name: errata; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA errata;


ALTER SCHEMA errata OWNER TO postgres;

--
-- TOC entry 836 (class 1247 OID 47070)
-- Name: IssueModerationEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."IssueModerationEnum" AS ENUM (
    'accepted',
    'in-review',
    'not-required',
    'rejected'
);


ALTER TYPE errata."IssueModerationEnum" OWNER TO test_db_errata_2;

--
-- TOC entry 839 (class 1247 OID 47080)
-- Name: IssueResourceTypeEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."IssueResourceTypeEnum" AS ENUM (
    'url',
    'material',
    'dataset'
);


ALTER TYPE errata."IssueResourceTypeEnum" OWNER TO test_db_errata_2;

--
-- TOC entry 830 (class 1247 OID 47051)
-- Name: IssueSeverityEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."IssueSeverityEnum" AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);


ALTER TYPE errata."IssueSeverityEnum" OWNER TO test_db_errata_2;

--
-- TOC entry 833 (class 1247 OID 47060)
-- Name: IssueWorkflowEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."IssueWorkflowEnum" AS ENUM (
    'new',
    'onhold',
    'resolved',
    'wontfix'
);


ALTER TYPE errata."IssueWorkflowEnum" OWNER TO test_db_errata_2;

--
-- TOC entry 842 (class 1247 OID 47088)
-- Name: PIDActionEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."PIDActionEnum" AS ENUM (
    'insert',
    'delete'
);


ALTER TYPE errata."PIDActionEnum" OWNER TO test_db_errata_2;

--
-- TOC entry 845 (class 1247 OID 47094)
-- Name: PIDTaskStateEnum; Type: TYPE; Schema: errata; Owner: test_db_errata_2
--

CREATE TYPE errata."PIDTaskStateEnum" AS ENUM (
    'complete',
    'error',
    'queued'
);


ALTER TYPE errata."PIDTaskStateEnum" OWNER TO test_db_errata_2;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 211 (class 1259 OID 47102)
-- Name: tbl_issue; Type: TABLE; Schema: errata; Owner: test_db_errata_2
--

CREATE TABLE errata.tbl_issue (
    id integer NOT NULL,
    row_create_date timestamp without time zone NOT NULL,
    row_update_date timestamp without time zone,
    project character varying(63) NOT NULL,
    institute character varying(63) NOT NULL,
    uid character varying(63) NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    severity errata."IssueSeverityEnum" NOT NULL,
    status errata."IssueWorkflowEnum" NOT NULL,
    moderation_status errata."IssueModerationEnum" NOT NULL,
    created_by character varying(511),
    created_date timestamp without time zone NOT NULL,
    updated_by character varying(511),
    updated_date timestamp without time zone,
    closed_by character varying(511),
    closed_date timestamp without time zone
);


ALTER TABLE errata.tbl_issue OWNER TO test_db_errata_2;

--
-- TOC entry 217 (class 1259 OID 47144)
-- Name: tbl_issue_facet; Type: TABLE; Schema: errata; Owner: test_db_errata_2
--

CREATE TABLE errata.tbl_issue_facet (
    id integer NOT NULL,
    row_create_date timestamp without time zone NOT NULL,
    row_update_date timestamp without time zone,
    project character varying(63) NOT NULL,
    issue_uid character varying(63) NOT NULL,
    facet_type character varying(63) NOT NULL,
    facet_value character varying(1023) NOT NULL
);


ALTER TABLE errata.tbl_issue_facet OWNER TO test_db_errata_2;

--
-- TOC entry 216 (class 1259 OID 47143)
-- Name: tbl_issue_facet_id_seq; Type: SEQUENCE; Schema: errata; Owner: test_db_errata_2
--

CREATE SEQUENCE errata.tbl_issue_facet_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE errata.tbl_issue_facet_id_seq OWNER TO test_db_errata_2;

--
-- TOC entry 3541 (class 0 OID 0)
-- Dependencies: 216
-- Name: tbl_issue_facet_id_seq; Type: SEQUENCE OWNED BY; Schema: errata; Owner: test_db_errata_2
--

ALTER SEQUENCE errata.tbl_issue_facet_id_seq OWNED BY errata.tbl_issue_facet.id;


--
-- TOC entry 210 (class 1259 OID 47101)
-- Name: tbl_issue_id_seq; Type: SEQUENCE; Schema: errata; Owner: test_db_errata_2
--

CREATE SEQUENCE errata.tbl_issue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE errata.tbl_issue_id_seq OWNER TO test_db_errata_2;

--
-- TOC entry 3542 (class 0 OID 0)
-- Dependencies: 210
-- Name: tbl_issue_id_seq; Type: SEQUENCE OWNED BY; Schema: errata; Owner: test_db_errata_2
--

ALTER SEQUENCE errata.tbl_issue_id_seq OWNED BY errata.tbl_issue.id;


--
-- TOC entry 215 (class 1259 OID 47128)
-- Name: tbl_issue_resource; Type: TABLE; Schema: errata; Owner: test_db_errata_2
--

CREATE TABLE errata.tbl_issue_resource (
    id integer NOT NULL,
    row_create_date timestamp without time zone NOT NULL,
    row_update_date timestamp without time zone,
    issue_uid character varying(63) NOT NULL,
    resource_type errata."IssueResourceTypeEnum" NOT NULL,
    resource_location character varying(1023) NOT NULL
);


ALTER TABLE errata.tbl_issue_resource OWNER TO test_db_errata_2;

--
-- TOC entry 214 (class 1259 OID 47127)
-- Name: tbl_issue_resource_id_seq; Type: SEQUENCE; Schema: errata; Owner: test_db_errata_2
--

CREATE SEQUENCE errata.tbl_issue_resource_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE errata.tbl_issue_resource_id_seq OWNER TO test_db_errata_2;

--
-- TOC entry 3543 (class 0 OID 0)
-- Dependencies: 214
-- Name: tbl_issue_resource_id_seq; Type: SEQUENCE OWNED BY; Schema: errata; Owner: test_db_errata_2
--

ALTER SEQUENCE errata.tbl_issue_resource_id_seq OWNED BY errata.tbl_issue_resource.id;


--
-- TOC entry 213 (class 1259 OID 47114)
-- Name: tbl_pid_service_task; Type: TABLE; Schema: errata; Owner: test_db_errata_2
--

CREATE TABLE errata.tbl_pid_service_task (
    id integer NOT NULL,
    row_create_date timestamp without time zone NOT NULL,
    row_update_date timestamp without time zone,
    action errata."PIDActionEnum" NOT NULL,
    status errata."PIDTaskStateEnum" NOT NULL,
    issue_uid character varying(63) NOT NULL,
    dataset_id character varying(1023) NOT NULL,
    error character varying(1023),
    try_count integer,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE errata.tbl_pid_service_task OWNER TO test_db_errata_2;

--
-- TOC entry 212 (class 1259 OID 47113)
-- Name: tbl_pid_service_task_id_seq; Type: SEQUENCE; Schema: errata; Owner: test_db_errata_2
--

CREATE SEQUENCE errata.tbl_pid_service_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE errata.tbl_pid_service_task_id_seq OWNER TO test_db_errata_2;

--
-- TOC entry 3544 (class 0 OID 0)
-- Dependencies: 212
-- Name: tbl_pid_service_task_id_seq; Type: SEQUENCE OWNED BY; Schema: errata; Owner: test_db_errata_2
--

ALTER SEQUENCE errata.tbl_pid_service_task_id_seq OWNED BY errata.tbl_pid_service_task.id;


--
-- TOC entry 3365 (class 2604 OID 47105)
-- Name: tbl_issue id; Type: DEFAULT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue ALTER COLUMN id SET DEFAULT nextval('errata.tbl_issue_id_seq'::regclass);


--
-- TOC entry 3368 (class 2604 OID 47147)
-- Name: tbl_issue_facet id; Type: DEFAULT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_facet ALTER COLUMN id SET DEFAULT nextval('errata.tbl_issue_facet_id_seq'::regclass);


--
-- TOC entry 3367 (class 2604 OID 47131)
-- Name: tbl_issue_resource id; Type: DEFAULT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_resource ALTER COLUMN id SET DEFAULT nextval('errata.tbl_issue_resource_id_seq'::regclass);


--
-- TOC entry 3366 (class 2604 OID 47117)
-- Name: tbl_pid_service_task id; Type: DEFAULT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_pid_service_task ALTER COLUMN id SET DEFAULT nextval('errata.tbl_pid_service_task_id_seq'::regclass);


--
-- TOC entry 3528 (class 0 OID 47102)
-- Dependencies: 211
-- Data for Name: tbl_issue; Type: TABLE DATA; Schema: errata; Owner: test_db_errata_2
--

COPY errata.tbl_issue (id, row_create_date, row_update_date, project, institute, uid, title, description, severity, status, moderation_status, created_by, created_date, updated_by, updated_date, closed_by, closed_date) FROM stdin;
1	2023-01-03 11:48:10.836329	\N	cmip6	ipsl	986b1346-542b-efb7-a9a5-d4d769b61456	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-2	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-2	low	new	in-review	asladeofgreen@gmail.com	2023-01-03 11:48:10.832527	\N	\N	\N	\N
2	2023-01-03 12:06:09.588748	2023-01-03 18:08:49.577155	cmip6	ipsl	2428b051-e492-6a6c-b079-54576522cfd0	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-3	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-33	low	new	accepted	asladeofgreen@gmail.com	2023-01-03 12:06:09.584714	asladeofgreen	2023-01-03 13:58:59.548205	\N	\N
3	2023-01-03 18:14:27.917277	2023-01-03 18:15:36.116525	cmip6	ipsl	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-4	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605-44	high	new	not-required	asladeofgreen	2023-01-03 18:14:27.913278	asladeofgreen	2023-01-03 18:15:36.114997	\N	\N
\.


--
-- TOC entry 3534 (class 0 OID 47144)
-- Dependencies: 217
-- Data for Name: tbl_issue_facet; Type: TABLE DATA; Schema: errata; Owner: test_db_errata_2
--

COPY errata.tbl_issue_facet (id, row_create_date, row_update_date, project, issue_uid, facet_type, facet_value) FROM stdin;
1	2023-01-03 11:48:10.848846	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	esdoc:errata:project	cmip6
2	2023-01-03 11:48:10.848853	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	esdoc:errata:status	new
3	2023-01-03 11:48:10.848857	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	esdoc:errata:moderation-status	in-review
4	2023-01-03 11:48:10.84886	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	esdoc:errata:severity	low
5	2023-01-03 11:48:10.848862	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:experiment-id	1pctco2
6	2023-01-03 11:48:10.848865	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:activity-id	cmip
7	2023-01-03 11:48:10.848868	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:source-id	ipsl-cm6a-lr
8	2023-01-03 11:48:10.848871	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:institution-id	ipsl
9	2023-01-03 11:48:10.848873	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:table-id	3hr
10	2023-01-03 11:48:10.848876	\N	cmip6	986b1346-542b-efb7-a9a5-d4d769b61456	wcrp:cmip6:grid-label	gr
91	2023-01-03 18:15:36.11728	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	esdoc:errata:project	cmip6
92	2023-01-03 18:15:36.117284	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	esdoc:errata:status	new
93	2023-01-03 18:15:36.117287	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	esdoc:errata:moderation-status	not-required
94	2023-01-03 18:15:36.117288	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	esdoc:errata:severity	high
95	2023-01-03 18:15:36.11729	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:institution-id	ipsl
96	2023-01-03 18:15:36.117292	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:grid-label	gr
97	2023-01-03 18:15:36.117294	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:experiment-id	1pctco2
98	2023-01-03 18:15:36.117296	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:activity-id	cmip
99	2023-01-03 18:15:36.117298	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:source-id	ipsl-cm6a-lr
100	2023-01-03 18:15:36.117299	\N	cmip6	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	wcrp:cmip6:table-id	3hr
71	2023-01-03 13:58:59.551256	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	esdoc:errata:project	cmip6
72	2023-01-03 13:58:59.551261	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	esdoc:errata:status	new
73	2023-01-03 13:58:59.551264	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	esdoc:errata:moderation-status	accepted
74	2023-01-03 13:58:59.551266	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	esdoc:errata:severity	low
75	2023-01-03 13:58:59.551267	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:institution-id	ipsl
76	2023-01-03 13:58:59.551269	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:grid-label	gr
77	2023-01-03 13:58:59.551271	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:experiment-id	1pctco2
78	2023-01-03 13:58:59.551273	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:activity-id	cmip
79	2023-01-03 13:58:59.551275	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:source-id	ipsl-cm6a-lr
80	2023-01-03 13:58:59.551277	\N	cmip6	2428b051-e492-6a6c-b079-54576522cfd0	wcrp:cmip6:table-id	3hr
\.


--
-- TOC entry 3532 (class 0 OID 47128)
-- Dependencies: 215
-- Data for Name: tbl_issue_resource; Type: TABLE DATA; Schema: errata; Owner: test_db_errata_2
--

COPY errata.tbl_issue_resource (id, row_create_date, row_update_date, issue_uid, resource_type, resource_location) FROM stdin;
1	2023-01-03 11:48:10.854379	\N	986b1346-542b-efb7-a9a5-d4d769b61456	dataset	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605
8	2023-01-03 13:58:59.552259	\N	2428b051-e492-6a6c-b079-54576522cfd0	dataset	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605
10	2023-01-03 18:15:36.118381	\N	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	dataset	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605
\.


--
-- TOC entry 3530 (class 0 OID 47114)
-- Dependencies: 213
-- Data for Name: tbl_pid_service_task; Type: TABLE DATA; Schema: errata; Owner: test_db_errata_2
--

COPY errata.tbl_pid_service_task (id, row_create_date, row_update_date, action, status, issue_uid, dataset_id, error, try_count, "timestamp") FROM stdin;
1	2023-01-03 11:48:10.85806	\N	insert	queued	986b1346-542b-efb7-a9a5-d4d769b61456	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605	\N	0	2023-01-03 11:48:10.858086
2	2023-01-03 12:06:09.603834	\N	insert	queued	2428b051-e492-6a6c-b079-54576522cfd0	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605	\N	0	2023-01-03 12:06:09.603845
3	2023-01-03 18:14:27.936134	\N	insert	queued	dbdb62a9-3aef-bdbd-bb2e-5e244d5d6efc	CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.3hr.clt.gr#20180605	\N	0	2023-01-03 18:14:27.936151
\.


--
-- TOC entry 3545 (class 0 OID 0)
-- Dependencies: 216
-- Name: tbl_issue_facet_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: test_db_errata_2
--

SELECT pg_catalog.setval('errata.tbl_issue_facet_id_seq', 100, true);


--
-- TOC entry 3546 (class 0 OID 0)
-- Dependencies: 210
-- Name: tbl_issue_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: test_db_errata_2
--

SELECT pg_catalog.setval('errata.tbl_issue_id_seq', 3, true);


--
-- TOC entry 3547 (class 0 OID 0)
-- Dependencies: 214
-- Name: tbl_issue_resource_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: test_db_errata_2
--

SELECT pg_catalog.setval('errata.tbl_issue_resource_id_seq', 10, true);


--
-- TOC entry 3548 (class 0 OID 0)
-- Dependencies: 212
-- Name: tbl_pid_service_task_id_seq; Type: SEQUENCE SET; Schema: errata; Owner: test_db_errata_2
--

SELECT pg_catalog.setval('errata.tbl_pid_service_task_id_seq', 3, true);


--
-- TOC entry 3382 (class 2606 OID 47153)
-- Name: tbl_issue_facet tbl_issue_facet_issue_uid_facet_value_facet_type_key; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_facet
    ADD CONSTRAINT tbl_issue_facet_issue_uid_facet_value_facet_type_key UNIQUE (issue_uid, facet_value, facet_type);


--
-- TOC entry 3384 (class 2606 OID 47151)
-- Name: tbl_issue_facet tbl_issue_facet_pkey; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_facet
    ADD CONSTRAINT tbl_issue_facet_pkey PRIMARY KEY (id);


--
-- TOC entry 3371 (class 2606 OID 47109)
-- Name: tbl_issue tbl_issue_pkey; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue
    ADD CONSTRAINT tbl_issue_pkey PRIMARY KEY (id);


--
-- TOC entry 3377 (class 2606 OID 47137)
-- Name: tbl_issue_resource tbl_issue_resource_issue_uid_resource_type_resource_locatio_key; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_resource
    ADD CONSTRAINT tbl_issue_resource_issue_uid_resource_type_resource_locatio_key UNIQUE (issue_uid, resource_type, resource_location);


--
-- TOC entry 3379 (class 2606 OID 47135)
-- Name: tbl_issue_resource tbl_issue_resource_pkey; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_resource
    ADD CONSTRAINT tbl_issue_resource_pkey PRIMARY KEY (id);


--
-- TOC entry 3373 (class 2606 OID 47111)
-- Name: tbl_issue tbl_issue_uid_key; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue
    ADD CONSTRAINT tbl_issue_uid_key UNIQUE (uid);


--
-- TOC entry 3375 (class 2606 OID 47121)
-- Name: tbl_pid_service_task tbl_pid_service_task_pkey; Type: CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_pid_service_task
    ADD CONSTRAINT tbl_pid_service_task_pkey PRIMARY KEY (id);


--
-- TOC entry 3369 (class 1259 OID 47112)
-- Name: idx_issue_description; Type: INDEX; Schema: errata; Owner: test_db_errata_2
--

CREATE INDEX idx_issue_description ON errata.tbl_issue USING btree (lower(description));


--
-- TOC entry 3380 (class 1259 OID 47159)
-- Name: ix_errata_tbl_issue_facet_facet_value; Type: INDEX; Schema: errata; Owner: test_db_errata_2
--

CREATE INDEX ix_errata_tbl_issue_facet_facet_value ON errata.tbl_issue_facet USING btree (facet_value);


--
-- TOC entry 3387 (class 2606 OID 47154)
-- Name: tbl_issue_facet tbl_issue_facet_issue_uid_fkey; Type: FK CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_facet
    ADD CONSTRAINT tbl_issue_facet_issue_uid_fkey FOREIGN KEY (issue_uid) REFERENCES errata.tbl_issue(uid);


--
-- TOC entry 3386 (class 2606 OID 47138)
-- Name: tbl_issue_resource tbl_issue_resource_issue_uid_fkey; Type: FK CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_issue_resource
    ADD CONSTRAINT tbl_issue_resource_issue_uid_fkey FOREIGN KEY (issue_uid) REFERENCES errata.tbl_issue(uid);


--
-- TOC entry 3385 (class 2606 OID 47122)
-- Name: tbl_pid_service_task tbl_pid_service_task_issue_uid_fkey; Type: FK CONSTRAINT; Schema: errata; Owner: test_db_errata_2
--

ALTER TABLE ONLY errata.tbl_pid_service_task
    ADD CONSTRAINT tbl_pid_service_task_issue_uid_fkey FOREIGN KEY (issue_uid) REFERENCES errata.tbl_issue(uid);


--
-- TOC entry 3540 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA errata; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA errata TO test_db_errata_2;
GRANT USAGE ON SCHEMA errata TO test_db_errata_2;


-- Completed on 2023-01-03 20:12:36 CET

--
-- PostgreSQL database dump complete
--

