google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(GetGraph);

function drawBasic(player_data) {
    let data = new google.visualization.DataTable();

    data.addColumn('number', 'game');
    data.addColumn('number', 'elo');

    data.addRows(player_data);

    let options = {
        'width':'100%',
        'height': 500,
         gridlines: { count: 10},

        hAxis: {
            title: 'Games'
        },
        vAxis: {
            title: 'Rating'
        }
    };
    let container = document.getElementById('chart_div');
    let chart = new google.visualization.LineChart(container);
    chart.draw(data, options);

}


function ParseJSON(text) {
    const json = JSON.parse(text);
    if (json.games !== undefined) {
        console.log(json.games);
        drawBasic(json.games);
    }
}

function GetGraph() {
    const currentLocation = window.location;
    console.log(currentLocation);
    httpGetAsync(currentLocation + "/get_graph", ParseJSON);
}