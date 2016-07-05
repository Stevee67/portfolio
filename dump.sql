--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET search_path = public, pg_catalog;

--
-- Name: cr_tm(); Type: FUNCTION; Schema: public; Owner: webdev
--

CREATE FUNCTION cr_tm() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	NEW.cr_tm = now();
	return NEW;
END;$$;


ALTER FUNCTION public.cr_tm() OWNER TO webdev;

--
-- Name: cr_uuid(); Type: FUNCTION; Schema: public; Owner: webdev
--

CREATE FUNCTION cr_uuid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
   NEW.id = uuid_generate_v4();
   RETURN NEW;
END;$$;


ALTER FUNCTION public.cr_uuid() OWNER TO webdev;

--
-- Name: uuid_generate()(); Type: FUNCTION; Schema: public; Owner: webdev
--

CREATE FUNCTION "uuid_generate()"() RETURNS character varying
    LANGUAGE plpgsql
    AS $$BEGIN
   RETURN uuid_generate_v4();
END;$$;


ALTER FUNCTION public."uuid_generate()"() OWNER TO webdev;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: educations; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE educations (
    id character varying(64) NOT NULL,
    title character varying(200),
    level character varying(200),
    ed_from timestamp without time zone,
    ed_to timestamp without time zone,
    description character varying(500),
    cr_tm timestamp without time zone
);


ALTER TABLE educations OWNER TO webdev;

--
-- Name: experience; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE experience (
    id character varying(64) NOT NULL,
    user_id character varying(64) NOT NULL,
    title character varying(255) NOT NULL,
    subtitle character varying(255),
    w_from timestamp without time zone,
    w_to timestamp without time zone,
    description character varying(500),
    cr_tm timestamp without time zone
);


ALTER TABLE experience OWNER TO webdev;

--
-- Name: images; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE images (
    id character varying(64) NOT NULL,
    folder_name character varying(150) NOT NULL,
    file_name character varying(150),
    mime character varying(50),
    size integer,
    cr_tm timestamp without time zone
);


ALTER TABLE images OWNER TO webdev;

--
-- Name: users; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE users (
    id character varying(64) NOT NULL,
    name character varying(100) NOT NULL,
    lastname character varying(100) NOT NULL,
    email character varying NOT NULL,
    age smallint NOT NULL,
    phone character varying(50),
    address character varying(500),
    status character varying(50) NOT NULL,
    skype character varying(100),
    about_me character varying(1000),
    linkedin character varying(100),
    facebook character varying(100),
    short_about character varying(200),
    password_hash character varying(128),
    cr_tm timestamp without time zone
);


ALTER TABLE users OWNER TO webdev;

--
-- Name: personal_info_age_seq; Type: SEQUENCE; Schema: public; Owner: webdev
--

CREATE SEQUENCE personal_info_age_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE personal_info_age_seq OWNER TO webdev;

--
-- Name: personal_info_age_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: webdev
--

ALTER SEQUENCE personal_info_age_seq OWNED BY users.age;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE projects (
    id character varying(64) NOT NULL,
    name character varying(200) NOT NULL,
    url character varying(100) NOT NULL,
    image_id character varying(64),
    cr_tm timestamp without time zone
);


ALTER TABLE projects OWNER TO webdev;

--
-- Name: skils; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE skils (
    id character varying(64) NOT NULL,
    name character varying(150) NOT NULL,
    user_id character varying(64) NOT NULL,
    kn_percent integer,
    cr_tm timestamp without time zone
);


ALTER TABLE skils OWNER TO webdev;

--
-- Name: static_data; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE static_data (
    type character varying(200),
    text text DEFAULT ''::text,
    cr_tm timestamp without time zone,
    id character varying(64) NOT NULL
);


ALTER TABLE static_data OWNER TO webdev;

--
-- Name: visitors; Type: TABLE; Schema: public; Owner: webdev; Tablespace: 
--

CREATE TABLE visitors (
    id character varying(64) NOT NULL,
    location character varying(100),
    last_visit timestamp without time zone,
    city character varying(200),
    country character varying(200),
    region character varying(200),
    hostname character varying(200),
    cr_tm timestamp without time zone,
    ip character varying(100),
    count_visits integer
);


