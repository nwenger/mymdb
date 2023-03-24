package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"

    _ "github.com/mattn/go-sqlite3"
)

type Movie struct {
	Rank    int
	Title   string
	Watched bool
}

func main() {
	db, err := sql.Open("sqlite3", "./mymdb.sqlite")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	rows, err := db.Query("SELECT rank, title, watched FROM movies ORDER BY rank ASC")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	var movies []Movie

	for rows.Next() {
		var m Movie
		err := rows.Scan(&m.Rank, &m.Title, &m.Watched)
		if err != nil {
			log.Fatal(err)
		}
		movies = append(movies, m)
	}
	err = rows.Err()
	if err != nil {
		log.Fatal(err)
	}

	tmpl := template.Must(template.ParseFiles("table.html"))

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		err := tmpl.Execute(w, movies)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	fmt.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

