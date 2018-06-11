# The Backend of MovieGuru

This project is our final project of information retrieval course (delivered by [Prof. Zhumin Chen](http://ir.sdu.edu.cn/~zhuminchen/)) of Shandong University. For study use **ONLY** and **NO** commerical purposes are permitted.

## API Specification

* `GET /search?q={keywords}&offset={0}&limit={0}` Search movies with given keywords. Response is a search result list. Parameters `offset` and `limit` are optional, both of which default to 0.
* `GET /movie?id={id}` Get information of movie with given ID. Response is a movie entity.

## JSON Schemas

Here lists JSON schemas of entities mentioned above.

### JSON Schema of Search Result List

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "matched_fields": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "ranges": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "start": { "type": "integer" },
                  "end": { "type": "integer" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### JSON Schema of Movie Entity

```json
{
  "definitions": {
    "string-array": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "title": { "type": "string" },
    "original_title": { "type": "string" },
    "introduction": { "type": "string" },
    "aliases": { "$ref": "#/definitions/string-array" },
    "tags": { "$ref": "#/definitions/string-array" },
    "genres": { "$ref": "#/definitions/string-array" },
    "poster": {
      "type": "string",
      "format": "uri"
    },
    "staffs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "roles": { "$ref": "#/definitions/string-array" }
        }
      }
    }
  }
}
```
