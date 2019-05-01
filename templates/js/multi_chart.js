//{% comment %}
// Template multi_chart.js
//
// players - list with pair (name, pk)
// graph_data - list with touples (p1, p2, change)
//
// HTML elements we may use
// chart_div - for placing chart inside
// player_selector - for placing player checkbox
//
//{% endcomment %}

/*
<div class="input-group-prepend">
    <div class="input-group-text">
        <input type="checkbox">
    </div>
    <div class="input-group-text">
        Sanja
    </div>
</div>
*/
const player_count = {{players|length}};

let player_names = [
    {% for name,pk in players %}
        "{{name}}",
    {% endfor %}
];

let player_pks = [
    {% for name,pk in players %}
        {{pk}},
    {% endfor %}
];

class Game {
    constructor(p1, p2, change) {
        this.p1 = p1;
        this.p2 = p2;
        this.change = change;
    }
}


let games = [
    {% for p1, p2, change in graph_data %}
        new Game({{p1}},{{p2}},{{change}}),
    {% endfor %}
];

let precalc = [
];

let mapingPk_index = {};


function PreCalc() {
    let t0 = performance.now();

    for (let i = 0; i < player_count; i++)
        mapingPk_index[player_pks[i]] = i;


    let arr = [];
    for (let i = 0; i < player_count; i++) {
        arr.push(800.0);
    }

    precalc.push(arr);

    for (let game = 0; game < games.length; game++) {
        arr = arr.slice();
        const g = games[game];
        arr[mapingPk_index[g.p1]] += g.change;
        arr[mapingPk_index[g.p2]] -= g.change;
        precalc.push(arr);
    }

    let t1 = performance.now();
    console.log("Precalc done in " + (t1 - t0) + " milliseconds.");
}

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
    let divtext = document.createElement("div");
    divtext.classList.add("input-group-text");
    divtext.innerText = player;
    div.appendChild(divtext);
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

function DrawGraph() {
    let data = new google.visualization.DataTable();

    let checked = [];
    for (let i = 0; i < player_count; i++) {
        checked.push(document.getElementById("checkbox_" + player_pks[i].toString()).checked);
    }

    //Create Game number column
    data.addColumn('number', 'game');
    //Create all players column
    for (let i = 0; i < player_count; i++) {
        if (checked[i]) {
            data.addColumn('number', player_names[i]);
        }
    }

    let curMatrix = [];

    for (let i = 0; i < precalc.length; i++) {
        let this_row = [];
        this_row.push(i + 1);
        for (let j = 0; j < player_count; j++) {
            if (checked[j]) {
                this_row.push(precalc[i][j]);
            }
        }
        curMatrix.push(this_row);
    }
    data.addRows(curMatrix);

    const options = {
        //curveType: 'function',
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
    PreCalc();
    let holder = document.getElementById("player_selector");

    for (let i = 0; i < player_count; i++) {
        let div = CreateDivWithCheckBox(player_names[i], "checkbox_" + player_pks[i].toString());
        holder.appendChild(div);
    }

    SetAll();
    DrawGraph();
}

window.onload = Render;

