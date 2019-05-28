
let player_count = 0;

let player_names = [];

let player_pks = [];

class Game {
    constructor(p1, p2, change, id) {
        this.p1 = p1;
        this.p2 = p2;
        this.change = change;
        this.id = id;
    }
}


let games = [];

let mapingPk_index = {};

function CreateDivWithCheckBox(player, checkbox_id) {
    let div = document.createElement("div");
    div.classList.add("input-group-prepend");
    let divcheck = document.createElement("div");
    divcheck.classList.add("input-group-text");
    let input = document.createElement("input");
    input.type = "checkbox";
    input.id = checkbox_id;
    divcheck.appendChild(input);
    div.appendChild(divcheck);
    let label = document.createElement("label");
    label.classList.add("input-group-text");
    label.innerText = player;
    label.setAttribute("for", checkbox_id);
    div.appendChild(label);
    return div;
}

function SetAll() {
    for (let i = 0; i < player_count; i++) {
        let div = document.getElementById("checkbox_" + player_pks[i].toString());
        div.checked = true;
    }
}

function ResetAll() {
    for (let i = 0; i < player_count; i++) {
        let div = document.getElementById("checkbox_" + player_pks[i].toString());
        div.checked = false;
    }
}


google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(GetGraph);

function DrawGraph() {
    let data = new google.visualization.DataTable();

    let checked = [];
    for (let i = 0; i < player_count; i++) {
        checked.push(document.getElementById("checkbox_" + player_pks[i].toString()).checked);
    }

    let checked_cnt = 0;
    for (let i = 0; i < player_count; i++) {
        if (checked[i]) checked_cnt += 1;
    }

    console.log(checked_cnt);

    if (checked_cnt === 0)
        return;


    //Create Game number column
    data.addColumn('number', 'game');
    //Create all players column

    let row = [0];
    let newMaping = {};

    for (let i = 0; i < player_count; i++) {
        if (checked[i]) {
            data.addColumn('number', player_names[i]);
            row.push(800.0);
            newMaping[player_pks[i]] = row.length - 1;
        }
    }


    let curMatrix = [];

    curMatrix.push(row);

    for (let i = 0; i < games.length; i++) {

        let p1_checked = checked[ mapingPk_index[games[i].p1] ];
        let p2_checked = checked[ mapingPk_index[games[i].p2] ];


        if (p1_checked || p2_checked) {
            row = row.slice(); // copy
            row[0] = games[i].id; //change game pk

            if (p1_checked) {
                row[ newMaping[games[i].p1]] += games[i].change;
            }
            if (p2_checked) {
                row[ newMaping[games[i].p2]] -= games[i].change;
            }

            curMatrix.push(row);
        }
    }
    data.addRows(curMatrix);

    const options = {
        'width':'100%',
        'height': 1000,

        hAxis: {
            title: 'Time'
        },
        vAxis: {
            title: 'Rating'
        }
    };

    const chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}

function Render() {
    let holder = document.getElementById("player_selector");

    for (let i = 0; i < player_count; i++) {
        let div = CreateDivWithCheckBox(player_names[i], "checkbox_" + player_pks[i].toString());
        holder.appendChild(div);
    }

    SetAll();
    DrawGraph();
}

function ParseJSON(text) {
    const json = JSON.parse(text);

    if (json.games === undefined) return;
    player_count = json.player_count;
    player_names = json.player_names;
    player_pks = json.player_pks;

    for (let i = 0; i < player_count; i++) {
        mapingPk_index[player_pks[i]] = i;
    }

    for (let i = 0; i < json.games.length; i++) {
        games.push(new Game(json.games[i][0], json.games[i][1], json.games[i][2], json.games[i][3]));
    }

    Render();
}

function GetGraph() {
    httpGetAsync("/core/json/interactive_graph", ParseJSON);
}

