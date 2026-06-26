async function fetchData() {
    const response = await fetch('/data');
    const data = await response.json();
    return data;
}

async function fetchGPSData() {
    const response = await fetch('/gps_data');
    const data = await response.json();
    return data;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();  // 只显示小时分钟秒
}

function createChart(ctx, label, data, dataKey, color) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamp.reverse().map(formatTimestamp),  // 格式化时间戳
            datasets: [{
                label: label,
                data: data[dataKey].reverse(),
                borderColor: color,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            }
        }
    });
}

async function updateChart(chart, data, dataKey) {
    chart.data.labels = data.timestamp.reverse().map(formatTimestamp);  // 格式化时间戳
    chart.data.datasets[0].data = data[dataKey].reverse();
    chart.update();
}

async function updateMap(map) {
    const gpsData = await fetchGPSData();
    const position = new AMap.LngLat(gpsData.longitude, gpsData.latitude);

    map.setCenter(position);
    map.setZoom(15);

    new AMap.Marker({
        position: position,
        map: map
    });
}

document.addEventListener('DOMContentLoaded', async function () {
    const data = await fetchData();

    const co2Chart = createChart(document.getElementById('co2Chart').getContext('2d'), 'CO2', data, 'co2', 'rgb(255, 99, 132)');
    const ch2oChart = createChart(document.getElementById('ch2oChart').getContext('2d'), 'CH2O', data, 'ch2o', 'rgb(54, 162, 235)');
    const tvocChart = createChart(document.getElementById('tvocChart').getContext('2d'), 'TVOC', data, 'tvoc', 'rgb(75, 192, 192)');
    const pm25Chart = createChart(document.getElementById('pm25Chart').getContext('2d'), 'PM2.5', data, 'pm2_5', 'rgb(153, 102, 255)');  // 创建PM2.5折线图
    const pm10Chart = createChart(document.getElementById('pm10Chart').getContext('2d'), 'PM10', data, 'pm10', 'rgb(255, 159, 64)');  // 创建PM10折线图
    const tempChart = createChart(document.getElementById('tempChart').getContext('2d'), 'Temp', data, 'temp', 'rgb(255, 206, 86)');  // 创建温度折线图
    const humChart = createChart(document.getElementById('humChart').getContext('2d'), 'Humidity', data, 'hum', 'rgb(255, 192, 203)');  // 创建湿度折线图

    setInterval(async function () {
        const newData = await fetchData();
        await updateChart(co2Chart, newData, 'co2');
        await updateChart(ch2oChart, newData, 'ch2o');
        await updateChart(tvocChart, newData, 'tvoc');
        await updateChart(pm25Chart, newData, 'pm2_5');
        await updateChart(pm10Chart, newData, 'pm10');
        await updateChart(tempChart, newData, 'temp');
        await updateChart(humChart, newData, 'hum');
    }, 1000);  // 每秒更新一次图表数据

    const map = new AMap.Map('mapContainer', {
        zoom: 15,
        center: [108.8288, 34.1313],  // 初始中心点
    });

    setInterval(async function () {
        await updateMap(map);
    }, 1000);  // 每秒更新一次地图数据
});
