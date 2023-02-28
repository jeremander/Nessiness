function flashAlert(eltTag, duration = 4000) {
  $(eltTag).fadeIn('fast', () => {
    $(eltTag).delay(duration).fadeOut('slow');
  });
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