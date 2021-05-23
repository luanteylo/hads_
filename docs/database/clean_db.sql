--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Drop databases (except postgres and template1)
--

DROP DATABASE controldb;
DROP DATABASE mydb;
DROP DATABASE portalv2;
DROP DATABASE test;




--
-- Drop roles
--

DROP ROLE gera;
DROP ROLE gera1;
DROP ROLE postgres;
DROP ROLE role_name;


--
-- Roles
--

CREATE ROLE gera;
ALTER ROLE gera WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS;
CREATE ROLE gera1;
ALTER ROLE gera1 WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'md58c8242a0d0df025045679b41e7c067ce';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'md5a724072422c87962d234dcddd8aed15d';
CREATE ROLE role_name;
ALTER ROLE role_name WITH SUPERUSER INHERIT NOCREATEROLE NOCREATEDB NOLOGIN NOREPLICATION NOBYPASSRLS;






--
-- Databases
--

--
-- Database "template1" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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

UPDATE pg_catalog.pg_database SET datistemplate = false WHERE datname = 'template1';
DROP DATABASE template1;
--
-- Name: template1; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE template1 WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE template1 OWNER TO postgres;

\connect template1

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
-- Name: DATABASE template1; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE template1 IS 'default template for new databases';


--
-- Name: template1; Type: DATABASE PROPERTIES; Schema: -; Owner: postgres
--

ALTER DATABASE template1 IS_TEMPLATE = true;


\connect template1

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
-- Name: DATABASE template1; Type: ACL; Schema: -; Owner: postgres
--

REVOKE CONNECT,TEMPORARY ON DATABASE template1 FROM PUBLIC;
GRANT CONNECT ON DATABASE template1 TO PUBLIC;


--
-- PostgreSQL database dump complete
--

--
-- Database "controldb" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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
-- Name: controldb; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE controldb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE controldb OWNER TO postgres;

\connect controldb

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
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: execution; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.execution (
    execution_id integer NOT NULL,
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    instance_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    avg_memory double precision,
    status character varying
);


ALTER TABLE public.execution OWNER TO postgres;

--
-- Name: execution_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.execution_status (
    execution_id integer NOT NULL,
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    instance_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    avg_memory double precision,
    status character varying
);


ALTER TABLE public.execution_status OWNER TO postgres;

--
-- Name: instance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance (
    id character varying NOT NULL,
    type character varying,
    region character varying,
    zone character varying,
    market character varying,
    price double precision
);


ALTER TABLE public.instance OWNER TO postgres;

--
-- Name: instance_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance_status (
    instance_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    status character varying
);


ALTER TABLE public.instance_status OWNER TO postgres;

--
-- Name: instance_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance_type (
    type character varying NOT NULL,
    vcpu integer,
    memory double precision,
    provider character varying
);


ALTER TABLE public.instance_type OWNER TO postgres;

--
-- Name: job; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job (
    id integer NOT NULL,
    name character varying,
    description character varying
);


ALTER TABLE public.job OWNER TO postgres;

--
-- Name: job_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.job_id_seq OWNER TO postgres;

--
-- Name: job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_id_seq OWNED BY public.job.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task (
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    command character varying,
    memory double precision,
    io double precision
);


ALTER TABLE public.task OWNER TO postgres;

--
-- Name: test; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test (
    execution_id integer NOT NULL,
    job_id integer NOT NULL,
    start timestamp without time zone,
    "end" timestamp without time zone,
    deadline timestamp without time zone,
    hibernations integer,
    faults integer,
    work_stealing integer,
    hibernation_recovery integer,
    hibernation_timeout integer,
    idle_migration integer,
    working_migration integer,
    on_demand integer,
    spot integer,
    elapsed interval,
    cost double precision,
    ondemand_cost double precision,
    completed_tasks integer
);


ALTER TABLE public.test OWNER TO postgres;

--
-- Name: job id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job ALTER COLUMN id SET DEFAULT nextval('public.job_id_seq'::regclass);


--
-- Data for Name: execution; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.execution (execution_id, job_id, task_id, instance_id, "timestamp", avg_memory, status) FROM stdin;
\.


--
-- Data for Name: execution_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.execution_status (execution_id, job_id, task_id, instance_id, "timestamp", avg_memory, status) FROM stdin;
0	200	2	i-0bfdd8e5b2a5a8143	2019-03-30 15:01:38.20816	0	waiting
0	200	0	i-0363e6ac3b1b46ad5	2019-03-30 15:01:38.51292	0	waiting
0	200	1	i-040402b85d7bc54c4	2019-03-30 15:01:38.553461	0	waiting
0	200	3	i-048a046b3d575b7c8	2019-03-30 15:01:38.56174	0	waiting
0	200	3	i-048a046b3d575b7c8	2019-03-30 15:02:14.279995	0	executing
0	200	0	i-0363e6ac3b1b46ad5	2019-03-30 15:02:14.328468	0	executing
0	200	1	i-040402b85d7bc54c4	2019-03-30 15:02:14.399822	0	executing
0	200	2	i-0bfdd8e5b2a5a8143	2019-03-30 15:02:42.096192	0	executing
0	200	1	i-040402b85d7bc54c4	2019-03-30 15:03:12.929855	9.350523749999999	finished
0	200	0	i-0363e6ac3b1b46ad5	2019-03-30 15:03:13.123799	9.18373275	finished
0	200	3	i-048a046b3d575b7c8	2019-03-30 15:03:13.482473	9.32167625	finished
0	200	2	i-0bfdd8e5b2a5a8143	2019-03-30 15:03:51.027635	7.958879555555555	finished
\.