ALTER TABLE visitors OWNER TO webdev;

--
-- Name: age; Type: DEFAULT; Schema: public; Owner: webdev
--

ALTER TABLE ONLY users ALTER COLUMN age SET DEFAULT nextval('personal_info_age_seq'::regclass);


--
-- Data for Name: educations; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY educations (id, title, level, ed_from, ed_to, description, cr_tm) FROM stdin;
c5ed1d45-2b52-46ba-830d-5430b3b3eca7	Lviv National Agrarian University	Master	2012-09-01 00:00:00	2013-12-20 00:00:00	daaadsasddasasd\r\nsaddasds\r\nsadasdasd\r\nsadadsasd\r\nsadasdaa	\N
bb6812f2-6cb3-46da-a0c1-d6b3c1a90fd2	Volytsya	Middle School of General Education	1997-09-01 09:00:00	2008-05-31 09:00:00	daaadsasddasasd\r\nsaddasds\r\nsadasdasd\r\nsadadsasd\r\nsadasdaa	\N
feb53606-8430-4498-9dfc-bab330916d6f	Lviv National Agrarian University	Bachelor	2008-09-01 09:00:00	2012-07-01 09:00:00	111	\N
683ee25e-a2eb-4f7b-b699-717d45321bba	Azbuka svitu	pre intermediate	2015-04-18 21:00:00	2015-06-04 21:00:00	\N	2016-07-05 12:05:25.587365
\.


--
-- Data for Name: experience; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY experience (id, user_id, title, subtitle, w_from, w_to, description, cr_tm) FROM stdin;
464c0136-e79d-4069-8b36-1fc18b876053	984e586d-bd84-4ecc-b261-46b1c9c00c8c	Python Developer	NTaxa	2015-03-15 10:00:00	2016-05-19 09:00:00	NTaxa	\N
0b4e28fa-6142-4e4a-9fa2-0986abe58e7d	984e586d-bd84-4ecc-b261-46b1c9c00c8c	Engineer	Viktar	2014-03-09 10:00:00	2014-12-05 10:00:00	Віктар	\N
68dc1d1d-113b-4f15-ad24-4af087baf4ef	984e586d-bd84-4ecc-b261-46b1c9c00c8c	Python Developer	UkrInSofT	2016-05-23 09:00:00	\N	UkrInSofT is the Ukrainian nearshore web and mobile app development company. UkrInSofT stands for “Ukrainian Innovation Software Technologies”. This phrase perfectly mirrors our approach to software development process: here at UkrInSofT we not just deliver standard solutions, but strive to provide our clients with a software that would address their issue and strengthen their competitive position on the market.	\N
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY images (id, folder_name, file_name, mime, size, cr_tm) FROM stdin;
08688184-a8c4-420b-bd09-d9131edea063	projects	file(3).png	\N	85167	2016-06-22 09:50:52.298377
76f986f5-095e-4f58-98ac-eb5a834a8f3c	projects	file(1).png	image/png	1451577	\N
4af519d5-35ec-4b36-82cd-d9e22d1f4f49	projects	file(2).png	image/png	226838	\N
0000000-0000-0000-0000-000000000001	projects	default.png	image/png	85167	\N
\.


--
-- Name: personal_info_age_seq; Type: SEQUENCE SET; Schema: public; Owner: webdev
--

SELECT pg_catalog.setval('personal_info_age_seq', 1, false);


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY projects (id, name, url, image_id, cr_tm) FROM stdin;
27bb84f3-c08c-447c-808c-2c252a0617fc	Profireader	http://profireader.com/	4af519d5-35ec-4b36-82cd-d9e22d1f4f49	\N
9b0cdfe3-d401-49f8-bd65-7feadfbc6a05	Parser for Insurance Company	http://verifacto.com	76f986f5-095e-4f58-98ac-eb5a834a8f3c	\N
8a00584a-cd19-410e-8e34-4b090d001987	FeatureApp	http://test-ukrinsoft.rhcloud.com/	08688184-a8c4-420b-bd09-d9131edea063	\N
\.


