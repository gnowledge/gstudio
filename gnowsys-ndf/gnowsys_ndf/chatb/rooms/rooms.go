package rooms

import (
	"bytes"
	"code.google.com/p/go.net/websocket"
	"encoding/json"
	"io"
	"log"
	"strconv"
	"time"
)

type Room struct {
	Name  string           `json:"name"`
	Users map[string]*User `json:"users"`
}

type Message struct {
	Type string `json:"type,omitempty"`
	Data string `json:"data,omitempty"`
	To   string `json:"to,omitempty"`
	From string `json:"from,omitempty"`
}

type Cmd struct {
	Action string `json:"action"`
	Data   string `json:"data,omitempty"`
}

type User struct {
	Id   string          `json:"id"`
	Name string          `json:"name"`
	Room *Room           `json:"-"`
	send chan Message    `json:"-"`
	ws   *websocket.Conn `json:"-"`
}

func (r *Room) Join(u *User) {
	if u.Room != r {
		if u.Room != nil {
			u.Room.Leave(u)
		}
		//log.Println("Add user to room:", r.Name)
		u.Room = r
		r.Users[u.Id] = u
		r.SendInfo()
	} else {
		//log.Println("User is already in this room:", r.Name)
	}
}

func (r *Room) Leave(u *User) {
	u.Room = nil
	delete(r.Users, u.Id)
	if len(r.Users) == 0 {
		delete(rooms, r.Name)
	} else {
		r.SendInfo()
	}
}

func (r *Room) Send(m Message) {
	for _, u := range r.Users {
		u.Send(m)
	}
}

func (r *Room) SendOthers(m Message, sender *User) {
	for _, u := range r.Users {
		if u != sender {
			u.Send(m)
		}
	}
}

func (r *Room) SendPrivateMessage(m Message) {
	if user, ok := r.Users[m.To]; ok {
		user.Send(m)
	}
}

func (r *Room) Info() string {
	var b bytes.Buffer
	s, err := json.Marshal(r)
	if err == nil {
		b.Write(s)
	} else {
		log.Println("failed to marshal room", err)
	}
	return b.String()
}

func (r *Room) SendInfo() {
	r.Send(Message{Type: "info", Data: r.Info()})
}

func (u *User) reader() {
	for {
		var message Message
		if err := websocket.JSON.Receive(u.ws, &message); err != nil {
			if err != io.EOF {
				log.Println("invalid message", err)
			}
			break
		}

		if message.Type == "cmd" {
			var cmd Cmd
			if err := json.Unmarshal([]byte(message.Data), &cmd); err != nil {
				log.Println("Invalid command", message.Data)
				break
			}
			if cmd.Action == "leave" {
				if u.Room != nil {
					//log.Println("Leave Room:", u.Room.Name)
					u.Room.Leave(u)
				} else {
					//log.Println("not in any room")
				}
			} else if cmd.Action == "join" {
				if cmd.Data != "" {
					name := cmd.Data
					room, ok := rooms[name]
					if !ok {
						rooms[name] = &Room{Name: name, Users: make(map[string]*User)}
						room = rooms[name]
					}
					room.Join(u)
				}
			} else if cmd.Action == "info" {
				if u.Room != nil {
					u.SendInfo()
				}
			} else if cmd.Action == "nick" {
				u.Name = cmd.Data
				if u.Room != nil {
					u.Room.SendInfo()
				}
			}
		} else if message.To != "" {
			message.From = u.Id
			//log.Println("Sending private message from", message.From, "to", message.To, message)
			u.Room.SendPrivateMessage(message)
		} else {
			message.From = u.Id
			//log.Println("Sending message to room: ", message)
			u.Room.SendOthers(message, u)
		}
	}
	u.ws.Close()
}

func (u *User) writer() {
	for m := range u.send {
		u.ws.SetWriteDeadline(time.Now().Add(5 * time.Second))
		err := websocket.JSON.Send(u.ws, m)
		if err != nil {
			//log.Println("send failed, user disconnected", err)
			break
		}
	}
	u.ws.Close()
}

func (u *User) Send(m Message) {
	u.send <- m
}

func (u *User) SendInfo() {
	u.Send(Message{Type: "info", Data: u.Room.Info()})
}

func IDChan() <-chan (string) {
	next := make(chan string)
	//id := 1
	id := uint64(time.Now().Unix())
	go func() {
		for {
			next <- strconv.FormatUint(id, 10)
			id++
		}
	}()
	return next
}

var getID = IDChan()

func Handler(ws *websocket.Conn) {
	//log.Println("Room connection:", ws.Request().RemoteAddr)
	u := &User{Id: <-getID, send: make(chan Message, 256), ws: ws, Room: nil}
	u.Send(Message{Type: "init", Data: u.Id})
	defer func() {
		//log.Println("Disconnected:", ws.Request().RemoteAddr)
		close(u.send)
		u.send = nil
		if u.Room != nil {
			u.Room.Leave(u)
		}
	}()
	go u.writer()
	u.reader()
}

var rooms = make(map[string]*Room)