--
-- Data for Name: instance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance (id, type, region, zone, market, price) FROM stdin;
\.


--
-- Data for Name: instance_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance_status (instance_id, "timestamp", status) FROM stdin;
\.


--
-- Data for Name: instance_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance_type (type, vcpu, memory, provider) FROM stdin;
\.


--
-- Data for Name: job; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job (id, name, description) FROM stdin;
\.


--
-- Data for Name: task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task (job_id, task_id, command, memory, io) FROM stdin;
\.


--
-- Data for Name: test; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.test (execution_id, job_id, start, "end", deadline, hibernations, faults, work_stealing, hibernation_recovery, hibernation_timeout, idle_migration, working_migration, on_demand, spot, elapsed, cost, ondemand_cost, completed_tasks) FROM stdin;
\.


--
-- Name: job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_id_seq', 1, false);


--
-- Name: execution execution_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_pkey PRIMARY KEY (execution_id, job_id, task_id, instance_id, "timestamp");


--
-- Name: execution_status execution_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution_status
    ADD CONSTRAINT execution_status_pkey PRIMARY KEY (execution_id, job_id, task_id, instance_id, "timestamp");


--
-- Name: instance instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance
    ADD CONSTRAINT instance_pkey PRIMARY KEY (id);


--
-- Name: instance_status instance_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_status
    ADD CONSTRAINT instance_status_pkey PRIMARY KEY (instance_id, "timestamp");


--
-- Name: instance_type instance_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_type
    ADD CONSTRAINT instance_type_pkey PRIMARY KEY (type);


--
-- Name: job job_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job
    ADD CONSTRAINT job_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (job_id, task_id);


--
-- Name: test test_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test
    ADD CONSTRAINT test_pkey PRIMARY KEY (execution_id, job_id);


--
-- Name: execution execution_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.instance(id);


--
-- Name: execution execution_job_id_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_job_id_task_id_fkey FOREIGN KEY (job_id, task_id) REFERENCES public.task(job_id, task_id);


--
-- Name: instance_status instance_status_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_status
    ADD CONSTRAINT instance_status_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.instance(id);


--
-- Name: instance instance_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance
    ADD CONSTRAINT instance_type_fkey FOREIGN KEY (type) REFERENCES public.instance_type(type);


--
-- Name: task task_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.job(id);


--
-- PostgreSQL database dump complete
--

--
-- Database "mydb" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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
-- Name: mydb; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE mydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE mydb OWNER TO postgres;

\connect mydb

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
-- Name: test_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_table (
    user_id integer NOT NULL,
    type character varying(100) NOT NULL
);


ALTER TABLE public.test_table OWNER TO postgres;

--
-- Name: test_table_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_table_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.test_table_user_id_seq OWNER TO postgres;

--
-- Name: test_table_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_table_user_id_seq OWNED BY public.test_table.user_id;


--
-- Name: test_table user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_table ALTER COLUMN user_id SET DEFAULT nextval('public.test_table_user_id_seq'::regclass);


--
-- Data for Name: test_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.test_table (user_id, type) FROM stdin;
1	test
\.


--
-- Name: test_table_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.test_table_user_id_seq', 1, true);


--
-- Name: test_table test_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_table
    ADD CONSTRAINT test_table_pkey PRIMARY KEY (user_id);


--
-- PostgreSQL database dump complete
--

--
-- Database "portalv2" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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
-- Name: portalv2; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE portalv2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE portalv2 OWNER TO postgres;

\connect portalv2

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
-- Name: auth_group; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO gera1;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO gera1;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO gera1;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO gera1;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO gera1;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO gera1;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO gera1;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO gera1;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO gera1;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO gera1;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO gera1;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO gera1;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: common_cidade; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_cidade (
    id integer NOT NULL,
    nome character varying(250) NOT NULL,
    estado_id integer NOT NULL
);


ALTER TABLE public.common_cidade OWNER TO gera1;

--
-- Name: common_cidade_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_cidade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_cidade_id_seq OWNER TO gera1;

--
-- Name: common_cidade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_cidade_id_seq OWNED BY public.common_cidade.id;


--
-- Name: common_distribuidora; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_distribuidora (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    is_active boolean NOT NULL,
    created_by_id integer NOT NULL,
    estado_id integer
);


ALTER TABLE public.common_distribuidora OWNER TO gera1;

--
-- Name: common_distribuidora_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_distribuidora_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_distribuidora_id_seq OWNER TO gera1;

--
-- Name: common_distribuidora_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_distribuidora_id_seq OWNED BY public.common_distribuidora.id;


--
-- Name: common_estado; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_estado (
    id integer NOT NULL,
    nome character varying(250) NOT NULL,
    uf character varying(2) NOT NULL,
    pais_id integer NOT NULL
);


