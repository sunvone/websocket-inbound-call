import { WebSocketServer } from "ws";
import { randomUUID } from "crypto";

const wss = new WebSocketServer({ port: 4143 });

wss.on("connection", (ws, req) => {
  console.log("Client connected");

  const sessionId = randomUUID();

  setTimeout(() => {
    console.log("send action incoming call");
    ws.send(
      JSON.stringify({
        event: "incoming_call",
        sessionId: sessionId,
      })
    );

    setTimeout(() => {
      console.log("send action answer call");
      ws.send(
        JSON.stringify({
          event: "answer",
          sessionId: sessionId,
        })
      );

      setTimeout(() => {
        console.log("send action hangup call");
        ws.send(
          JSON.stringify({
            event: "hangup",
          })
        );
      }, 1000 * 10);
    }, 5000);
  }, 1000);

  ws.on("message", (data, isBinary) => {
    if (!isBinary) {
      const payload = JSON.parse(data);
     

      if (payload && payload.event) {
        switch (payload.event) {
          /***
           * receive dtmf evebt from client
           */
          case "dtmf":
            console.log("DTMF received:", {
              event: "dtmf",
              sessionId: payload.sessionId,
              digit: payload.digit,
            });
            break;
            /**
             * receive hangup event from client
             */
           case "hangup":
             console.log("Hangup received:", {
               event: "hangup",
               sessionId: payload.sessionId,
             });
             break;
         }
      }
    } else {
      //audio data
      ws.send(data); // send back
    }
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });

  ws.on("error", (err) => {
    console.error("WS error:", err.message);
  });
});

console.log("WS server listening on :4143");
