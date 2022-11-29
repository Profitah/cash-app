function Time() {
  var date = new Date();
  var hour = date.getHours();
  var minute = date.getMinutes();
  var second = date.getSeconds();
  var period = "";
  if (hour >= 12) {
  period = "PM";
  } else {
  period = "AM";
  }
  if (hour == 0) {
  hour = 12;
  } else {
  if (hour > 12) {
  hour = hour - 12;
  }
  }

  hour = update(hour);
  minute = update(minute);
  second = update(second);
  
  document.getElementById("time").innerText = hour + " : " + minute + " : " + second + " " + period;
  
  setTimeout(Time, 1000);
 }

 function update(t) {
  if (t < 10) {
  return "0" + t;
  }
  else {
  return t;
  }
 }
 Time();