--
-- Data for Name: skils; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY skils (id, name, user_id, kn_percent, cr_tm) FROM stdin;
e9d15f1a-78de-48c7-a375-de7010107d87	SQLAlchemy	984e586d-bd84-4ecc-b261-46b1c9c00c8c	50	\N
fd5e661a-c17e-47da-88b0-1249e1f67850	Flask	984e586d-bd84-4ecc-b261-46b1c9c00c8c	62	\N
6128d7d6-dc19-4716-8da3-d246cd0e8c4f	Python	984e586d-bd84-4ecc-b261-46b1c9c00c8c	75	\N
7d0b55d8-52fd-4d13-a18d-2dd952419ad6	Jinja	984e586d-bd84-4ecc-b261-46b1c9c00c8c	70	\N
3e136b31-9f68-4861-894c-0e22e49ade99	PostgreSQL	984e586d-bd84-4ecc-b261-46b1c9c00c8c	55	\N
c93ebf69-b9e7-42f5-ab1d-b91efe7a2839	AngularJS	984e586d-bd84-4ecc-b261-46b1c9c00c8c	45	\N
c326c527-a370-410a-b52e-bdd5053bd7b1	GIT	984e586d-bd84-4ecc-b261-46b1c9c00c8c	70	\N
a79fa10e-08d0-4696-a3e3-58b8f8a682ac	SQL	984e586d-bd84-4ecc-b261-46b1c9c00c8c	60	\N
f2a136e4-f5b8-4fb6-b02c-617540b53338	JS	984e586d-bd84-4ecc-b261-46b1c9c00c8c	55	\N
b8b25ee2-40d4-4f24-95b6-d6832c738319	HTML	984e586d-bd84-4ecc-b261-46b1c9c00c8c	50	\N
bb08069e-2025-4ef6-a0ca-66365d2f6d9c	jira	984e586d-bd84-4ecc-b261-46b1c9c00c8c	70	2016-07-05 11:57:51.980204
568eb211-7389-4253-8bc2-bcea8b54b7f1	tornado	984e586d-bd84-4ecc-b261-46b1c9c00c8c	58	2016-06-21 17:26:08.063024
0c5026ee-b02d-4102-b549-d979c57549b9	jQuery	984e586d-bd84-4ecc-b261-46b1c9c00c8c	40	\N
89a6cd37-d391-43e8-9d88-d1f47528cb2a	CSS	984e586d-bd84-4ecc-b261-46b1c9c00c8c	60	\N
\.


--
-- Data for Name: static_data; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY static_data (type, text, cr_tm, id) FROM stdin;
EXPERIENCE		2016-06-22 10:57:13.749709	d99d1b5d-196a-46d8-85e1-1cc47bf33e0a
PORTFOLIO		2016-06-22 10:57:20.244415	ffcb0569-9528-4fdf-a8e9-906cb929381e
FOOTER		2016-06-22 10:57:23.394632	9493761c-b630-429a-a50e-5f5c8d340722
TITLE		2016-06-22 11:12:43.996111	7f3a1c5a-2e68-470b-9b02-5659a8629421
HEADER		2016-06-22 10:57:26.200282	e6f24043-9bdc-4c6a-9134-8f08e1431455
EDUCATION		2016-06-22 10:57:16.786128	3cecf740-3570-4d52-a7da-c9c0aa297185
CONTACT	Please contact me, If you have some questions!	2016-06-22 10:57:03.590151	dd3b15cf-a6dd-4182-85bd-cbf7b3a7e894
SKILL		2016-06-29 17:49:28.578701	9061a77d-e0a0-463f-b4cf-5feee496bea8
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY users (id, name, lastname, email, age, phone, address, status, skype, about_me, linkedin, facebook, short_about, password_hash, cr_tm) FROM stdin;
984e586d-bd84-4ecc-b261-46b1c9c00c8c	Stepan	Shysh	stopa6767@gmail.com	25	+380934340484	Lviv, Hotckevycha str. 58	admin	stopa67	Hello my name is Steve)) I live in great city - Lviv! I"m programmer and i like my job :)Yeep	www.linkedin.com	www.facebook.com/profile.php?id=100009694988182	None	pbkdf2:sha256:1000$uYkuf2SFRp9FwIzM65jW7wLybo2AgTZ2$dc7c7a6f6ba4ccca4b56f1c3ab5d28739c4ba120e1ac3825675989bfa4c58c05	\N
\.


