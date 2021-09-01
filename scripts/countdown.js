import parseMilliseconds from "./parse-ms.js";
const countdownElement = document.getElementById(
  "timelastuntilteknofest"
);
setInterval(() => {
  const milliseconds = 1631772000000 - Date.now();
  const parsed = parseMilliseconds(milliseconds);
  const spans = countdownElement.getElementsByTagName("span");
  spans[0].textContent = parsed.days;
  spans[1].textContent = parsed.hours;
  spans[2].textContent = parsed.minutes;
  spans[3].textContent = parsed.seconds;
}, 10);

