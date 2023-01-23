CREATE TABLE "papers" (
  "id" SERIAL PRIMARY KEY,
  "venue_id" INTEGER,
  "title" VARCHAR(2000),
  "abstract" VARCHAR(150000),
  "year" INTEGER,
  "n_citation" INTEGER,
  "page_start" VARCHAR(100),
  "page_end" VARCHAR(100),
  "issue" VARCHAR(100),
  "volume" VARCHAR(100),
  "keywords" VARCHAR(70000),
  "fos" VARCHAR(4000),
  "doi" VARCHAR(700),
  "pdf" VARCHAR(700),
  "url" VARCHAR(15000)
);

CREATE TABLE "authors" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(300),
  "org" VARCHAR(4000)
);

CREATE TABLE "author_paper" (
  "id" SERIAL PRIMARY KEY,
  "paper_id" INTEGER,
  "author_id" INTEGER
);

CREATE TABLE "venues" (
  "id" SERIAL PRIMARY KEY,
  "raw" VARCHAR(1000),
  "publisher" VARCHAR(500),
  "issn" VARCHAR(500),
  "isbn" VARCHAR(500)
);

CREATE TABLE "papers_refs" (
  "id" SERIAL PRIMARY KEY,
  "parent_paper" INTEGER,
  "child_paper" INTEGER
);

CREATE TABLE "papers_tags" (
  "id" SERIAL PRIMARY KEY,
  "paper_id" INTEGER,
  "tag_id" INTEGER
);

CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY,
  "login" VARCHAR(20),
  "password" VARCHAR(20)
);

CREATE TABLE "tags" (
  "id" SERIAL PRIMARY KEY,
  "tag_name" VARCHAR(200)
);

ALTER TABLE "papers" ADD FOREIGN KEY ("venue_id") REFERENCES "venues" ("id");

ALTER TABLE "author_paper" ADD FOREIGN KEY ("paper_id") REFERENCES "papers" ("id");

ALTER TABLE "author_paper" ADD FOREIGN KEY ("author_id") REFERENCES "authors" ("id");

ALTER TABLE "papers_refs" ADD FOREIGN KEY ("parent_paper") REFERENCES "papers" ("id");

ALTER TABLE "papers_refs" ADD FOREIGN KEY ("child_paper") REFERENCES "papers" ("id");

ALTER TABLE "papers_tags" ADD FOREIGN KEY ("tag_id") REFERENCES "tags" ("id");

ALTER TABLE "papers_tags" ADD FOREIGN KEY ("paper_id") REFERENCES "papers" ("id");

