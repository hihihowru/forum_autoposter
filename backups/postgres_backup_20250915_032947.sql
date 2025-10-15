--
-- PostgreSQL database dump
--

\restrict GvX5XoBgEzwIx12z1l2ZWKmBMdRLHN1fjoiyFHeEIaFeof4Sj87rYov4LLGDKSz

-- Dumped from database version 14.19 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

-- Started on 2025-09-15 03:29:47 CST

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

DROP DATABASE posting_management;
--
-- TOC entry 3810 (class 1262 OID 16384)
-- Name: posting_management; Type: DATABASE; Schema: -; Owner: williamchen
--

CREATE DATABASE posting_management WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C';


ALTER DATABASE posting_management OWNER TO williamchen;

\unrestrict GvX5XoBgEzwIx12z1l2ZWKmBMdRLHN1fjoiyFHeEIaFeof4Sj87rYov4LLGDKSz
\connect posting_management
\restrict GvX5XoBgEzwIx12z1l2ZWKmBMdRLHN1fjoiyFHeEIaFeof4Sj87rYov4LLGDKSz

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 210 (class 1259 OID 16387)
-- Name: kol_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kol_profiles (
    id integer NOT NULL,
    serial integer NOT NULL,
    nickname character varying(100) NOT NULL,
    name character varying(100),
    persona character varying(50),
    style_preference text,
    expertise_areas text[],
    activity_level character varying(20),
    question_ratio double precision,
    content_length character varying(20),
    interaction_starters text[],
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.kol_profiles OWNER TO postgres;

--
-- TOC entry 209 (class 1259 OID 16386)
-- Name: kol_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kol_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kol_profiles_id_seq OWNER TO postgres;

--
-- TOC entry 3811 (class 0 OID 0)
-- Dependencies: 209
-- Name: kol_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kol_profiles_id_seq OWNED BY public.kol_profiles.id;


--
-- TOC entry 212 (class 1259 OID 16494)
-- Name: posting_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posting_sessions (
    id integer NOT NULL,
    session_name character varying(100) NOT NULL,
    trigger_type character varying(50) NOT NULL,
    trigger_data jsonb,
    template_id integer,
    config jsonb,
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.posting_sessions OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 16493)
-- Name: posting_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posting_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posting_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 3812 (class 0 OID 0)
-- Dependencies: 211
-- Name: posting_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posting_sessions_id_seq OWNED BY public.posting_sessions.id;


--
-- TOC entry 214 (class 1259 OID 16503)
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    session_id integer,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    status character varying(20),
    kol_serial integer NOT NULL,
    kol_nickname character varying(50) NOT NULL,
    kol_persona character varying(100),
    stock_codes jsonb,
    stock_names jsonb,
    stock_data jsonb,
    generation_config jsonb,
    prompt_template text,
    technical_indicators jsonb,
    quality_score double precision,
    ai_detection_score double precision,
    risk_level character varying(20),
    views integer,
    likes integer,
    comments integer,
    shares integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 16502)
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO postgres;

--
-- TOC entry 3813 (class 0 OID 0)
-- Dependencies: 213
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- TOC entry 3645 (class 2604 OID 16390)
-- Name: kol_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kol_profiles ALTER COLUMN id SET DEFAULT nextval('public.kol_profiles_id_seq'::regclass);


--
-- TOC entry 3649 (class 2604 OID 16497)
-- Name: posting_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posting_sessions ALTER COLUMN id SET DEFAULT nextval('public.posting_sessions_id_seq'::regclass);


--
-- TOC entry 3650 (class 2604 OID 16506)
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- TOC entry 3800 (class 0 OID 16387)
-- Dependencies: 210
-- Data for Name: kol_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kol_profiles (id, serial, nickname, name, persona, style_preference, expertise_areas, activity_level, question_ratio, content_length, interaction_starters, is_active, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3802 (class 0 OID 16494)
-- Dependencies: 212
-- Data for Name: posting_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posting_sessions (id, session_name, trigger_type, trigger_data, template_id, config, status, created_at, updated_at) FROM stdin;
1	New Session	custom_stocks	{"stock_codes": ["2330"], "stock_names": ["台積電"]}	\N	{"kol": {"selected_kols": [200]}, "kolPrompts": []}	active	2025-09-09 16:43:52.935985	2025-09-09 16:43:52.935987
\.


--
-- TOC entry 3804 (class 0 OID 16503)
-- Dependencies: 214
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posts (id, session_id, title, content, status, kol_serial, kol_nickname, kol_persona, stock_codes, stock_names, stock_data, generation_config, prompt_template, technical_indicators, quality_score, ai_detection_score, risk_level, views, likes, comments, shares, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3814 (class 0 OID 0)
-- Dependencies: 209
-- Name: kol_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kol_profiles_id_seq', 12, true);


--
-- TOC entry 3815 (class 0 OID 0)
-- Dependencies: 211
-- Name: posting_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posting_sessions_id_seq', 1, true);


--
-- TOC entry 3816 (class 0 OID 0)
-- Dependencies: 213
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- TOC entry 3652 (class 2606 OID 16397)
-- Name: kol_profiles kol_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kol_profiles
    ADD CONSTRAINT kol_profiles_pkey PRIMARY KEY (id);


--
-- TOC entry 3654 (class 2606 OID 16399)
-- Name: kol_profiles kol_profiles_serial_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kol_profiles
    ADD CONSTRAINT kol_profiles_serial_key UNIQUE (serial);


--
-- TOC entry 3656 (class 2606 OID 16501)
-- Name: posting_sessions posting_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posting_sessions
    ADD CONSTRAINT posting_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 3658 (class 2606 OID 16510)
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- TOC entry 3659 (class 2606 OID 16511)
-- Name: posts posts_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.posting_sessions(id);


-- Completed on 2025-09-15 03:29:48 CST

--
-- PostgreSQL database dump complete
--

\unrestrict GvX5XoBgEzwIx12z1l2ZWKmBMdRLHN1fjoiyFHeEIaFeof4Sj87rYov4LLGDKSz

