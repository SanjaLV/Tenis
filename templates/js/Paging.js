// Template Paging.js
// url -> url/?page=X
// page -> current page number
// max_page -> maximal page number
//
// Need to user NODE with page-menu

const base_url = "/core{{url}}";

{% if page %}
const page = {{page}};
{% else %}
const page = 1;
{% endif %}
const max_page = {{max_page}};

function NextPage() {
    MoveToPage(+1);
}
function PrevPage() {
    MoveToPage(-1);
}
function GetMoveToPageParam(evt) {
    MoveToPage(evt.target.myparam);
}

function MoveToPage(offset) {
    let next_page = page + offset;
    if (next_page >= 1) {
        location.replace(base_url + "/?page=" + next_page.toString());
    }
}

function CreateLiWithDiv(is_active, on_click_function, text, param=null) {
    let li = document.createElement("li");
    li.classList.add("page-item");
    if (is_active) {
        li.classList.add("active");
    }
    let div = document.createElement("div");
    div.addEventListener("click", on_click_function, false);
    if (param != null) {
        div.myparam = param;
    }
    div.classList.add("page-link");
    div.innerText = text;
    li.appendChild(div);
    return li;
}

function min(a, b) {
    if (a < b) return a;
    return b;
}

function Render() {
    let main = document.getElementById("page-menu");

    if (page !== 1) {
        main.appendChild(CreateLiWithDiv(false, PrevPage, "Previous"));
    }

    const count = 5;
    let can_before = min(4, page - 1);
    let can_after  = min(4, max_page - page);
    let start = 0;

    console.log(can_before);
    console.log(page);

    if (can_before >= 2 && can_after >= 2) {
        start = -2;
    }
    else if (can_before === 1) {
        start = -1;
    }
    else if (can_before === 0) {
        start = 0;
    }
    else if (can_after === 1) {
        start = -3;
    }
    else if (can_after === 0) {
        start = -4;
    }

    for (let i = 0; i < count; i++) {
        if (start + i + page > max_page) break;
        main.appendChild(CreateLiWithDiv(start + i === 0, GetMoveToPageParam, page + start + i, start + i));
    }

    if (page !== max_page) {
        main.appendChild(CreateLiWithDiv(false, NextPage, "Next"));
    }

}

window.onload = Render;