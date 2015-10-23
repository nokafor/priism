// Your Client ID can be retrieved from your project in the Google
// Developer Console, https://console.developers.google.com

var SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"];


/**
* Handle response from authorization server.
*
* @param {Object} authResult Authorization result.
*/
function handleAuthResult(authResult) {
var authorizeDiv = document.getElementById('authorize-div');
var outputDiv = document.getElementById('output');
var calendarDiv = document.getElementById('calendars');

if (authResult && !authResult.error) {
  // Hide auth UI, then load client library.
  authorizeDiv.style.display = 'none';
  outputDiv.style.display = 'none';
  calendarDiv.style.display = 'block';
  loadCalendarApi();
} else {
  // Show auth UI, allowing the user to initiate authorization by
  // clicking authorize button.
  authorizeDiv.style.display = 'inline';
  outputDiv.style.display = 'none';
  calendarDiv.style.display = 'none';
}
}

/**
* Initiate auth flow in response to user clicking authorize button.
*
* @param {Event} event Button click event.
*/
function handleAuthClick(event, client_id) {
	CLIENT_ID = client_id;
gapi.auth.authorize(
  {client_id: CLIENT_ID, scope: SCOPES, immediate: false},
  handleAuthResult);
return false;
}

/**
* Load Google Calendar client library. List upcoming events
* once client library is loaded.
*/
function loadCalendarApi() {
gapi.client.load('calendar', 'v3', listCalendars);
}

/**
* Print the summary and start datetime/date of the next ten events in
* the authorized user's calendar. If no events are found an
* appropriate message is printed.
*/
function listUpcomingEvents(calendar_id) {
	var outputDiv = document.getElementById('output');
	var calendarDiv = document.getElementById('calendars');
	outputDiv.style.display = 'block';
  	calendarDiv.style.display = 'none';

	var request = gapi.client.calendar.events.list({
	  'calendarId': calendar_id,
	  'timeMin': (new Date()).toISOString(),
	  'showDeleted': false,
	  'singleEvents': true,
	  'maxResults': 10,
	  'orderBy': 'startTime'
	});

	request.execute(function(resp) {
		var events = resp.items;
		var div = document.getElementById('output');
		var weekday = new Array(7);
		weekday[0]=  "Sun";
		weekday[1] = "Mon";
		weekday[2] = "Tue";
		weekday[3] = "Wed";
		weekday[4] = "Thu";
		weekday[5] = "Fri";
		weekday[6] = "Sat";

		if (events.length > 0) {
		    for (i = 0; i < events.length; i++) {
		      var event = events[i];
		      var beg = event.start.dateTime;
		      var end = event.end.dateTime;
		      if (!beg) {
		        beg = event.start.date;
		      }
		      if (!end) {
		      	end = event.end.date;
		      }
		      var newEvent = document.createElement('div');
		      var divIdName = 'event'+i;
		      newEvent.setAttribute('id', divIdName);
		      var beg_date = new Date(beg);
		      var end_date = new Date(end);
		      var date = event.summary +'-'+ weekday[beg_date.getDay()] + '-' + beg_date.getTime()+'-' + beg_date.getTimezoneOffset() +'-'+ end_date.getTime()+'-'+end_date.getTimezoneOffset();
		      var display = weekday[beg_date.getDay()] +'. '+beg_date.toLocaleTimeString() +'-'+end_date.toLocaleTimeString();
		      newEvent.innerHTML = event.summary + ' (' + display + ')' + ' <a id=\"add\" href=\"add/'+date+'/\">Save</a>';
		      div.appendChild(newEvent);
		      // appendPre(event.summary + ' (' + end_date.toLocaleString() + ')');
		    }
		} else {
		    // appendPre('No upcoming events found.');
		    var newEvent = document.createElement('div');
		    newEvent.setAttribute('class', 'text-muted');
		    newEvent.innerHTML='No upcoming events found.';
		    div.appendChild(newEvent)
		}

	});
}

function listCalendars() {
var request = gapi.client.calendar.calendarList.list({
  'showHidden': true,
  'maxResults': 10
});

request.execute(function(resp) {
  var calendars = resp.items;
  var div = document.getElementById('calendars');

  if (calendars.length > 0) {
    for (i = 0; i < calendars.length; i++) {
      var calendar = calendars[i];

      var newEvent = document.createElement('div');
      var divIdName = 'calendar'+i;
      newEvent.setAttribute('id', divIdName);
      var functionName = 'listUpcomingEvents(\'' + calendar.id + '\')';
      newEvent.innerHTML = '<a href=\"#output\" onclick=' + functionName+'>' +calendar.summary+'</a>';
      div.appendChild(newEvent);
      // appendPre(event.summary + ' (' + end_date.toLocaleString() + ')');
    }
  } else {
    // appendPre('No upcoming events found.');
    var newEvent = document.createElement('div');
    newEvent.setAttribute('class', 'text-muted');
    newEvent.innerHTML='No calendars found.';
    div.appendChild(newEvent)
  }

});
}
