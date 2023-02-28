const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function dateToStr(date) {
  let monthName = monthNames[date.getMonth()];
  let day = date.getDate();
  let year = date.getFullYear();
  return `${monthName} ${day}, ${year}`;
}

function datetimeToStr(date) {
  let dateStr = dateToStr(date);
  let timeStr = date.toTimeString().slice(0, 17);
  return `${dateStr} ${timeStr}`;
}

function timestampToDate(timestamp) {
  let year = timestamp.slice(0, 4);
  let month = timestamp.slice(5, 7);
  let day = timestamp.slice(8, 10);
  let date = new Date();
  date.setFullYear(year);
  date.setMonth(month);
  date.setDate(day);
  return date;
}

function loadProfile() {
  return requiresLogin(() => {
    let loginState = getLocalLoginState();
    let data = loginState.data;
    let user = data.user;
    let accessToken = data.access_token;
    let refreshToken = data.refresh_token;
    let tbody = $('#profile-table').find('tbody');
    const addRow = (name, value) => {
      let row = `<tr><td>${name}:</td><td>${value}</td></tr>`;
      tbody.append(row);
    };
    addRow('Username', user.username);
    addRow('E-mail', user.email);
    addRow('Date created', dateToStr(timestampToDate(user.created_at)));
    addRow('Access level', user.access);
    let rememberYes = '<span class="remember-me"><input type="radio" name="remember-me" ';
    let rememberNo = '<span class="remember-me"><input type="radio" name="remember-me" ';
    if (accessToken.remember_me) {
      rememberYes += 'checked';
    }
    else {
      rememberNo += 'checked';
    }
    rememberYes += ' value="yes"></input><label for="yes">yes</label></span>';
    rememberNo += ' value="no"></input><label for="no">no</label></span>';
    addRow('Remember me', rememberYes + rememberNo);

    let showExtra = isDev || (['super', 'admin'].includes(user.access));
    if (showExtra) {
      accessIssued = new Date(accessToken.iat * 1000);
      addRow('Access token issued', datetimeToStr(accessIssued));
      accessExpires = new Date(accessToken.exp * 1000);
      addRow('Access token expires', datetimeToStr(accessExpires));
      if (refreshToken != null) {
        refreshIssued = new Date(refreshToken.iat * 1000);
        addRow('Refresh token issued', datetimeToStr(refreshIssued));
        refreshExpires = new Date(refreshToken.exp * 1000);
        addRow('Refresh token expires', datetimeToStr(refreshExpires));
      }
    }

    $('#delete-account-msg').html(`Delete your Nessiness account? All data associated with <b>${user.username}</b> will be deleted.`);
    // $(function () {
    //   $("[rel='tooltip']").tooltip({selector: "[title]"});
    // });
  });
}

$('#profile-table tbody').on('change', 'input[type=radio][name=remember-me]', function() {
  // refresh the access token when user toggles 'remember me'
  let rememberMe = (this.value == 'yes');
  refreshAccessToken(rememberMe);
});

$('#delete-account-btn').click((elt) => {
  let username = getCurrentUser();
  $('#delete-account-modal').modal('hide');
  localStorage.setItem('deletedUser', username);
  redirectToRoute('/', false);
});