ALTER TABLE public.common_estado OWNER TO gera1;

--
-- Name: common_estado_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_estado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_estado_id_seq OWNER TO gera1;

--
-- Name: common_estado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_estado_id_seq OWNED BY public.common_estado.id;


--
-- Name: common_modelonegocio; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_modelonegocio (
    id integer NOT NULL,
    nome character varying(25) NOT NULL
);


ALTER TABLE public.common_modelonegocio OWNER TO gera1;

--
-- Name: common_modelonegocio_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_modelonegocio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_modelonegocio_id_seq OWNER TO gera1;

--
-- Name: common_modelonegocio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_modelonegocio_id_seq OWNED BY public.common_modelonegocio.id;


--
-- Name: common_pais; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_pais (
    id integer NOT NULL,
    nome character varying(250) NOT NULL,
    sigla character varying(2) NOT NULL
);


ALTER TABLE public.common_pais OWNER TO gera1;

--
-- Name: common_pais_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_pais_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_pais_id_seq OWNER TO gera1;

--
-- Name: common_pais_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_pais_id_seq OWNED BY public.common_pais.id;


--
-- Name: common_tipocontrato; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.common_tipocontrato (
    id integer NOT NULL,
    nome character varying(30) NOT NULL
);


ALTER TABLE public.common_tipocontrato OWNER TO gera1;

--
-- Name: common_tipocontrato_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.common_tipocontrato_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.common_tipocontrato_id_seq OWNER TO gera1;

--
-- Name: common_tipocontrato_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.common_tipocontrato_id_seq OWNED BY public.common_tipocontrato.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO gera1;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO gera1;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO gera1;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO gera1;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO gera1;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO gera1;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO gera1;

--
-- Name: faturas_common_bandeira; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.faturas_common_bandeira (
    id integer NOT NULL,
    tipo character varying(10) NOT NULL
);


ALTER TABLE public.faturas_common_bandeira OWNER TO gera1;

--
-- Name: faturas_common_bandeira_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.faturas_common_bandeira_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faturas_common_bandeira_id_seq OWNER TO gera1;

--
-- Name: faturas_common_bandeira_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.faturas_common_bandeira_id_seq OWNED BY public.faturas_common_bandeira.id;


--
-- Name: faturas_common_tipoenergia; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.faturas_common_tipoenergia (
    id integer NOT NULL,
    tipo character varying(50) NOT NULL
);


ALTER TABLE public.faturas_common_tipoenergia OWNER TO gera1;

--
-- Name: faturas_common_tipoenergia_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.faturas_common_tipoenergia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faturas_common_tipoenergia_id_seq OWNER TO gera1;

--
-- Name: faturas_common_tipoenergia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.faturas_common_tipoenergia_id_seq OWNED BY public.faturas_common_tipoenergia.id;


--
-- Name: faturas_common_tipohorario; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.faturas_common_tipohorario (
    id integer NOT NULL,
    tipo character varying(20) NOT NULL
);


ALTER TABLE public.faturas_common_tipohorario OWNER TO gera1;

--
-- Name: faturas_common_tipohorario_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.faturas_common_tipohorario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faturas_common_tipohorario_id_seq OWNER TO gera1;

--
-- Name: faturas_common_tipohorario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.faturas_common_tipohorario_id_seq OWNED BY public.faturas_common_tipohorario.id;


--
-- Name: faturas_common_tipoquantidade; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.faturas_common_tipoquantidade (
    id integer NOT NULL,
    tipo character varying(10) NOT NULL
);


ALTER TABLE public.faturas_common_tipoquantidade OWNER TO gera1;

--
-- Name: faturas_common_tipoquantidade_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.faturas_common_tipoquantidade_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faturas_common_tipoquantidade_id_seq OWNER TO gera1;

--
-- Name: faturas_common_tipoquantidade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.faturas_common_tipoquantidade_id_seq OWNED BY public.faturas_common_tipoquantidade.id;


--
-- Name: faturas_common_tipotarifa; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.faturas_common_tipotarifa (
    id integer NOT NULL,
    tipo character varying(10) NOT NULL
);


ALTER TABLE public.faturas_common_tipotarifa OWNER TO gera1;

--
-- Name: faturas_common_tipotarifa_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.faturas_common_tipotarifa_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faturas_common_tipotarifa_id_seq OWNER TO gera1;

--
-- Name: faturas_common_tipotarifa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.faturas_common_tipotarifa_id_seq OWNED BY public.faturas_common_tipotarifa.id;


--
-- Name: tenant_client; Type: TABLE; Schema: public; Owner: gera1
--

CREATE TABLE public.tenant_client (
    id integer NOT NULL,
    domain_url character varying(128) NOT NULL,
    schema_name character varying(63) NOT NULL,
    name character varying(500) NOT NULL,
    is_active boolean NOT NULL,
    created_on date NOT NULL
);


ALTER TABLE public.tenant_client OWNER TO gera1;

--
-- Name: tenant_client_id_seq; Type: SEQUENCE; Schema: public; Owner: gera1
--

CREATE SEQUENCE public.tenant_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_client_id_seq OWNER TO gera1;

--
-- Name: tenant_client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gera1
--

