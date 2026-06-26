// 定义一个名为 fetchData 的函数，用于从服务器获取传感器数据并更新网页上的显示内容
function fetchData() {
    // 使用 Fetch API 发起一个 GET 请求，向服务器的 /data 路由请求最新的传感器数据
    fetch('/data')
        // 当服务器返回响应时，将响应转换为 JSON 格式
        .then(response => response.json())
        // 处理转换后的 JSON 数据
        .then(data => {
            // 查找页面上 ID 为 'co2' 的元素，并将其文本内容设置为从服务器获取到的 CO2 数据
            document.getElementById('co2').textContent = data.co2;

            // 查找页面上 ID 为 'ch2o' 的元素，并将其文本内容设置为从服务器获取到的 CH2O 数据
            document.getElementById('ch2o').textContent = data.ch2o;

            // 查找页面上 ID 为 'tvoc' 的元素，并将其文本内容设置为从服务器获取到的 TVOC 数据
            document.getElementById('tvoc').textContent = data.tvoc;

            // 查找页面上 ID 为 'pm2_5' 的元素，并将其文本内容设置为从服务器获取到的 PM2.5 数据
            document.getElementById('pm2_5').textContent = data.pm2_5;

            // 查找页面上 ID 为 'pm10' 的元素，并将其文本内容设置为从服务器获取到的 PM10 数据
            document.getElementById('pm10').textContent = data.pm10;

            // 查找页面上 ID 为 'temp' 的元素，并将其文本内容设置为从服务器获取到的温度数据
            document.getElementById('temp').textContent = data.temp;

            // 查找页面上 ID 为 'hum' 的元素，并将其文本内容设置为从服务器获取到的湿度数据
            document.getElementById('hum').textContent = data.hum;

            // 查找页面上 ID 为 'timestamp' 的元素，并将其文本内容设置为从服务器获取到的时间戳数据
            document.getElementById('timestamp').textContent = data.timestamp;
        });
}

// 当网页内容加载完成后执行以下代码
document.addEventListener('DOMContentLoaded', function() {
    // 首先调用 fetchData 函数，立即获取并显示初始数据
    fetchData();

    // 设置一个定时器，每隔 1 秒（1000 毫秒）调用一次 fetchData 函数，确保数据持续实时更新
    setInterval(fetchData, 1000);
});
