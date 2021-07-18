## SmiteAPI-Dev

![maintenance](https://img.shields.io/badge/maintained-yes-green.svg)
![maintenance](https://img.shields.io/badge/python-3.9-blue.svg)
![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)

<h3>Database</h3>

<h4>1. Structure</h4>

- `[smiteapi].[dbo].[players]`

Table storing basic information about the player.


| Column        | Type           | Description  |
|:--------------:|:---------------:|:------------:|
| ID      | `int` | player ID       |
| nickname            | `nvarchar`        |   player nickname        |
| lvl            | `int`        |   player lvl        |
| clanID | `int`        |    clan ID         |
| avatarUrl | `nvarchar`        |    player's avatar        |
| createdAt | `date`        |    date of account creation         |
| hoursPlayed | `int`        |    number of hours played         |
| lastLoginDate | `date`        |    last date of login        |
| leaves | `int`        |    total number of leaves         |
| masteryLevel | `int`        |    amount of gods that are mastered        |

---

- `[smiteapi].[dbo].[testplayers]`

Table that we can use for testing reasons, structure is the same as above.

---

- `[smiteapi].[dbo].[motd]`

Table storing all information about motd. Stores data of prospective, current and archived motds. 


| Column        | Type           | Description  |
|:--------------:|:---------------:|:------------:|
| name      | `nvarchar` | name of the motd       |
| description            | `nvarchar`        |   full description about motd        |
| validDate            | `datetime`        |   motd start date        |

<h4>2. Functions</h4>

 > *healthcheck():*

Checks the connection to the database server. This function does not take any arguments. Returns response if the application was able to connect to the database.

---

> *run_query(query, operation):*

Send a request to the database, function takes two arguments `query` and `operation`. If the operation parameter equals *read*, function will return all requested data. However if we selected *write* the function will only display status of operation (sucess or error).
 
<h5>Parameters:</h5>

- Query: database request, example: `SELECT * FROM [table_name] WHERE col1 = "DEV"`
 
- Operation : direction of request, if we want to read data from db we should use **read** parameter, in other cases when we would like to insert/update/delete we need to use **write** argument.

---