ALTER SEQUENCE public.tenant_client_id_seq OWNED BY public.tenant_client.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: common_cidade id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_cidade ALTER COLUMN id SET DEFAULT nextval('public.common_cidade_id_seq'::regclass);


--
-- Name: common_distribuidora id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_distribuidora ALTER COLUMN id SET DEFAULT nextval('public.common_distribuidora_id_seq'::regclass);


--
-- Name: common_estado id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_estado ALTER COLUMN id SET DEFAULT nextval('public.common_estado_id_seq'::regclass);


--
-- Name: common_modelonegocio id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_modelonegocio ALTER COLUMN id SET DEFAULT nextval('public.common_modelonegocio_id_seq'::regclass);


--
-- Name: common_pais id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_pais ALTER COLUMN id SET DEFAULT nextval('public.common_pais_id_seq'::regclass);


--
-- Name: common_tipocontrato id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_tipocontrato ALTER COLUMN id SET DEFAULT nextval('public.common_tipocontrato_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: faturas_common_bandeira id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_bandeira ALTER COLUMN id SET DEFAULT nextval('public.faturas_common_bandeira_id_seq'::regclass);


--
-- Name: faturas_common_tipoenergia id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipoenergia ALTER COLUMN id SET DEFAULT nextval('public.faturas_common_tipoenergia_id_seq'::regclass);


--
-- Name: faturas_common_tipohorario id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipohorario ALTER COLUMN id SET DEFAULT nextval('public.faturas_common_tipohorario_id_seq'::regclass);


--
-- Name: faturas_common_tipoquantidade id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipoquantidade ALTER COLUMN id SET DEFAULT nextval('public.faturas_common_tipoquantidade_id_seq'::regclass);


--
-- Name: faturas_common_tipotarifa id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipotarifa ALTER COLUMN id SET DEFAULT nextval('public.faturas_common_tipotarifa_id_seq'::regclass);


--
-- Name: tenant_client id; Type: DEFAULT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.tenant_client ALTER COLUMN id SET DEFAULT nextval('public.tenant_client_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add client	7	add_client
26	Can change client	7	change_client
27	Can delete client	7	delete_client
28	Can view client	7	view_client
29	Can add Cidade	8	add_cidade
30	Can change Cidade	8	change_cidade
31	Can delete Cidade	8	delete_cidade
32	Can view Cidade	8	view_cidade
33	Can add Distribuidora	9	add_distribuidora
34	Can change Distribuidora	9	change_distribuidora
35	Can delete Distribuidora	9	delete_distribuidora
36	Can view Distribuidora	9	view_distribuidora
37	Can add Estado	10	add_estado
38	Can change Estado	10	change_estado
39	Can delete Estado	10	delete_estado
40	Can view Estado	10	view_estado
41	Can add modelo negocio	11	add_modelonegocio
42	Can change modelo negocio	11	change_modelonegocio
43	Can delete modelo negocio	11	delete_modelonegocio
44	Can view modelo negocio	11	view_modelonegocio
45	Can add Pais	12	add_pais
46	Can change Pais	12	change_pais
47	Can delete Pais	12	delete_pais
48	Can view Pais	12	view_pais
49	Can add tipo contrato	13	add_tipocontrato
50	Can change tipo contrato	13	change_tipocontrato
51	Can delete tipo contrato	13	delete_tipocontrato
52	Can view tipo contrato	13	view_tipocontrato
53	Can add tipo quantidade	14	add_tipoquantidade
54	Can change tipo quantidade	14	change_tipoquantidade
55	Can delete tipo quantidade	14	delete_tipoquantidade
56	Can view tipo quantidade	14	view_tipoquantidade
57	Can add bandeira	15	add_bandeira
58	Can change bandeira	15	change_bandeira
59	Can delete bandeira	15	delete_bandeira
60	Can view bandeira	15	view_bandeira
61	Can add tipo tarifa	16	add_tipotarifa
62	Can change tipo tarifa	16	change_tipotarifa
63	Can delete tipo tarifa	16	delete_tipotarifa
64	Can view tipo tarifa	16	view_tipotarifa
65	Can add tipo horario	17	add_tipohorario
66	Can change tipo horario	17	change_tipohorario
67	Can delete tipo horario	17	delete_tipohorario
68	Can view tipo horario	17	view_tipohorario
69	Can add tipo energia	18	add_tipoenergia
70	Can change tipo energia	18	change_tipoenergia
71	Can delete tipo energia	18	delete_tipoenergia
72	Can view tipo energia	18	view_tipoenergia
73	Can add fatura	19	add_fatura
74	Can change fatura	19	change_fatura
75	Can delete fatura	19	delete_fatura
76	Can view fatura	19	view_fatura
77	Can add item energia	20	add_itemenergia
78	Can change item energia	20	change_itemenergia
79	Can delete item energia	20	delete_itemenergia
80	Can view item energia	20	view_itemenergia
81	Can add historico robo	21	add_historicorobo
82	Can change historico robo	21	change_historicorobo
83	Can delete historico robo	21	delete_historicorobo
84	Can view historico robo	21	view_historicorobo
85	Can add historico fatura	22	add_historicofatura
86	Can change historico fatura	22	change_historicofatura
87	Can delete historico fatura	22	delete_historicofatura
88	Can view historico fatura	22	view_historicofatura
89	Can add AcessoDistribuidora	23	add_acessodistribuidora
90	Can change AcessoDistribuidora	23	change_acessodistribuidora
91	Can delete AcessoDistribuidora	23	delete_acessodistribuidora
92	Can view AcessoDistribuidora	23	view_acessodistribuidora
93	Can add acesso distribuidora url	24	add_acessodistribuidoraurl
94	Can change acesso distribuidora url	24	change_acessodistribuidoraurl
95	Can delete acesso distribuidora url	24	delete_acessodistribuidoraurl
96	Can view acesso distribuidora url	24	view_acessodistribuidoraurl
97	Can add Conta	25	add_conta
98	Can change Conta	25	change_conta
99	Can delete Conta	25	delete_conta
100	Can view Conta	25	view_conta
101	Can add Empresa	26	add_empresa
102	Can change Empresa	26	change_empresa
103	Can delete Empresa	26	delete_empresa
104	Can view Empresa	26	view_empresa
105	Can add usina	27	add_usina
106	Can change usina	27	change_usina
107	Can delete usina	27	delete_usina
108	Can view usina	27	view_usina
109	Can add projeto gd	28	add_projetogd
110	Can change projeto gd	28	change_projetogd
111	Can delete projeto gd	28	delete_projetogd
112	Can view projeto gd	28	view_projetogd
113	Can add meta economia	29	add_metaeconomia
114	Can change meta economia	29	change_metaeconomia
115	Can delete meta economia	29	delete_metaeconomia
116	Can view meta economia	29	view_metaeconomia
117	Can add item rateio	30	add_itemrateio
118	Can change item rateio	30	change_itemrateio
119	Can delete item rateio	30	delete_itemrateio
120	Can view item rateio	30	view_itemrateio
121	Can add item contrato	31	add_itemcontrato
122	Can change item contrato	31	change_itemcontrato
123	Can delete item contrato	31	delete_itemcontrato
124	Can view item contrato	31	view_itemcontrato
125	Can add Token	32	add_token
126	Can change Token	32	change_token
127	Can delete Token	32	delete_token
128	Can view Token	32	view_token
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$150000$sFpISSNtFohb$mkCR4zO/qhXFHUJfaZwaZ8+GOdbqHGunqG7Rz5urt7g=	2019-05-15 16:48:48.846172+00	t	leonardo.jesus@geraeb.com.br			leonardo.jesus@geraeb.com.br	t	t	2019-05-15 16:48:36.916561+00
2	pbkdf2_sha256$150000$rF4getFevaVl$6L0YZy5V2rrAlFPMHc5863B4PsRXg4Fxkad2lKQ/OHA=	\N	t	murdoc			luanteylo@gmail.com	t	t	2019-06-10 23:23:34.420266+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: common_cidade; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_cidade (id, nome, estado_id) FROM stdin;
\.


--
-- Data for Name: common_distribuidora; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_distribuidora (id, name, description, "timestamp", is_active, created_by_id, estado_id) FROM stdin;
\.


--
-- Data for Name: common_estado; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_estado (id, nome, uf, pais_id) FROM stdin;
\.


--
-- Data for Name: common_modelonegocio; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_modelonegocio (id, nome) FROM stdin;
1	Geração Local
2	Autoconsumo Remoto
3	Consórcio
4	Cooperativa
\.


--
-- Data for Name: common_pais; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_pais (id, nome, sigla) FROM stdin;
1	Brasil	BR
\.


--
-- Data for Name: common_tipocontrato; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.common_tipocontrato (id, nome) FROM stdin;
1	Desconto Fixo
2	Tarifa Fixa
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	tenant	client
8	common	cidade
9	common	distribuidora
10	common	estado
11	common	modelonegocio
12	common	pais
13	common	tipocontrato
14	faturas_common	tipoquantidade
15	faturas_common	bandeira
16	faturas_common	tipotarifa
17	faturas_common	tipohorario
18	faturas_common	tipoenergia
19	faturas	fatura
20	faturas	itemenergia
21	faturas	historicorobo
22	faturas	historicofatura
23	api	acessodistribuidora
24	api	acessodistribuidoraurl
25	api	conta
26	api	empresa
27	api	usina
28	api	projetogd
29	api	metaeconomia
30	api	itemrateio
31	api	itemcontrato
32	authtoken	token
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2019-06-08 00:04:10.429+00
2	auth	0001_initial	2019-06-08 00:04:11.025779+00
3	admin	0001_initial	2019-06-08 00:04:12.059527+00
4	admin	0002_logentry_remove_auto_add	2019-06-08 00:04:12.226555+00
5	admin	0003_logentry_add_action_flag_choices	2019-06-08 00:04:12.286306+00
6	common	0001_initial	2019-06-08 00:04:12.973462+00
7	common	0002_auto_20190607_1903	2019-06-08 00:04:13.469084+00
8	api	0001_initial	2019-06-08 00:04:13.807184+00
9	contenttypes	0002_remove_content_type_name	2019-06-08 00:04:13.926033+00
10	auth	0002_alter_permission_name_max_length	2019-06-08 00:04:13.977393+00
11	auth	0003_alter_user_email_max_length	2019-06-08 00:04:14.150348+00
12	auth	0004_alter_user_username_opts	2019-06-08 00:04:14.248894+00
13	auth	0005_alter_user_last_login_null	2019-06-08 00:04:14.311417+00
14	auth	0006_require_contenttypes_0002	2019-06-08 00:04:14.36428+00
15	auth	0007_alter_validators_add_error_messages	2019-06-08 00:04:14.449862+00
16	auth	0008_alter_user_username_max_length	2019-06-08 00:04:14.566606+00
17	auth	0009_alter_user_last_name_max_length	2019-06-08 00:04:14.639503+00
18	auth	0010_alter_group_name_max_length	2019-06-08 00:04:14.695399+00
19	auth	0011_update_proxy_permissions	2019-06-08 00:04:14.779284+00
20	authtoken	0001_initial	2019-06-08 00:04:14.83181+00
21	authtoken	0002_auto_20160226_1747	2019-06-08 00:04:14.922455+00
22	sessions	0001_initial	2019-06-08 00:04:15.10489+00
23	tenant	0001_initial	2019-06-08 00:04:15.469883+00
38	common	0002_auto_20190515_1318	2019-05-15 18:18:19.131177+00
39	api	0002_auto_20190515_1757	2019-05-15 22:58:06.13334+00
40	api	0003_remove_empresa_distribuidora	2019-05-15 23:23:25.086511+00
41	api	0004_auto_20190515_1844	2019-05-15 23:44:49.643683+00
42	faturas	0002_auto_20190515_1923	2019-05-16 00:23:47.503129+00
43	api	0005_auto_20190515_2002	2019-05-16 01:02:10.266997+00
44	api	0006_remove_conta_meta_economia	2019-05-16 01:27:14.069585+00
45	api	0007_auto_20190605_1625	2019-06-05 21:25:21.219381+00
46	faturas	0003_historicofatura_historicorobo	2019-06-05 21:25:21.306176+00
47	api	0008_auto_20190605_1952	2019-06-06 00:59:37.466665+00
50	authtoken	0001_initial	2019-06-06 18:59:33.645453+00
51	authtoken	0002_auto_20160226_1747	2019-06-06 18:59:33.835109+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
hh5uw88nl1eri6phvj70ixxpgte2zv45	YzUzYTc1ZGU3ODMyZTZiYTgyMTYzNGM4ODIwMGM5NDlmZGMwNTFmNjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI2ZTNiNDY1MTFlMWU5N2VmMzhhZmExNTQxMTBkMzM3ZDM0NGYwYWRmIn0=	2019-05-29 16:48:48.858209+00
wh3qf2aes73kfqs5qigtzk5xjz3s3j9v	YzUzYTc1ZGU3ODMyZTZiYTgyMTYzNGM4ODIwMGM5NDlmZGMwNTFmNjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI2ZTNiNDY1MTFlMWU5N2VmMzhhZmExNTQxMTBkMzM3ZDM0NGYwYWRmIn0=	2019-06-21 19:02:37.544937+00
q1yuqxfqxg0hny3qkdp834pev6yc6pjb	YzUzYTc1ZGU3ODMyZTZiYTgyMTYzNGM4ODIwMGM5NDlmZGMwNTFmNjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI2ZTNiNDY1MTFlMWU5N2VmMzhhZmExNTQxMTBkMzM3ZDM0NGYwYWRmIn0=	2019-06-22 22:15:26.578748+00
\.


--
-- Data for Name: faturas_common_bandeira; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.faturas_common_bandeira (id, tipo) FROM stdin;
1	VERDE
2	AMARELA
3	VERMELHA
\.


--
-- Data for Name: faturas_common_tipoenergia; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.faturas_common_tipoenergia (id, tipo) FROM stdin;
1	ENERGIA CONSUMIDA
2	ENERGIA INJETADA
3	ENERGIA FORNECIDA
4	ENERGIA REATIVA
5	DEMANDA ATIVA
6	ULTRAPASSAGEM
7	CUSTO DISPONIBILIDADE
8	SALDO GERACAO
9	SALDO GERACAO PONTA
\.


--
-- Data for Name: faturas_common_tipohorario; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.faturas_common_tipohorario (id, tipo) FROM stdin;
1	PONTA
2	FORA PONTA
3	INTERMEDIARIA
\.


--
-- Data for Name: faturas_common_tipoquantidade; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.faturas_common_tipoquantidade (id, tipo) FROM stdin;
1	KWH
2	TARIFA
3	VALOR
4	KW
5	KVA
\.


--
-- Data for Name: faturas_common_tipotarifa; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.faturas_common_tipotarifa (id, tipo) FROM stdin;
1	TE
2	TUSD
3	COMPOSTO
\.


--
-- Data for Name: tenant_client; Type: TABLE DATA; Schema: public; Owner: gera1
--

COPY public.tenant_client (id, domain_url, schema_name, name, is_active, created_on) FROM stdin;
1	demo.portalgera.localhost	demo	demo	t	2019-05-10
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 128, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: common_cidade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_cidade_id_seq', 1, false);


--
-- Name: common_distribuidora_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_distribuidora_id_seq', 12, true);


--
-- Name: common_estado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_estado_id_seq', 1, false);


--
-- Name: common_modelonegocio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_modelonegocio_id_seq', 4, true);


--
-- Name: common_pais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_pais_id_seq', 1, false);


--
-- Name: common_tipocontrato_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.common_tipocontrato_id_seq', 2, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 3, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 44, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 51, true);


--
-- Name: faturas_common_bandeira_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.faturas_common_bandeira_id_seq', 1, false);


--
-- Name: faturas_common_tipoenergia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.faturas_common_tipoenergia_id_seq', 1, false);


--
-- Name: faturas_common_tipohorario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.faturas_common_tipohorario_id_seq', 1, false);


--
-- Name: faturas_common_tipoquantidade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.faturas_common_tipoquantidade_id_seq', 1, false);


--
-- Name: faturas_common_tipotarifa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.faturas_common_tipotarifa_id_seq', 1, false);


--
-- Name: tenant_client_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gera1
--

SELECT pg_catalog.setval('public.tenant_client_id_seq', 11, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: common_cidade common_cidade_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_cidade
    ADD CONSTRAINT common_cidade_pkey PRIMARY KEY (id);


--
-- Name: common_distribuidora common_distribuidora_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_distribuidora
    ADD CONSTRAINT common_distribuidora_pkey PRIMARY KEY (id);


--
-- Name: common_estado common_estado_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_estado
    ADD CONSTRAINT common_estado_pkey PRIMARY KEY (id);


--
-- Name: common_modelonegocio common_modelonegocio_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_modelonegocio
    ADD CONSTRAINT common_modelonegocio_pkey PRIMARY KEY (id);


--
-- Name: common_pais common_pais_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_pais
    ADD CONSTRAINT common_pais_pkey PRIMARY KEY (id);


--
-- Name: common_tipocontrato common_tipocontrato_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_tipocontrato
    ADD CONSTRAINT common_tipocontrato_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: faturas_common_bandeira faturas_common_bandeira_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_bandeira
    ADD CONSTRAINT faturas_common_bandeira_pkey PRIMARY KEY (id);


--
-- Name: faturas_common_tipoenergia faturas_common_tipoenergia_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipoenergia
    ADD CONSTRAINT faturas_common_tipoenergia_pkey PRIMARY KEY (id);


--
-- Name: faturas_common_tipohorario faturas_common_tipohorario_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipohorario
    ADD CONSTRAINT faturas_common_tipohorario_pkey PRIMARY KEY (id);


--
-- Name: faturas_common_tipoquantidade faturas_common_tipoquantidade_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipoquantidade
    ADD CONSTRAINT faturas_common_tipoquantidade_pkey PRIMARY KEY (id);


--
-- Name: faturas_common_tipotarifa faturas_common_tipotarifa_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.faturas_common_tipotarifa
    ADD CONSTRAINT faturas_common_tipotarifa_pkey PRIMARY KEY (id);


--
-- Name: tenant_client tenant_client_domain_url_key; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.tenant_client
    ADD CONSTRAINT tenant_client_domain_url_key UNIQUE (domain_url);


--
-- Name: tenant_client tenant_client_pkey; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.tenant_client
    ADD CONSTRAINT tenant_client_pkey PRIMARY KEY (id);


--
-- Name: tenant_client tenant_client_schema_name_key; Type: CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.tenant_client
    ADD CONSTRAINT tenant_client_schema_name_key UNIQUE (schema_name);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: common_cidade_id_estado_id_f89c2e51; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX common_cidade_id_estado_id_f89c2e51 ON public.common_cidade USING btree (estado_id);


--
-- Name: common_distribuidora_created_by_id_500ea82c; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX common_distribuidora_created_by_id_500ea82c ON public.common_distribuidora USING btree (created_by_id);


--
-- Name: common_distribuidora_sigla_id_247bb5b1; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX common_distribuidora_sigla_id_247bb5b1 ON public.common_distribuidora USING btree (estado_id);


--
-- Name: common_estado_id_pais_id_bd53d131; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX common_estado_id_pais_id_bd53d131 ON public.common_estado USING btree (pais_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: tenant_client_domain_url_1c08c38b_like; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX tenant_client_domain_url_1c08c38b_like ON public.tenant_client USING btree (domain_url varchar_pattern_ops);


--
-- Name: tenant_client_schema_name_c49f34ff_like; Type: INDEX; Schema: public; Owner: gera1
--

CREATE INDEX tenant_client_schema_name_c49f34ff_like ON public.tenant_client USING btree (schema_name varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: common_cidade common_cidade_estado_id_cb4b33ed_fk_common_estado_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_cidade
    ADD CONSTRAINT common_cidade_estado_id_cb4b33ed_fk_common_estado_id FOREIGN KEY (estado_id) REFERENCES public.common_estado(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: common_distribuidora common_distribuidora_created_by_id_500ea82c_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_distribuidora
    ADD CONSTRAINT common_distribuidora_created_by_id_500ea82c_fk_auth_user_id FOREIGN KEY (created_by_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: common_distribuidora common_distribuidora_estado_id_56697849_fk_common_estado_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_distribuidora
    ADD CONSTRAINT common_distribuidora_estado_id_56697849_fk_common_estado_id FOREIGN KEY (estado_id) REFERENCES public.common_estado(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: common_estado common_estado_pais_id_b797eaaf_fk_common_pais_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.common_estado
    ADD CONSTRAINT common_estado_pais_id_b797eaaf_fk_common_pais_id FOREIGN KEY (pais_id) REFERENCES public.common_pais(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: gera1
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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

DROP DATABASE postgres;
--
-- Name: postgres; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE postgres WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE postgres OWNER TO postgres;

\connect postgres

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
-- Name: DATABASE postgres; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


--
-- PostgreSQL database dump complete
--

--
-- Database "test" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

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
-- Name: test; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE test WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE test OWNER TO postgres;

\connect test

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
-- Name: execution; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.execution (
    id integer NOT NULL,
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    instance_id character varying NOT NULL
);


ALTER TABLE public.execution OWNER TO postgres;

--
-- Name: execution_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.execution_status (
    execution_id integer NOT NULL,
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    instance_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    status character varying
);


ALTER TABLE public.execution_status OWNER TO postgres;

--
-- Name: instance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance (
    id character varying NOT NULL,
    type character varying,
    region character varying,
    zone character varying,
    market character varying,
    price double precision
);


ALTER TABLE public.instance OWNER TO postgres;

--
-- Name: instance_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance_status (
    instance_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    status character varying
);


ALTER TABLE public.instance_status OWNER TO postgres;

--
-- Name: instance_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instance_type (
    type character varying NOT NULL,
    vcpu integer,
    memory double precision
);


ALTER TABLE public.instance_type OWNER TO postgres;

--
-- Name: job; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job (
    id integer NOT NULL,
    name character varying,
    description character varying
);


ALTER TABLE public.job OWNER TO postgres;

--
-- Name: job_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.job_id_seq OWNER TO postgres;

--
-- Name: job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_id_seq OWNED BY public.job.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task (
    job_id integer NOT NULL,
    task_id integer NOT NULL,
    command character varying,
    memory double precision,
    io double precision
);


ALTER TABLE public.task OWNER TO postgres;

--
-- Name: job id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job ALTER COLUMN id SET DEFAULT nextval('public.job_id_seq'::regclass);


--
-- Data for Name: execution; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.execution (id, job_id, task_id, instance_id) FROM stdin;
1	1	0	xyz
1	1	1	xyz
\.


--
-- Data for Name: execution_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.execution_status (execution_id, job_id, task_id, instance_id, "timestamp", status) FROM stdin;
1	1	0	xyz	2019-03-13 13:45:19.089362	waiting
1	1	0	xyz	2019-03-13 13:45:19.08952	waiting
1	1	0	xyz	2019-03-13 13:45:19.089662	running
\.


--
-- Data for Name: instance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance (id, type, region, zone, market, price) FROM stdin;
xyz	c3.xlarge			spot	0.5
\.


--
-- Data for Name: instance_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance_status (instance_id, "timestamp", status) FROM stdin;
xyz	2019-03-13 13:45:19.055422	running
\.


--
-- Data for Name: instance_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instance_type (type, vcpu, memory) FROM stdin;
c3.xlarge	2	2
\.


--
-- Data for Name: job; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job (id, name, description) FROM stdin;
1	Test	A Simple Job
\.


--
-- Data for Name: task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task (job_id, task_id, command, memory, io) FROM stdin;
1	0	Test	2	1
1	1	Test	2	1
\.


--
-- Name: job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_id_seq', 1, false);


--
-- Name: execution execution_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_pkey PRIMARY KEY (id, job_id, task_id, instance_id);


--
-- Name: execution_status execution_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution_status
    ADD CONSTRAINT execution_status_pkey PRIMARY KEY (execution_id, job_id, task_id, instance_id, "timestamp");


--
-- Name: instance instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance
    ADD CONSTRAINT instance_pkey PRIMARY KEY (id);


--
-- Name: instance_status instance_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_status
    ADD CONSTRAINT instance_status_pkey PRIMARY KEY (instance_id, "timestamp");


--
-- Name: instance_type instance_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_type
    ADD CONSTRAINT instance_type_pkey PRIMARY KEY (type);


--
-- Name: job job_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job
    ADD CONSTRAINT job_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (job_id, task_id);


--
-- Name: execution execution_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.instance(id);


--
-- Name: execution execution_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution
    ADD CONSTRAINT execution_job_id_fkey FOREIGN KEY (job_id, task_id) REFERENCES public.task(job_id, task_id);


--
-- Name: execution_status execution_status_execution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.execution_status
    ADD CONSTRAINT execution_status_execution_id_fkey FOREIGN KEY (execution_id, job_id, task_id, instance_id) REFERENCES public.execution(id, job_id, task_id, instance_id);


--
-- Name: instance_status instance_status_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance_status
    ADD CONSTRAINT instance_status_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.instance(id);


--
-- Name: instance instance_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instance
    ADD CONSTRAINT instance_type_fkey FOREIGN KEY (type) REFERENCES public.instance_type(type);


--
-- Name: task task_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.job(id);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

