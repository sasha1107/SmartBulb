new Chart(document.getElementById("pie-chart"), {
    type: 'pie',
    data: {
      labels: ["긍정", "부정", "중립"],
      datasets: [{
        label: "Population (millions)",
        backgroundColor: ["#3EACFA", "#fa5c58","#3cba9f"],
        data: [15,10,5]
      }]
    },
    options: {
      title: {
        display: false,
        text: '한 달 동안 다음와 같은 감정이 있었네요.'
      }
    }
});