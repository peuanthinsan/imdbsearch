# IMDb Search API: People and Movies
Search peoples' names and their contributions as director, creator, or actor on the [IMDb Top 1000 Movies](http://imdb.com/search/title?groups=top_1000).

## Running API on Docker, `http://localhost:8000`
Install [docker and docker-compose](https://docs.docker.com/compose/install/).
```
docker-compose up
```
or
```
docker-compose up --build
```
After indexing is finished, the API can be accessed at `http://localhost:8000/?name=`

## Example
### Searching by name
`?name=spielberg` returns movies involving first, last, or middle names that start with `spielberg`
```
[  
   {  
      "Steven Spielberg":{  
         "directors":[  
            "Schindler's List",
            "Saving Private Ryan",
            "Raiders of the Lost Ark",
            "Indiana Jones and the Last Crusade",
            "Jurassic Park",
            "Catch Me If You Can",
            "Jaws",
            "E.T. the Extra-Terrestrial",
            "Empire of the Sun",
            "The Color Purple",
            "Minority Report",
            "Close Encounters of the Third Kind",
            "Bridge of Spies",
            "Indiana Jones and the Temple of Doom",
            "Munich"
         ],
         "creators":[  
            "The Goonies",
            "Close Encounters of the Third Kind"
         ]
      }
   }
]
```
`?name=stephen` returns movies involving first, last, or middle names that start with `stephen`
```
[  
   {  
      "Stephen King":{  
         "creators":[  
            "The Shawshank Redemption",
            "The Green Mile",
            "The Shining",
            "Stand by Me",
            "Misery"
         ]
      }
   },
   {  
      "Stephen P. Lindsey":{  
         "creators":[  
            "Hachi: A Dog's Tale"
         ]
      }
   },
   {  
      "Stephen Boyd":{  
         "actors":[  
            "Ben-Hur"
         ]
      }
   },
   {  
      "Stephen Chbosky":{  
         "directors":[  
            "Wonder",
            "The Perks of Being a Wallflower"
         ],
         "creators":[  
            "Wonder",
            "The Perks of Being a Wallflower",
            "The Perks of Being a Wallflower"
         ]
      }
   },
   {  
      "Stephen Young":{  
         "actors":[  
            "Patton"
         ]
      }
   },
   {  
      "Stephen McFeely":{  
         "creators":[  
            "Captain America: Civil War",
            "Captain America: The Winter Soldier"
         ]
      }
   },
   {  
      "Stephen Chow":{  
         "directors":[  
            "Kung Fu Hustle"
         ],
         "creators":[  
            "Kung Fu Hustle"
         ],
         "actors":[  
            "Kung Fu Hustle"
         ]
      }
   },
   {  
      "Stephen Beresford":{  
         "creators":[  
            "Pride"
         ]
      }
   },
   {  
      "Stephen Trask":{  
         "creators":[  
            "Hedwig and the Angry Inch"
         ],
         "actors":[  
            "Hedwig and the Angry Inch"
         ]
      }
   },
   {  
      "Stephen Graham":{  
         "actors":[  
            "This Is England"
         ]
      }
   },
   {  
      "Stephen Daldry":{  
         "directors":[  
            "Billy Elliot",
            "The Reader",
            "The Hours"
         ]
      }
   },
   {  
      "Stephen Gaghan":{  
         "creators":[  
            "Traffic"
         ]
      }
   },
   {  
      "Stephen Frears":{  
         "directors":[  
            "Dangerous Liaisons",
            "Philomena"
         ]
      }
   },
   {  
      "Harvey Stephens":{  
         "actors":[  
            "The Omen"
         ]
      }
   }
]
```

## Simplifying Assumptions
It helped to focus on defining assumptions towards crawling, parsing, and indexing.

Crawling and parsing was simplified by assuming:
- a fixed data set
- no network errors
- a fixed URL structure: i.e. `/search/title?page=[1 through 20]` (and exactly 20 list pages)
- a fixed HTML structure for all list and movie pages

Search and indexing was simplified by assuming:
- a search and index primarily and only for peoples' names
- the search results will be small number of peoples' names (as keys) that will fit in memory

## Possible Improvements
If I had more time to improve the quality and architecture of this code, these are some things I could work on:
- handling cases of timeouts, connection errors, memory limits, or server errors
- string and data structure validation
- unit and functional testing
- generalizing the search methods (`find`, `index`, `search`) into its own interface, so that multiple crawlers/parsers could use an instance of it

If this code were to scale to handle several requests at a time, a load balancer and http caching like nginx would help performance.