--
-- Data for Name: visitors; Type: TABLE DATA; Schema: public; Owner: webdev
--

COPY visitors (id, location, last_visit, city, country, region, hostname, cr_tm, ip, count_visits) FROM stdin;
6745036d-efb6-4a6f-8f39-304e44b7c3bd	longitude: 24.0305 / latitude: 49.8407	2016-07-05 17:28:51.115474	Lviv	Ukraine	L_vivs_ka Oblast_	\N	2016-07-05 17:27:06.772075	95.215.156.204	3
\.


--
-- Name: educations_pkey; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY educations
    ADD CONSTRAINT educations_pkey PRIMARY KEY (id);


--
-- Name: ex_id; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY experience
    ADD CONSTRAINT ex_id PRIMARY KEY (id);


--
-- Name: image_pk; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY images
    ADD CONSTRAINT image_pk PRIMARY KEY (id);


--
-- Name: personal_id; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT personal_id PRIMARY KEY (id);


--
-- Name: pr_id; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT pr_id PRIMARY KEY (id);


--
-- Name: skil_id; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY skils
    ADD CONSTRAINT skil_id PRIMARY KEY (id);


--
-- Name: static_data_pkey; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY static_data
    ADD CONSTRAINT static_data_pkey PRIMARY KEY (id);


--
-- Name: uniq_status; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT uniq_status UNIQUE (status);


--
-- Name: uniqemail; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT uniqemail UNIQUE (email);


--
-- Name: unqi_name; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY skils
    ADD CONSTRAINT unqi_name UNIQUE (name);


--
-- Name: vis_ip_uniq; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY visitors
    ADD CONSTRAINT vis_ip_uniq UNIQUE (ip);


--
-- Name: vis_pk; Type: CONSTRAINT; Schema: public; Owner: webdev; Tablespace: 
--

ALTER TABLE ONLY visitors
    ADD CONSTRAINT vis_pk PRIMARY KEY (id);


--
-- Name: fki_image_fk; Type: INDEX; Schema: public; Owner: webdev; Tablespace: 
--

CREATE INDEX fki_image_fk ON projects USING btree (image_id);


--
-- Name: cr_id; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER cr_id BEFORE INSERT ON static_data FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: cr_id; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER cr_id BEFORE INSERT ON visitors FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: ed_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER ed_cr_tm BEFORE INSERT ON educations FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: ed_uuid; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER ed_uuid BEFORE INSERT ON educations FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: ex_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER ex_cr_tm BEFORE INSERT ON experience FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: ex_id; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER ex_id BEFORE INSERT ON experience FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: im_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER im_cr_tm BEFORE INSERT ON images FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: image_id; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER image_id BEFORE INSERT ON images FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: pr_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER pr_cr_tm BEFORE INSERT ON projects FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: pr_uuid; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER pr_uuid BEFORE INSERT ON projects FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: sd_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER sd_cr_tm BEFORE INSERT ON static_data FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: sk_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER sk_cr_tm BEFORE INSERT ON skils FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: skill_id; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER skill_id BEFORE INSERT ON skils FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: us_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER us_cr_tm BEFORE INSERT ON users FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: uuid; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER uuid BEFORE INSERT ON users FOR EACH ROW EXECUTE PROCEDURE cr_uuid();


--
-- Name: vt_cr_tm; Type: TRIGGER; Schema: public; Owner: webdev
--

CREATE TRIGGER vt_cr_tm BEFORE INSERT ON visitors FOR EACH ROW EXECUTE PROCEDURE cr_tm();


--
-- Name: image_fk; Type: FK CONSTRAINT; Schema: public; Owner: webdev
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT image_fk FOREIGN KEY (image_id) REFERENCES images(id) ON UPDATE SET NULL ON DELETE SET NULL;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

