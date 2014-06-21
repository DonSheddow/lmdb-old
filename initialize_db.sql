CREATE TYPE type AS ENUM('movie', 'series');

CREATE TABLE films (
                    pathname varchar(256) UNIQUE NOT NULL,
                    id SERIAL PRIMARY KEY,
                    title text,
                    start_year smallint, 
                    end_year smallint,
                    plot text,
                    imdbid char(9),
                    type type,
                    awards text,
                    metascore smallint,
                    imdbrating real,
                    tomatometer smallint,
                    tomatoconsensus text,
                    tomatousermeter smallint,
                    tomatoimage text
);

CREATE TABLE genres (
                     film_id integer REFERENCES films ON DELETE CASCADE,
                     genre text
);

CREATE TABLE people (
                     id SERIAL PRIMARY KEY,
                     name text UNIQUE NOT NULL
);

CREATE TABLE performances (
                           film_id integer REFERENCES films ON DELETE CASCADE,
                           actor_id integer REFERENCES people,
                           character text,
                           order_of_appearance integer
);

CREATE TABLE crew (
                   film_id integer REFERENCES films ON DELETE CASCADE,
                   crewmember_id integer REFERENCES people,
                   department text
);
