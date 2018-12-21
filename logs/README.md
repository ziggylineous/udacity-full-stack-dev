# Logs Report

## Intro
This project is the first of the Udacity Full Stack Dev ND. It is a report about an articles database. This database consists on 3 tables:
- articles: with the article's title, body, subtitle and author (FK to authors table)
- authors: with its name and biography
- logs: which consists in each HTTP request done to the site. It has the result status for each requests, date and path. The path is a string that if it starts with '/articles/', is a request for an article.

#### Requirements
The requirements for the report were:
1. What are the most popular three _articles_ of all time?
2. Who are the most popular article _authors_ of all time?
3. On which days did more than 1% of requests lead to errors?

#### Dev Tools
To solve these requirements I've used:
- Python programming (functions, objects, error handling, list comprehensions, ...);
- The Python DB API to connect to a database (the db engine being psql, and I connected to it using the psycopg2 module);
- SQL views and functions.

## Running
To run this project you'll need to install:
1. [Python 3](https://www.python.org/downloads/).
2. [VirtualBox](https://www.virtualbox.org/wiki/Downloads), for running the VM with the psql database. You only need the platform package for your operating system (not the extension pack nor the sdk).  You do not need to launch VirtualBox after installing it.
3. [Vagrant](https://www.vagrantup.com/downloads.html). Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.
4. Clone the [full stack vm repo](https://github.com/udacity/fullstack-nanodegree-vm.) containing the VM files. After cloning it, navigate to the vagrant folder. Here you must run `vagrant up`. This will download Linux; it will take a while. Then run `vagrant ssh` to log into the vm.
5. Install the database in the vm. To do this, put the file [news.sql](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) in the vagrant shared folder, log into the vm, navigate to the shared folder (`cd /vagrant`) and run `psql -d news -f newsdata.sql`.
6. Finally, still connected to the vm, run `python3 logs_report.py`


## Program Design - Organization
Each of the requirements it's an option for the user. Each of these option is implemented with a `Command` object. These options are in the `OPTIONS` list. The command can be a `QueryCommand` or an `ExitCommand`. They have an `execute()` in which they do some proccessing and format it. The `ExitCommand` just returns a exit message. The `QueryCommand` sends a select query to the database and formats the query results with a formatter function.

In the `main()` loop:
1. I show each command with its `message` attribute
2. Make the user select one option
3. `execute()` and format the command


## SQL Views and Functions
#### 1. What are the most popular three articles of all time?
I created 2 views, `articles_visit_counts` and `most_popular_articles`, to make the queries simpler. 

The first one counts the views of an article grouped by its slug. In this view, I also made 2 functions:
- `is_article_view`, tells if a log is an article view
- `path_to_slug`, transforms a path to the article's slug

```
CREATE FUNCTION is_article_view(status text, path text) RETURNS boolean AS $$
    SELECT
        status = '200 OK' AND
        path LIKE '/article/%'
$$ LANGUAGE SQL;

CREATE FUNCTION path_to_slug(path text) RETURNS text AS $$
    SELECT replace(path, '/article/', '')
$$ LANGUAGE SQL;

CREATE VIEW articles_visit_counts AS
SELECT path_to_slug(path) slug, COUNT(id) visit_count
FROM log
WHERE is_article_view(status, path)
GROUP BY path
```

To get the article data I joined `articles_visit_counts` with `articles` in  the second view, `most_popular_articles`. I also ordered it by `visit_count` so that from python I had to do less work:

```
CREATE VIEW most_popular_articles AS
SELECT A.id, A.title, A.slug, A.author, COALESCE(visit_count, 0) visit_count
FROM articles A
LEFT JOIN articles_visit_counts AVC
ON A.slug = AVC.slug
ORDER BY visit_count DESC
```


#### 2. Who are the most popular article authors of all time? 
To know how many views an author had, I just needed to join the `most_popular_articles` table with the `authors` one. I abstracted this in the `most_popular_authors` view:

```
CREATE VIEW most_popular_authors AS
SELECT Au.id id, Au.name, COALESCE(SUM(visit_count), 0) as visit_count
FROM authors Au
LEFT JOIN most_popular_articles Ar
ON Au.id = Ar.author
GROUP BY Au.id
ORDER BY visit_count DESC;
```


#### 3. On which days did more than 1% of requests lead to errors?
1. I truncated the `log` `day` column and kept only the day part in the view `log_day_trunc`
2. I created the function `is_error_status_count` to turn a status string to 1 or 0 if it was an error
3. Then I grouped by day and summed up the error status codes (in the `error_proportion_per_day` view)

```
CREATE FUNCTION is_error_status(status text) RETURNS boolean AS $$
    SELECT CASE
        WHEN substr(status, 0, 4) >= '400' THEN TRUE
        ELSE FALSE
    END
$$ LANGUAGE SQL;

CREATE FUNCTION is_error_status_count(status text) RETURNS integer AS $$
    SELECT CASE
        WHEN is_error_status(status) THEN 1
        ELSE 0
    END
$$ LANGUAGE SQL;

CREATE FUNCTION percentage(part bigint, total bigint) RETURNS numeric AS $$
    SELECT CAST(part AS numeric) / CAST(total AS numeric) * 100.0
$$ LANGUAGE SQL;
 
CREATE VIEW log_day_trunc AS
SELECT *, date_trunc('day', time) AS day FROM log;

CREATE VIEW error_proportion_per_day AS
SELECT day, percentage(SUM(is_error_status_count(status)), COUNT(id)) AS proportion
FROM log_day_trunc
GROUP BY day;
```