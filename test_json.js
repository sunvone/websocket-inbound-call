import { Buffer } from 'buffer';

const buf = Buffer.from(JSON.stringify({ foo: 'bar' }));
try {
  const result = JSON.parse(buf);
  console.log("Success:", result);
} catch (e) {
  console.log("Error:", e.message);
}
