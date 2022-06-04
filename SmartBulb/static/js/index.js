let date = new Date();

const renderCalender = () => {
  const viewYear = date.getFullYear();
  const viewMonth = date.getMonth();

  document.querySelector('.year-month').textContent = `${viewYear}년 ${viewMonth + 1}월`;

  const prevLast = new Date(viewYear, viewMonth, 0);
  const thisLast = new Date(viewYear, viewMonth + 1, 0);

  const PLDate = prevLast.getDate();
  const PLDay = prevLast.getDay();

  const TLDate = thisLast.getDate();
  const TLDay = thisLast.getDay();

  const prevDates = [];
  const thisDates = [...Array(TLDate + 1).keys()].slice(1);
  const nextDates = [];

  if (PLDay !== 6) {
    for (let i = 0; i < PLDay + 1; i++) {
      prevDates.unshift(PLDate - i);
    }
  }

  for (let i = 1; i < 7 - TLDay; i++) {
    nextDates.push(i);
  }

  const dates = prevDates.concat(thisDates, nextDates);
  const firstDateIndex = dates.indexOf(1);
  const lastDateIndex = dates.lastIndexOf(TLDate);

  dates.forEach((date, i) => {
    const condition = i >= firstDateIndex && i < lastDateIndex + 1
                      ? 'this'
                      : 'other';
    if (condition == 'this' && isPublished(date, viewMonth + 1, viewYear)) {
        dates[i] = `<div class="date"><img class="img_pub" src="../static/img/checked.png"><span class=${condition}><a href="save_diary/${viewYear}/${viewMonth + 1}/${date}">${date}</a></span></div>`;
    } else if (condition == 'this') {
        dates[i] = `<div class="date"><span class=${condition}><a href="save_diary/${viewYear}/${viewMonth + 1}/${date}">${date}</a></span></div>`;
    } else {
        dates[i] = `<div class="date"><span class=${condition}>${date}</span></div>`;
    }


  });

  document.querySelector('.dates').innerHTML = dates.join('');

  const today = new Date();
  if (viewMonth === today.getMonth() && viewYear === today.getFullYear()) {
    for (let date of document.querySelectorAll('.this')) {
      if (+date.innerText === today.getDate()) {
        date.classList.add('today');
        break;
      }
    }
  }
};

const prevMonth = () => {
  date.setDate(1);
  date.setMonth(date.getMonth() - 1);
  renderCalender();
}

const nextMonth = () => {
  date.setDate(1);
  date.setMonth(date.getMonth() + 1);
  renderCalender();
}

const goToday = () => {
  date = new Date();
  renderCalender();
};

function isPublished(date, month, year) {
    var dates = document.getElementsByClassName('date_published');
    var tmp = ""
    var result = false;

    for (var i = 0; i < dates.length; i++) {
        tmp = dates[i].innerHTML.split("-");
        if (parseInt(tmp[2]) == parseInt(date) && parseInt(tmp[1]) == parseInt(month) && parseInt(tmp[0]) == parseInt(year)) {
            result = true;
        }
    }


    return result;
}


renderCalender();

