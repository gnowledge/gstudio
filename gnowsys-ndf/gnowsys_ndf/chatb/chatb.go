package main

import (
	"code.google.com/p/go.net/websocket"
	"flag"
	"html/template"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"time"

	"./rooms"
)

func handleFile(path string) http.HandlerFunc {
	path = filepath.Join(*root, path)
	return func(response http.ResponseWriter, request *http.Request) {
		//log.Println("GET", request.URL.Path, path)
		http.ServeFile(response, request, path)
	}
}

func defaultHandler(response http.ResponseWriter, request *http.Request) {
	index := filepath.Join(*root, "index.html")
	path := filepath.Join(*root, request.URL.Path[1:])
	fi, err := os.Stat(path)
	if fi == nil && err != nil || request.URL.Path == "/" {
		path = index
	}
	//log.Println("GET", request.URL.Path, path)
	if path == index {
		t, err := template.ParseFiles(index)
		if err != nil {
			log.Print(err)
			http.ServeFile(response, request, path)
		} else {
			err = t.Execute(response, template.JS(config))
			if err != nil {
				http.Error(response, err.Error(), http.StatusInternalServerError)
			}
		}
	} else {
		http.ServeFile(response, request, path)
	}
}

var root *string = flag.String("root", "./static",
	"path to static files")

var listenAddr *string = flag.String("http", ":8000",
	"listen on this http address")

var certFile *string = flag.String("cert", "",
	"TLS certificate, if cert and key are provided server will use tls")

var keyFile *string = flag.String("key", "",
	"TLS certificate, if cert and key are provided server will use tls")

var configFile *string = flag.String("config", "",
	"path to config.json")

var config string = "{}"

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	rand.Seed(time.Now().UnixNano())
	flag.Parse()

	if *configFile != "" {
		content, err := ioutil.ReadFile(*configFile)
		if err != nil {
			log.Fatal(err)
		}
		config = string(content)
	}

	http.HandleFunc("/", defaultHandler)
	http.Handle("/_rooms", websocket.Handler(rooms.Handler))

	if *certFile != "" && *keyFile != "" {
		if err := http.ListenAndServeTLS(*listenAddr, *certFile, *keyFile, nil); err != nil {
			log.Fatalf("http.ListenAndServe: %v", err)
		}
	} else {
		if err := http.ListenAndServe(*listenAddr, nil); err != nil {
			log.Fatalf("http.ListenAndServe: %v", err)
		}
	}
}
