// gets the full URL for the auth server at the given path
function getAuthUrl(path) {
  return authUrl + path;
}

async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 8000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  const response = await fetch(resource, {
    ...options,
    signal: controller.signal
  });
  clearTimeout(id);
  return response;
}

function loginStateFromResponse(response, isLogin = true) {
  let status = response.status;
  if ((status == 200) || (status == 401)) {
    return response.json().then((data) => {
      let isLoggedIn = isLogin ? (status == 200) : false;
      return { status, data, isLoggedIn };
    });
  }
  else {
    return null;
  }
}

// gets the current login state of the user, returning null if the user is not logged in (or timeout occurs)
async function fetchUserLoginState() {
  const url = getAuthUrl('/users/me');
  const response = await fetchWithTimeout(url, {timeout: 3000});
  return loginStateFromResponse(response);
}

// gets the current login state of the user stored in localstorage
function getLocalLoginState() {
  let loginStateStr = localStorage.getItem('loginState');
  let loginState = (loginStateStr === null) ? null : JSON.parse(loginStateStr);
  return loginState;
}

// refreshes the login state of the user
// if the user has a valid access token, stores the token info in local storage
async function refreshUserLoginState() {
  let loginState = getLocalLoginState();
  if (loginState === null) {  // unknown login state, so fetch it from auth server
    console.log('User login status unknown.');
    loginState = await fetchUserLoginState();
  }
  if (loginState) {
    if (loginState.isLoggedIn) {  // user is logged in
      let accessToken = loginState.data.access_token;
      console.log(accessToken);
      let expiry = accessToken.exp * 1000;  // expiration time (milliseconds since epoch)
      let currentTimestamp = Date.now();
      if (currentTimestamp >= expiry) {
        // TODO: refresh access token
        console.log('Access token is expired.')
      }
      else {
        console.log('User is logged in.')
        console.log('Login state:', loginState.data);
      }
    }
    else {  // not logged in
      console.log('User is not logged in.')
    }
    localStorage.setItem('loginState', JSON.stringify(loginState));
  }
}
