let date = new Date();

const linkStatistics  = () => {
   const viewYear = date.getFullYear();
   const viewMonth = date.getMonth();

   const link = `<div class="link"><a href="../../diary/statistics/${viewYear}/${viewMonth + 1}">감정 통계 보기</a></div>`;

   document.querySelector('#link').innerHTML = link;
};

linkStatistics();