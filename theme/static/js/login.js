function refreshLoginDisplay() {
  let loginState = getLocalLoginState();
  if (loginState.isLoggedIn) {
    try {
      let username = loginState.data.user.username;
      $('.user-greeting').html(`Hello, <b>${username}</b>!`);
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

$('#login-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  let formData = new FormData(elt.target);
  const loginUrl = getAuthUrl('/login');
  fetch(loginUrl, { method: 'POST', body: formData }).then(loginStateFromResponse).then((loginState) => {
    // store the login state
    localStorage.setItem('loginState', JSON.stringify(loginState));
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
  fetch(logoutUrl, { method: 'POST' }).then((response) => {
    return loginStateFromResponse(response, false);
  }).then((loginState) => {
    localStorage.setItem('loginState', JSON.stringify(loginState));
    console.log('User is logged out.');
    console.log('Login state:', loginState.data);
    refreshLoginDisplay();
  });
});

$('#signup-form').submit(function(elt) {
  clearInvalid(elt.target);
  let obj = {};
  let inputs = $(elt.target).find('input');
  obj['username'] = inputs[0].value;
  obj['email'] = inputs[1].value;
  obj['password'] = inputs[2].value;
  let body = JSON.stringify(obj);
  let xhr = new XMLHttpRequest();
  let url = authUrl + '/users/create?welcome=true';
  xhr.open('POST', url, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      if (xhr.status == 0) {
        alert('Error: could not connect to Nessiness login server.')
      }
      let response = JSON.parse(xhr.responseText);
      if (xhr.status == 409) {  // user or email already exists
        let msg = response.detail;
        let tokens = msg.split(' ');
        let i = (tokens[2] == 'username') ? 0 : 1;
        let token = (i == 0) ? 'Username' : 'Email';
        $(inputs[i]).addClass('is-invalid');
        $(inputs[i]).parent().append(`<div class="invalid-feedback">${token} already exists.</div>`);
      }
      else if (xhr.status == 422) {  // invalid email address
        $(inputs[1]).addClass('is-invalid');
        $(inputs[1]).parent().append('<div class="invalid-feedback">Invalid email address.</div>');
      }
      else if (xhr.status == 200) {
        let email = inputs[1].value;
        $('#signup-modal').modal('hide');
        $('#signup-success .success-msg').html(`Account created successfully!<br><br>Sent email to <b>${email}</b>`);
        $('#signup-success').fadeIn('fast', function() {
          $(this).delay(5000).fadeOut('slow');
        });
        loginToggle();
      }
      else {
        alert('Unknown error occurred.')
      }
    }
  };
  xhr.send(body);
  return false;
});

$('#signup-toggle').click(signupToggle);

$('#login-toggle').click(loginToggle);