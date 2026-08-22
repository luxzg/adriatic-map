// Adriatic Map is licensed under GPL-3.0-or-later. See LICENSE.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"syscall"
	"time"

	"github.com/luxzg/adriatic-map/internal/server"
)

const version = "0.2.1"

func main() {
	listenAddress := flag.String("listen", "127.0.0.1:8080", "HTTP listen address")
	open := flag.Bool("open", true, "open the map in the default browser")
	showVersion := flag.Bool("version", false, "print the application version and exit")
	flag.Parse()

	if *showVersion {
		fmt.Println(version)
		return
	}

	log.SetFlags(0)
	listener, err := net.Listen("tcp", *listenAddress)
	if err != nil {
		log.Fatalf("cannot listen on %s: %v", *listenAddress, err)
	}

	httpServer := &http.Server{
		Handler:           server.New(server.Config{Version: version}),
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	url := "http://" + listener.Addr().String() + "/"
	log.Printf("Adriatic Map %s is available at %s", version, url)

	if *open {
		go func() {
			if err := openBrowser(url); err != nil {
				log.Printf("could not open the browser automatically: %v", err)
				log.Printf("open %s manually", url)
			}
		}()
	}

	serveErrors := make(chan error, 1)
	go func() {
		serveErrors <- httpServer.Serve(listener)
	}()

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
	select {
	case sig := <-signals:
		log.Printf("received %s; shutting down", sig)
	case err := <-serveErrors:
		if !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("HTTP server failed: %v", err)
		}
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := httpServer.Shutdown(ctx); err != nil {
		log.Fatalf("HTTP server shutdown failed: %v", err)
	}
}

func openBrowser(url string) error {
	var command *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		command = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	case "darwin":
		command = exec.Command("open", url)
	default:
		command = exec.Command("xdg-open", url)
	}
	return command.Start()
}
