function setFlashMessageContent(eltId, message) {
  $(`#${eltId} .flash-alert-content`).html(message);
}

function flashMessage(eltId, duration = 4000) {
  let eltTag = '#' + eltId;
  $(eltTag).fadeIn('fast', () => {
    $(eltTag).delay(duration).fadeOut('slow');
  });
}

function flashMessages() {
  // flash messages
  let messages = localStorage.getItem('flashMessages');
  if (messages) {
    let d = JSON.parse(messages);
    for (const [eltId, message] of Object.entries(d)) {
      setFlashMessageContent(eltId, message);
      flashMessage(eltId);
    }
    localStorage.removeItem('flashMessages');
  }
}

function addFlashMessage(eltId, message) {
  let messages = localStorage.getItem('flashMessages');
  let d = {}
  if (messages) {
    let d = JSON.parse(messages);
  }
  d[eltId] = message;
  localStorage.setItem('flashMessages', JSON.stringify(d));
}

// redirects to a route of the application; if redirect = true, addes a redirect query parameter with the current URL
function redirectToRoute(route, redirect = false) {
  let baseUrl = window.location.origin;
  let url = new URL(route, baseUrl);
  if (redirect) {
    let locUrl = new URL(window.location.href);
    url.searchParams.set('redirect', locUrl);
  }
  console.log(`Redirecting to ${url}`);
  window.location.replace(url);
}