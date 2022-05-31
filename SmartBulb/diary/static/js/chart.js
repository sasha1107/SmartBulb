var sentiments = document.getElementsByClassName("sentiment");
var sent_data = new Array(3)

for (var i = 0; i < sentiments.length; i++) {
    sent_data[i] = sentiments[i].innerText.split(":");
}
var ctx = document.getElementById('pie-chart');

var config = {
    type: 'pie',
    data: {
      labels: [sent_data[0][0], sent_data[1][0], sent_data[2][0]],
      datasets: [{
        label: "Population (millions)",
        backgroundColor: ["#3EACFA", "#fa5c58","#3cba9f"],
        data: [sent_data[0][1], sent_data[1][1], sent_data[2][1]]
      }]
    },
    options: {
      title: {
        display: false,
        text: '한 달 동안 다음와 같은 감정이 있었네요.'
      }
    }
}

var chart = new Chart(ctx, config);
