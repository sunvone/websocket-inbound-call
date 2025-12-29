import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 4143 });

wss.on("connection", (ws, req) => {
  console.log("Client connected", req.headers);

  ws.on("message", (data, isBinary) => {
    if (!isBinary) {
      const payload = JSON.parse(data);

      if (payload && payload.event) {
        switch (payload.event) {
          case "incoming_call":
            console.log("Incoming call received:", {
              event: "incoming_call",
              callerId: payload.callerId,
              didNumber: payload.didNumber,
              sessionId: payload.sessionId,
            });
            setTimeout(() => {
              console.log("send action answer call");
              ws.send(
                JSON.stringify({
                  event: "answer",
                })
              );

              //simulation send dtmf
              setTimeout(() => {
                ws.send(
                  JSON.stringify({
                    event: "dtmf",
                    digit: "1", //digit 0-9 * and #
                    duration: 200, //duration dtmf in milisecond  max 1000ms
                  })
                );
              }, 2000);

              setTimeout(() => {
                console.log("send action hangup call");
                ws.send(
                  JSON.stringify({
                    event: "hangup",
                  })
                );
              }, 1000 * 10);
            }, 5000);
            break;
          /***
           * receive dtmf evebt from client
           */
          case "dtmf":
            console.log("DTMF received:", {
              event: "dtmf",
              digit: payload.digit,
            });
            break;
          /**
           * receive hangup event from client
           */
          case "hangup":
            console.log("Hangup received:", {
              event: "hangup",
            });
            break;
          case "cdr":
            console.log("Cdr received:", {
              event: "cdr",
              sessionId: payload.sessionId,
              destination: payload.destination,
              startTime: payload.startTime,
              answerTime: payload.answerTime,
              endTime: payload.endTime,
              duration: payload.duration,
              billableSeconds: payload.billableSeconds,
              disposition: payload.disposition,
              hangupBy: payload.hangupBy,
              hangupCauseCode: payload.hangupCauseCode,
              hangupCauseText: payload.hangupCauseText,
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
