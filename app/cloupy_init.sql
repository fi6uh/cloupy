PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE FILES(
   ID INT PRIMARY KEY      NOT NULL,
   FILENAME       TEXT     NOT NULL,
   FILEPATH       TEXT     NOT NULL,
   FILEAPPPATH    TEXT     NOT NULL,
   SHA256SUM      CHAR(64) NOT NULL
);
CREATE TABLE JOBS(
   ID INT PRIMARY KEY   NOT NULL,
   FILEID         INT   NOT NULL,
   CREATED        TEXT  NOT NULL,
   STATUS         TEXT  NOT NULL
);
CREATE TABLE RESULTS(
   ID INT PRIMARY KEY   NOT NULL,
   JOBID          INT   NOT NULL,
   CREATED        TEXT  NOT NULL,
   RESULTPATH     TEXT  NOT NULL
);
COMMIT;