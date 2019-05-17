//{% comment %}
//
// LoadPVP.js
// p1 - player1 pk
// p2 - player2 pk
//
//{% endcomment %}

let loaded = false;

function ShowPVP(text) {
    const json = JSON.parse(text);
    console.log(json);

    document.getElementById("pvp_stat_games").innerText = json.games;

    document.getElementById("pvp_stat_win1").innerText = json.w1;
    document.getElementById("pvp_stat_win2").innerText = json.w2;

    if (json.games !== undefined && json.games !== 0) {
        document.getElementById("pvp_stat_wr1").innerText = (Number(json.w1) / Number(json.games) * 100).toFixed(2);
        document.getElementById("pvp_stat_wr2").innerText = (Number(json.w2) / Number(json.games) * 100).toFixed(2);
    }
    else {
        document.getElementById("pvp_stat_wr1").innerText = "NA";
        document.getElementById("pvp_stat_wr2").innerText = "NA";
    }

    document.getElementById("pvp_stat_st1").innerText = json.st1;
    document.getElementById("pvp_stat_st2").innerText = json.st2;

    const sets = Number(json.st1) + Number(json.st2);

    if (sets > 0) {
        document.getElementById("pvp_stat_sp1").innerText = (Number(json.st1) / sets * 100).toFixed(2);
        document.getElementById("pvp_stat_sp2").innerText = (Number(json.st2) / sets * 100).toFixed(2);
    }
    else {
        document.getElementById("pvp_stat_sp1").innerText = "NA";
        document.getElementById("pvp_stat_sp2").innerText = "NA";
    }

    document.getElementById("pvp_stat_elo1").innerText = json.elo1;
    document.getElementById("pvp_stat_elo2").innerText = json.elo2;
}


function GetPvpData() {
    httpGetAsync("/core/json/get_pvp/{{p1}}/{{p2}}" , ShowPVP);
}

function LoadPVPData() {
    if (loaded === false) {
        loaded = true;
        GetPvpData();
    }
}
