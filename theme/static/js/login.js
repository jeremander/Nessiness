// refreshes the page based on the current login state
function refreshLoginDisplay() {
  let loginState = getLocalLoginState();
  if (loginState.isLoggedIn) {
    try {
      let username = loginState.data.user.username;
      let link = '/profile';
      $('.user-greeting').html(`Hello, <a class="username" href="${link}" onclick="loadProfile()"><b>${username}</b></a>!`);
    }
    catch {
      console.log('Could not get username.');
    }
    finally {
      $('.login-link').hide();
      $('.logout-link').show();
    }
  }
  else {
    $('.user-greeting').html('');
    $('.login-link').show();
    $('.logout-link').hide();
  }
}

function clearInvalid(form) {
  $(form).find('input').removeClass('is-invalid');
  $(form).find('.invalid-feedback').remove();
}

function clearForm(form) {
  clearInvalid(form);
  for (input of $(form).find('input')) {
    if (input.type != 'submit') {
      $(input).val('');
    }
  }
}

function signupToggle() {
  $('#login-box').hide();
  $('#signup-box').show();
  clearForm($('#login-form'));
}

function loginToggle() {
  $('#signup-box').hide();
  $('#login-box').show();
  clearForm($('#signup-form'));
}

function redirectToLogin(elt) {
  if (!isLoggedIn()) {
    if (elt) {
      elt.preventDefault();
    }
    let baseUrl = window.location.origin;
    let loginUrl = new URL('/login', baseUrl);
    let locUrl = new URL(window.location.href);
    loginUrl.searchParams.set('redirect', locUrl);
    console.log(`Redirecting to ${loginUrl}`);
    window.location.replace(loginUrl);
  }
}

$('#login-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  const rememberMe = $(elt.target).find('#remember-me').prop('checked');
  let formData = new FormData(elt.target);
  const loginUrl = getAuthUrl('/login?remember_me=' + rememberMe.toString());
  fetch(loginUrl, {method: 'POST', body: formData}).then(loginStateFromResponse).then((loginState) => {
    // store the login state
    setLocalLoginState(loginState);
    if (loginState.status == 401) {  // authentication error
      let inputs = $(elt.target).find('input');
      $(inputs[1]).addClass('is-invalid');
      let err = loginState.data.detail;
      $(inputs[1]).parent().append(`<div class="invalid-feedback">${err}.</div>`);
    }
    else if (loginState.status == 200) {
      // if a redirect URL is present, redirect back there
      let locUrl = new URL(window.location.href);
      let redirectUrl = locUrl.searchParams.get('redirect');
      if (!redirectUrl) {
        redirectUrl = '/';
      }
      window.location.replace(redirectUrl);
    }
    else {
      alert('Unknown error occurred.');
    }
  });
});

$('.logout-link').click((elt) => {
  elt.preventDefault();
  const logoutUrl = getAuthUrl('/logout');
  fetch(logoutUrl, {method: 'POST'}).then((response) => {
    return loginStateFromResponse(response, false);
  }).then((loginState) => {
    setLocalLoginState(loginState);
    console.log('User is logged out.');
    console.log('Login state:', loginState.data);
    redirectToLogin();
  }).catch(() => {
    console.log('Could not connect to server for logout.');
    setLocalLoginState(null);
  });
});

$('#signup-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  let url = getAuthUrl('/users/create?welcome=true');
  let inputs = $(elt.target).find('input');
  let body = JSON.stringify({username: inputs[0].value, email: inputs[1].value, password: inputs[2].value});
  fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body}).then((response) => {
    return response.json().then((data) => {
      return {status: response.status, data}
    });
  }).then((obj) => {
    if (obj.status == 409) {  // conflict (user/e-mail already exists)
      let err = obj.data.detail;
      let tokens = err.split(' ');
      let i = (tokens[2] == 'username') ? 0 : 1;
      let token = (i == 0) ? 'Username' : 'Email';
      $(inputs[i]).addClass('is-invalid');
      $(inputs[i]).parent().append(`<div class="invalid-feedback">${token} already exists.</div>`);
    }
    else if (obj.status == 422) {  // invalid e-mail address
      $(inputs[1]).addClass('is-invalid');
      $(inputs[1]).parent().append('<div class="invalid-feedback">Invalid email address.</div>');
    }
    else if (obj.status == 200) {  // signup successful
      let email = inputs[1].value;
      $('#signup-modal').modal('hide');
      $('#signup-success .success-msg').html(`Account created successfully!<br><br>Sent email to <b>${email}</b>`);
      $('#signup-success').fadeIn('fast', () => {
        $('#signup-success').delay(5000).fadeOut('slow');
      });
      loginToggle();
    }
    else {
      alert('Unknown error occurred.')
    }
  });
});

$('#signup-toggle').click(signupToggle);

$('#login-toggle').click(loginToggle);