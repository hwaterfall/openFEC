SET search_path = public, pg_catalog;

DO
$body$
DECLARE
    v_role text;
    k_roles text[] = '{
         "fec",
         "fec_read"
}';
BEGIN
    FOREACH v_role IN ARRAY k_roles LOOP
        IF NOT EXISTS (
                SELECT *
                FROM pg_catalog.pg_roles
                WHERE  rolname = v_role) THEN
            EXECUTE FORMAT('CREATE ROLE %s', v_role);
        END IF;
    END LOOP;
END
$body$;

-- DO $$
-- BEGIN
-- 	EXECUTE format('CREATE ROLE fec');
-- 	EXECUTE format('CREATE ROLE fec_read');
-- EXCEPTION 
-- WHEN duplicate_table THEN 
-- 	null;
-- WHEN others THEN 
-- 	RAISE NOTICE 'some other error: %, %',  sqlstate, sqlerrm;  
-- END$$; 

--
-- Name: ofec_fips_states; Type: TABLE; Schema: public; Owner: fec
--

CREATE TABLE ofec_fips_states (
    index bigint,
    "Name" text,
    "FIPS State Numeric Code" bigint,
    "Official USPS Code" text
);


ALTER TABLE ofec_fips_states OWNER TO fec;

--
-- Name: ix_ofec_fips_states_index; Type: INDEX; Schema: public; Owner: fec
--

CREATE INDEX ix_ofec_fips_states_index ON ofec_fips_states USING btree (index);

--
-- Name: ofec_fips_states; Type: ACL; Schema: public; Owner: fec
--

GRANT SELECT ON TABLE ofec_fips_states TO fec_read;

--
-- Name: ofec_zips_districts; Type: TABLE; Schema: public; Owner: fec
--

CREATE TABLE ofec_zips_districts (
    index bigint,
    "State" bigint,
    "ZCTA" bigint,
    "Congressional District" bigint
);


ALTER TABLE ofec_zips_districts OWNER TO fec;

--
-- Name: ix_ofec_zips_districts_index; Type: INDEX; Schema: public; Owner: fec
--

CREATE INDEX ix_ofec_zips_districts_index ON ofec_zips_districts USING btree (index);


--
-- Name: ofec_zips_districts_ZCTA_idx; Type: INDEX; Schema: public; Owner: fec
--

CREATE INDEX "ofec_zips_districts_ZCTA_idx" ON ofec_zips_districts USING btree ("ZCTA");


--
-- Name: ofec_zips_districts; Type: ACL; Schema: public; Owner: fec
--

GRANT SELECT ON TABLE ofec_zips_districts TO fec_read;
