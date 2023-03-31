package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"regexp"

	_ "github.com/mattn/go-sqlite3"
)

type Movie struct {
	Rank    int
	Title   string
	Watched bool
}

var validPath = regexp.MustCompile("^/(reset|save)/$")

func getMoviesFromMyMDB() []Movie {
	return getMoviesFromDB("./mymdb.sqlite")
}

func getMoviesFromDB(dbfile string) []Movie {
	db, err := sql.Open("sqlite3", dbfile)
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
	return movies
}

/*
func makeHandler(fn func(http.ResponseWriter, *http.Request, string)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		m := validPath.FindStringSubmatch(r.URL.Path)
		if m == nil {
			http.NotFound(w, r)
			return
		}
		fn(w, r, m[2])
	}
}

func saveHandler(w http.ResponseWriter, r *http.Request) {

}
*/

func main() {
	movies := getMoviesFromMyMDB()
	tmpl := template.Must(template.ParseFiles("table.html"))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		err := tmpl.Execute(w, movies)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})
	//http.HandleFunc("/save/", makeHandler(saveHandler))

	//http.HandleFunc("/reset/", makeHandler(resetHandler))
	// '/' handler already resets

	fmt.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
