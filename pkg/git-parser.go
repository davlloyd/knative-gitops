package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"encoding/json"
)

type MessageDumper struct{}

func (md *MessageDumper) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)

	if reqBytes, err := httputil.DumpRequest(r, true); err == nil {
		var result map[string]interface{}
		json.Unmarshal([]byte(reqBytes), &result)
		log.Printf("Message Dumper received a message: %+v", result["commits"])
		w.Write(reqBytes)
	} else {
		log.Printf("Error dumping the request: %+v :: %+v", err, r)
	}
}

func main() {
	http.ListenAndServe(":8080", &MessageDumper{})
}