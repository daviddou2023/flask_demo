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

function createChart(data) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamp.reverse(),
            datasets: [
                {
                    label: 'CO2',
                    data: data.co2.reverse(),
                    borderColor: 'rgb(255, 99, 132)',
                    fill: false
                },
                {
                    label: 'CH2O',
                    data: data.ch2o.reverse(),
                    borderColor: 'rgb(54, 162, 235)',
                    fill: false
                },
                {
                    label: 'TVOC',
                    data: data.tvoc.reverse(),
                    borderColor: 'rgb(75, 192, 192)',
                    fill: false
                },
                {
                    label: 'PM2.5',
                    data: data.pm2_5.reverse(),
                    borderColor: 'rgb(153, 102, 255)',
                    fill: false
                },
                {
                    label: 'PM10',
                    data: data.pm10.reverse(),
                    borderColor: 'rgb(255, 159, 64)',
                    fill: false
                },
                {
                    label: 'Temperature',
                    data: data.temp.reverse(),
                    borderColor: 'rgb(255, 205, 86)',
                    fill: false
                },
                {
                    label: 'Humidity',
                    data: data.hum.reverse(),
                    borderColor: 'rgb(201, 203, 207)',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Timestamp'
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

    return chart;
}

async function updateChart(chart) {
    const data = await fetchData();

    chart.data.labels = data.timestamp.reverse();
    chart.data.datasets[0].data = data.co2.reverse();
    chart.data.datasets[1].data = data.ch2o.reverse();
    chart.data.datasets[2].data = data.tvoc.reverse();
    chart.data.datasets[3].data = data.pm2_5.reverse();
    chart.data.datasets[4].data = data.pm10.reverse();
    chart.data.datasets[5].data = data.temp.reverse();
    chart.data.datasets[6].data = data.hum.reverse();

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
    const chart = createChart(data);

    setInterval(async function () {
        await updateChart(chart);
    }, 1000);  // 每1秒更新一次数据

    const map = new AMap.Map('mapContainer', {
        zoom: 15,
        center: [108.8288, 34.1313],  // 初始中心点
    });

    setInterval(async function () {
        await updateMap(map);
    }, 1000);  // 每5秒更新一次地图数据
});
