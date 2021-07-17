## SmiteAPI-Dev

![maintenance](https://img.shields.io/badge/maintained-yes-green.svg)
![maintenance](https://img.shields.io/badge/python-3.9-blue.svg)
![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)

###Database structure

- `[smiteapi].[dbo].[players]`

Table storing basic information about the player.


| Columns        | Type           | Description  |
|:--------------:|:---------------:|:------------:|
| accountID      | `int` | player ID       |
| nickname            | `nvarchar`        |   player nickname        |
| lvl            | `int`        |   player Lvl        |
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