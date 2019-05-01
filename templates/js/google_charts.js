google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic() {
    let data = new google.visualization.DataTable();
    data.addColumn('number', 'game');
    data.addColumn('number', 'elo');
    //data.addColumn('number', 'username')

    data.addRows([
        {% for data in graph_data %}
        [ {{data.game_number}}, {{data.values}}],
        {% endfor %}
        /*
        [0, 800, 800],
        [1, 805, 800],
        [2, 807, 867],
        [3, 810, 777]
        */
    ]);

    let options = {
        //curveType: 'function',
        'width':'100%',
        'height': 500,

        hAxis: {
            title: 'Time'
        },
        vAxis: {
            title: 'Rating'
        }
    };

    let chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    /*
    function selectHandler() {
        var selectedItem = chart.getSelection()[0];
        if (selectedItem) {
            if (selectedItem.row !== 0) {
                window.open('/core/game/' + selectedItem.row);
            }
        }
    }

    google.visualization.events.addListener(chart, 'select', selectHandler);
    */
    chart.draw(data, options);
}