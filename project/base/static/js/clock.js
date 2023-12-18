function updateClock() {
    var now = new Date();
    var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    var day = days[now.getDay()];

    var hours = now.getHours();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;

    var minutes = now.getMinutes();
    minutes = minutes < 10 ? '0' + minutes : minutes;

    var timeString = hours + ':' + minutes + ' ' + ampm;
    
    document.getElementById("day-name").innerHTML = day;
    document.getElementById("current-time").innerHTML = timeString;
}


setInterval(updateClock, 1000);


updateClock();